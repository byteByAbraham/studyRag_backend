
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.config import settings

from app.api.deps import get_current_user
from app.models.user import User
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel

router = APIRouter()

class GoogleTokenRequest(BaseModel):
    id_token: str

    
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)

def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Verifica que el correo no esté duplicado y devuelve los datos públicos del usuario creado.
    """

    db_user = UserRepository.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este correo electrónico ya se encuentra registrado."
        )
    
    new_user = UserRepository.create(db, user_in=user_in)
    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)

def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión en el sistema. 
    Verifica las credenciales y devuelve un token JWT válido si son correctas.
    """
    user = UserRepository.get_by_email(db, email=user_in.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico o la contraseña son incorrectos."
        )
    
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico o la contraseña son incorrectos."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ha sido desactivado."
        )
    
    access_token = create_access_token(subject=user.id)
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/google", response_model=Token, status_code=status.HTTP_200_OK)

def google_login(token_data: GoogleTokenRequest, db: Session = Depends(get_db)):
    """
    Inicia sesión o registra automáticamente a un usuario utilizando un token de Google válido.
    Devuelve un token JWT propio del sistema.
    """
    try:
        id_info = id_token.verify_oauth2_token(
            token_data.id_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        email = id_info.get("email")
        full_name = id_info.get("name", "")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de Google no contiene un correo electrónico válido."
            )
            
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de Google es inválido o ha expirado."
        )
    
    user = UserRepository.get_by_email(db, email=email)
    
    if not user:
        user = UserRepository.create_oauth_user(db, email=email, full_name=full_name)
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario se encuentra inactivo."
        )
        
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)

def get_authenticated_user(current_user: User = Depends(get_current_user)):
    """
    Retorna los datos del usuario autenticado actual a traves del token JWT.
    Requiere un token JWT válido en la cabecera de autorización.
    """
    return current_user