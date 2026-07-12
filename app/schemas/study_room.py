
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class StudyRoomBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Equipo de Desarrollo Backend"])
    description: Optional[str] = Field(None, max_length=255, examples=["Sala para el proyecto final de cuatrimestre"])

class StudyRoomCreate(StudyRoomBase):
    pass

class RoomMemberUser(BaseModel):
    id: UUID
    email: str

    class Config:
        from_attributes = True

class StudyRoomResponse(StudyRoomBase):
    id: str
    owner_id: UUID
    created_at: datetime
    members: List[RoomMemberUser] = []

    class Config:
        from_attributes = True

class AddMemberRequest(BaseModel):
    user_id: UUID