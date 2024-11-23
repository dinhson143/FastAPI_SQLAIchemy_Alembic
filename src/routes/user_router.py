import logging
from datetime import timedelta, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError

from src.database import get_db
from src.models.user_models import CreateUserRequest, Token
from src.tables.user import User

router = APIRouter()
logging.basicConfig(level=logging.INFO)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/users/token")

SECRET_KEY = 'khfkdsjhfkjsdhfjkdfhdskfhsdiouoruewr464354c3xz1cdas6d4a'
ALGORITHM = 'HS256'


@router.post("/users/", status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(create_user_request: CreateUserRequest, db: Session = Depends(get_db)):
    create_user_model = User(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model


@router.post("/users/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")
        return {'username': username, 'id': user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Could not validate user.: {e}")


@router.get("/users/", response_model=dict)
async def get_user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}


def authenticate_user(username: str, password: str, db) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, expires_time: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_time
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
