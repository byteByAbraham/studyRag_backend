
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.services.document import DocumentService
from app.schemas.document import DocumentResponse

from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)

def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ruta para subir un archivo PDF o documento. 
    Extrae el usuario directamente del token JWT de forma segura.
    """


    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no soportado. Solo se permiten archivos .pdf"
        )

    try:
        
        document_service = DocumentService(db)
        db_document = document_service.upload_document(file=file, user_id=current_user.id)    
        
        return db_document
        

    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al guardar el documento: {str(e)}"
        )
    