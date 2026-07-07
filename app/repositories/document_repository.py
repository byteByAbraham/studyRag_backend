
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: DocumentCreate) -> Document:
        """
        Inserta un nuevo registro de documento en la base de datos.
        """

        db_obj = Document(
            filename=obj_in.filename,
            storage_path=obj_in.storage_path,
            user_id=obj_in.user_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def get_by_user(self, user_id: str) -> list[Document]:
        """
        Obtiene todos los documentos pertenecientes a un usuario.
        """

        return self.db.query(Document).filter(Document.user_id == user_id).all()