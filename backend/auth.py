# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import user_crud, user_schema
from db.database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=user_schema.UserRead)
def signup(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.create_user(db, user)
    return db_user

@router.post("/login")
def login(form: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.authenticate_user(db, form.email, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = user_crud.create_user_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
