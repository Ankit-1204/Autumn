from sqlalchemy.orm import Session
from .import user_models, user_schema
from .auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from settings import settings

def create_user(db: Session, user: user_schema.UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = user_models.User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(user_models.User).filter(user_models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_token(user_id: int):
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={"sub": str(user_id)}, expires_delta=expires)
