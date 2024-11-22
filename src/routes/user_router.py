import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User

router = APIRouter()
logging.basicConfig(level=logging.INFO)


@router.post("/users/")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email, hashed_password="hashed_dummy")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user