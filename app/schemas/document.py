
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    storage_path: str
    user_id: UUID


class DocumentResponse(DocumentBase):
    id: str  
    created_at: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)