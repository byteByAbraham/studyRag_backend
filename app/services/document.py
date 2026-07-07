
import os
import uuid
from shutil import copyfileobj
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate
from app.models.document import Document


class DocumentService:


    def __init__(self, db: Session):
        self.db = db
        self.repository = DocumentRepository(db)
        self.upload_dir = os.path.join(os.getcwd(), "storage", "documents")
        
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)


    def upload_document(self, file: UploadFile, user_id: uuid.UUID) -> Document:
        """
        Guarda el archivo en el disco local y registra sus metadatos en la base de datos.
        """
        file_extension = os.path.splitext(file.filename)[1]
        
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)


        with open(file_path, "wb") as buffer:
            copyfileobj(file.file, buffer)

        document_in = DocumentCreate(
            filename=file.filename,
            storage_path=file_path,  
            user_id=user_id
        )


        return self.repository.create(document_in)