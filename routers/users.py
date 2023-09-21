from fastapi import FastAPI, Depends,HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from passlib.context import CryptContext





router= APIRouter()

DATABASE_URL = "mysql://root:@localhost/fast_api"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class models(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String)
    email = Column(String)
    password = Column(String)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@router.get("/user")
def read_all_models( db: Session = Depends(get_db)):
    user_models = db.query(models).all()
    return user_models