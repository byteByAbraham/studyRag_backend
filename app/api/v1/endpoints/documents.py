from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document  

from app.models.document_chunk import DocumentChunk               
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService                
from app.services.document_processor import DocumentProcessorService 
from app.services.embedding import EmbeddingService       

from app.services.search_service import SearchService
from app.schemas.document import SemanticSearchQuery
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    room_id: Optional[str] = Query(None, description="ID opcional de la sala donde se comparte el documento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ruta automatizada para cargar un PDF, vincularlo opcionalmente a una sala,
    y ejecutar el pipeline RAG de fragmentos y embeddings de forma aislada.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no soportado. Solo se permiten archivos .pdf"
        )
    
    if room_id:
        from app.models.study_room import StudyRoom
        room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La sala de estudio especificada no existe.")
        
        is_member = any(str(member.id) == str(current_user.id) for member in room.members)
        is_owner = str(room.owner_id) == str(current_user.id)
        if not is_owner and not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para subir archivos a esta sala de estudio porque no eres miembro."
            )

    try:
        document_service = DocumentService(db)
        
        db_document = document_service.upload_document(file=file, user_id=current_user.id)
        
        if room_id:
            db_document.room_id = room_id
            db.commit()
            db.refresh(db_document)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al guardar el documento en el servidor: {str(e)}"
        )

    try:
        processor_service = DocumentProcessorService()
        embedding_service = EmbeddingService()

        chunks = processor_service.process_pdf(db_document.storage_path)
        
        for chunk in chunks:
            texto_fragmento = chunk["content"]
            vector_matematico = embedding_service.generate_embedding(texto_fragmento)
            
            nuevo_chunk_db = DocumentChunk(
                content=texto_fragmento,
                page=chunk["page"],          
                document_id=db_document.id,
                embedding=vector_matematico         
            )
            db.add(nuevo_chunk_db)
        
        db.commit()

        print(f"\n[ÉXITO RAG] Documento {db_document.filename} integrado con éxito.")
        print(f"[ÉXITO RAG] Se guardaron {len(chunks)} vectores en Postgres de forma nativa.\n")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"El archivo se guardó correctamente, pero falló el pipeline de IA: {str(e)}"
        )
    
    return db_document


@router.post("/search", response_model=list)
def test_semantic_search(
    query_data: SemanticSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Endpoint protegido (Búsqueda Semántica).
    Permite acceso si eres dueño, administrador o si perteneces a la sala dueña del documento.
    """

    db_document = db.query(Document).filter(Document.id == query_data.document_id).first()
    
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El documento solicitado no existe.")
    
    has_access = current_user.is_admin or str(db_document.user_id) == str(current_user.id)
    
    if not has_access and db_document.room_id:
        from app.models.study_room import StudyRoom
        room = db.query(StudyRoom).filter(StudyRoom.id == db_document.room_id).first()
        if room:
            is_member = any(str(member.id) == str(current_user.id) for member in room.members)
            is_owner = str(room.owner_id) == str(current_user.id)
            if is_member or is_owner:
                has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este documento ni su contexto RAG."
        )

    try:
        search_service = SearchService(db)
        relevant_chunks = search_service.search_context_for_question(
            document_id=query_data.document_id,
            question=query_data.question,
            limit=3 
        )
        return relevant_chunks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el pipeline de búsqueda: {str(e)}")
    

@router.post("/query")
def ask_question_to_document(
    query_data: SemanticSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint definitivo del Pipeline RAG con streaming.
    Verifica seguridad individual y colectiva antes de iniciar streaming con la IA.
    """

    db_document = db.query(Document).filter(Document.id == query_data.document_id).first()

    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El documento solicitado no existe.")    
    has_access = current_user.is_admin or str(db_document.user_id) == str(current_user.id)
    
    if not has_access and db_document.room_id:
        from app.models.study_room import StudyRoom
        room = db.query(StudyRoom).filter(StudyRoom.id == db_document.room_id).first()
        if room:
            is_member = any(str(member.id) == str(current_user.id) for member in room.members)
            is_owner = str(room.owner_id) == str(current_user.id)
            if is_member or is_owner:
                has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para realizar consultas sobre este documento."
        )

    try:
        chat_service = ChatService(db)
        stream_generator = chat_service.answer_question_stream(
            document_id=query_data.document_id,
            question=query_data.question
        )
        return StreamingResponse(stream_generator, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en streaming RAG: {str(e)}")