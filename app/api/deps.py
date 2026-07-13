
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = APIKeyHeader(
    name="Authorization",
    auto_error=False
)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependencia para validar el token JWT y retornar el usuario autenticado actual.
    Si el token es inválido o el usuario no existe, lanza una excepción 401 Unauthorized.
    """

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un token de acceso.",
        )

    try:

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron validar las credenciales (Token inválido).",
            )
        
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de acceso ha expirado o es inválido.",
        )
    
    user = UserRepository.get_by_id(db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado."
        )
        
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El usuario está inactivo."
        )
        
    return user