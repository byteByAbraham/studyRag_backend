

from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """
    Clase base para todos los modelos de la BDs. Que da la generacion automatica del nombre de la tabla.
    y tipado estricto compatible con SQLAlchemy 2.0.
    """

    id: Any

    @declared_attr
    def __tablename__(cls) -> str:
        
        return cls.__name__.lower()