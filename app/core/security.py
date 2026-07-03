

from passlib.context import CryptContext

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