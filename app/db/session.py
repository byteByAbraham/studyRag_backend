

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,
    )

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Devuelve una sesión de la base de datos. Se utiliza como dependencia en las rutas y para prevenir fugas de memoria en el servidor.
    """
    db = session_local()
    try:
        yield db
    finally:
        db.close()