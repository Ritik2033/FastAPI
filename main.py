from fastapi import FastAPI, Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()

# Database connection setup
DATABASE_URL = "mysql://root:@localhost/fast_api"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



class UserModel(BaseModel):
   
    firstname: str
    lastname: str
    email: str
    password: str



class showUserModel(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
   


class authmodel(BaseModel):
    email:str
    password:str


class models( Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String)
    email = Column(String)
    password = Column(String)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




'''@app.get("/user")
def read_all_models( db: Session = Depends(get_db),get_current_user:models=Depends(get_current_user)):
    user_models = db.query(models).all()
    return user_models'''

@app.get("/vue.js")
def function():
    return{
    "data":[
        {
            "id":1,
            "product_line":"Primary Saving",
            "product_referance":"Primary Saving"
        },

        {
            "id":2,
            "product_line":"Salary Saving",
            "product_referance":"Salary Saving"
        },


        {
            "id":3,
            "product_line":"Standard Saving",
            "product_referance":"Standard Saving"
        },


        {
            "id":4,
            "product_line":"Advanced Checking",
            "product_referance":"Advanced Checking"
        },


        {
            "id":5,
            "product_line":"Preferred Checking",
            "product_referance":"Preferred Checking"
        }


       


    ]
}





@app.get("/user/{id}")
def read_by_id_models( id: int, db: Session = Depends(get_db)):
    user_models = db.query(models).filter( models.id ==id).first()
    if not user_models:
        raise HTTPException(status_code=404, detail="User not found")
    return user_models


@app.post("/user", response_model=showUserModel)
def update_users_models(user: UserModel, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password  
    user_models = models(**user_dict)  
    db.add(user_models)
    db.commit()
    db.refresh(user_models)
    return user_models


@app.put("/user/{id}", response_model=UserModel)
def create_users_models(id:int,user:UserModel, db: Session = Depends(get_db)):
    user_models = db.query(models).filter( models.id ==id).first()

    if not user_models:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump().items():
        setattr(user_models, key, value)
    db.commit()
    db.refresh(user_models)
    return user_models


@app.delete("/user/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(models).filter(models.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return "user delete"




##############JWT Token Auth######################

@app.post("/login")
def auth_user(request: authmodel, db: Session = Depends(get_db)):
    db_user = db.query(models).filter(models.email == request.email).first()
    if not db_user or not pwd_context.verify(request.password, db_user.password):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}




'''@app.post("/login")
def auth_user(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models).filter(models.email == request.username).first()
    if not db_user or not pwd_context.verify(request.password, db_user.password):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}'''



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception



def get_current_user(token: str=Depends(oauth2_scheme)):
    Exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token,Exception)




@app.get("/user")
def read_all_models( db: Session = Depends(get_db),get_current_user:models=Depends(get_current_user)):
    user_models = db.query(models).all()
    return user_models



@app.get("/user/{id}")
def read_by_id_models( id: int, db: Session = Depends(get_db), get_current_user:models=Depends(get_current_user)):
    user_models = db.query(models).filter( models.id ==id).first()
    if not user_models:
        raise HTTPException(status_code=404, detail="User not found")
    return user_models




@app.post("/user", response_model=showUserModel)
def update_users_models(user: UserModel, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password  
    user_models = models(**user_dict)  
    db.add(user_models)
    db.commit()
    db.refresh(user_models)
    return user_models


@app.put("/user/{id}", response_model=UserModel)
def create_users_models(id:int,user:UserModel, db: Session = Depends(get_db),get_current_user:models=Depends(get_current_user)):
    user_models = db.query(models).filter( models.id ==id).first()

    if not user_models:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump().items():
        setattr(user_models, key, value)
        
    db.commit()
    db.refresh(user_models)
    return user_models


@app.delete("/user/{id}")
def delete_user(id: int, db: Session = Depends(get_db),get_current_user:models=Depends(get_current_user)):
    db_user = db.query(models).filter(models.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return "user delete"



