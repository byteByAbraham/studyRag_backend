
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    storage_path: str
    user_id: UUID
    room_id: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: str  
    created_at: datetime
    user_id: UUID
    room_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SemanticSearchQuery(BaseModel):
    document_id: str = Field(..., description="El identificador único del documento PDF")
    question: str = Field(..., description="La pregunta o duda que deseas buscar en el texto")