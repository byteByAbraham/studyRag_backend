
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk

class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_similar_chunks(
        self, 
        document_id: str, 
        query_embedding: List[float], 
        limit: int = 4
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Busca los fragmentos de texto más similares pertenecientes a un documento específico
        utilizando la distancia del coseno de pgvector.
        Retorna una lista de tuplas (Objeto Chunk, Distancia matemática).
        """
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        
        results = self.db.query(DocumentChunk, distance.label("distance"))\
            .filter(DocumentChunk.document_id == document_id)\
            .order_by(distance)\
            .limit(limit)\
            .all()
            
        return results