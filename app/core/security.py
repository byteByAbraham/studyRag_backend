
from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:

    """
    Tranformar una contraseña en texto plano utilizando bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    """
    Compara una contraseña en texto plano con lo guardado en la base de datos.
    Si coincide devuelve un True, si no un False.
    """

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:

    """"
    Se genera un token de acceso JWT firmado. 
    El parametro subject normalmente es el ID o correo del usuario.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt