
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from app.models.study_room import StudyRoom, study_room_members
from app.models.user import User
from app.schemas.study_room import StudyRoomCreate

class StudyRoomRepository:
    
    @staticmethod
    def create_room(db: Session, room_in: StudyRoomCreate, owner_id: UUID) -> StudyRoom:
        """Crea una sala de estudio y añade automáticamente al creador como miembro"""
        db_room = StudyRoom(
            name=room_in.name,
            description=room_in.description,
            owner_id=owner_id
        )
        db.add(db_room)
        db.flush()  
        
        owner_user = db.query(User).filter(User.id == owner_id).first()
        if owner_user:
            db_room.members.append(owner_user)
            
        db.commit()
        db.refresh(db_room)
        return db_room

    @staticmethod
    def get_room_by_id(db: Session, room_id: str) -> Optional[StudyRoom]:
        """Busca una sala de estudio específica por su ID"""
        return db.query(StudyRoom).filter(StudyRoom.id == room_id).first()

    @staticmethod
    def get_user_rooms(db: Session, user_id: UUID) -> List[StudyRoom]:
        """Obtiene todas las salas a las que pertenece un estudiante"""
        return db.query(StudyRoom).join(StudyRoom.members).filter(User.id == user_id).all()

    @staticmethod
    def add_member_to_room(db: Session, room: StudyRoom, user_to_add: User) -> StudyRoom:
        """Une a un nuevo compañero de equipo a la sala de estudio"""
        if user_to_add not in room.members:
            room.members.append(user_to_add)
            db.commit()
            db.refresh(room)
        return room