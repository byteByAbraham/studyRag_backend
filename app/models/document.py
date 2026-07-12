
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from datetime import datetime
import uuid

from app.db.base_class import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)    
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(String(36), ForeignKey("study_rooms.id", ondelete="CASCADE"), nullable=True)
    user = relationship("User", back_populates="documents")
    room = relationship("StudyRoom", backref="documents")

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
