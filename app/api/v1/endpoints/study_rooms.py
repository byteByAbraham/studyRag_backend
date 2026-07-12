
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.study_room import StudyRoomCreate, StudyRoomResponse, AddMemberRequest
from app.repositories.study_room_repository import StudyRoomRepository

router = APIRouter()

@router.post("/", response_model=StudyRoomResponse, status_code=status.HTTP_201_CREATED)
def create_study_room(room_in: StudyRoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Crea un nuevo espacio o grupo colaborativo de estudio"""
    return StudyRoomRepository.create_room(db=db, room_in=room_in, owner_id=current_user.id)

@router.get("/", response_model=List[StudyRoomResponse])
def list_my_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Muestra todas las salas donde participa el alumno actual"""
    return StudyRoomRepository.get_user_rooms(db=db, user_id=current_user.id)

@router.post("/{room_id}/members", response_model=StudyRoomResponse)
def invite_member(room_id: str, member_data: AddMemberRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Invita a un compañero a formar parte de tu sala usando su ID de usuario"""
    room = StudyRoomRepository.get_room_by_id(db, room_id=room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="La sala de estudio no existe")
        
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes autorización para administrar esta sala")
        
    user_to_invite = db.query(User).filter(User.id == member_data.user_id).first()
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="El alumno que intentas invitar no fue encontrado")
        
    return StudyRoomRepository.add_member_to_room(db=db, room=room, user_to_add=user_to_invite)