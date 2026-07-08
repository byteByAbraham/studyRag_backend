from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ruta automatizada para cargar un PDF, segmentarlo en fragmentos (chunks),
    generar sus vectores (embeddings) con Gemini y guardarlos en la base de datos vectorial.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no soportado. Solo se permiten archivos .pdf"
        )
    
    try:

        document_service = DocumentService(db)
        db_document = document_service.upload_document(file=file, user_id=str(current_user.id))  
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
    Endpoint de prueba para la Fase 2 (Búsqueda Semántica).
    Recibe una pregunta y el ID de un PDF, y retorna los fragmentos más relevantes de la base de datos.
    """
    try:
        search_service = SearchService(db)
        
        relevant_chunks = search_service.search_context_for_question(
            document_id=query_data.document_id,
            question=query_data.question,
            limit=3 
        )
        
        return relevant_chunks
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el pipeline de búsqueda semántica: {str(e)}"
        )
    

@router.post("/query", response_model=str)
def ask_question_to_document(
    query_data: SemanticSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint definitivo del Pipeline RAG.
    Recibe el ID de un PDF y una pregunta, busca los fragmentos relevantes
    y le pide a Gemini que redacte una respuesta inteligente basada en el texto.
    """
    try:
        chat_service = ChatService(db)
        
        answer = chat_service.answer_question_from_document(
            document_id=query_data.document_id,
            question=query_data.question
        )
        
        return answer
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en la generación de respuesta de la IA: {str(e)}"
        )
    
    