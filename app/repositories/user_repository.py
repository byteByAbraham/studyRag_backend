
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserRepository:

    """
    Esta clase esta encargada de interactuar con la base de datos para realizar todas las operaciones relacionadas con los usuarios.
    """


    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """
        Se busca un usuario en la base de datos utilizando su correo electrónico.
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """
        Se crea un nuevo registro de usuario en la base de datos. Se aplica el hash automatico a la contraseña antes de guardarla.
        """
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_admin=False,
            is_active=True
        )
        

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user