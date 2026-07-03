
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["Autenticación"])

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
    
    # 2. Crear el usuario usando el repositorio
    new_user = UserRepository.create(db, user_in=user_in)
    return new_user