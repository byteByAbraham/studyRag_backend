
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.embedding import EmbeddingService
from app.repositories.document_chunk_repository import DocumentChunkRepository

class SearchService:

    def __init__(self, db: Session):
        """
        Inicializa el servicio inyectando la sesión de base de datos
        y los componentes necesarios.
        """
        self.db = db
        self.embedding_service = EmbeddingService()
        self.chunk_repository = DocumentChunkRepository(db)

    def search_context_for_question(self, document_id: str, question: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda de contexto relevante para una pregunta específica dentro de un documento.
        1. Convierte la pregunta del alumno en un vector numérico.
        2. Busca los fragmentos más relevantes en Postgres filtrados por documento.
        3. Estructura y devuelve el contenido limpio.
        """
        if not question.strip():
            raise ValueError("La pregunta proporcionada no puede estar vacía.")


        query_embedding = self.embedding_service.generate_embedding(question)

        raw_results = self.chunk_repository.search_similar_chunks(
            document_id=document_id,
            query_embedding=query_embedding,
            limit=limit
        )

        formatted_context = []
        for chunk, distance in raw_results:
            formatted_context.append({
                "chunk_id": chunk.id,
                "content": chunk.content,
                "page": chunk.page,
                "distance": float(distance)  
            })

        return formatted_context