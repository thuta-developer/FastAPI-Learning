from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import model
from database import get_db, SessionLocal
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import or_, desc, asc
from jose import JWTError, jwt
import auth



from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "5fbb6c573fd209c770992a9520642d42f3823b65bdcee4971be4ab2028fdadb0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


db = SessionLocal()

admin = model.User(
    username="admin",
    hashed_password=auth.hash_password("superuser"),
    is_staff=True
)

db.add(admin)
db.commit()
db.close()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    username: str
    password: str
    

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == user_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    hashed_pwd = auth.hash_password(user_data.password)

    new_user = model.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        is_staff=False
    )

    db.add(new_user)
    db.commit()
    return {
        "username": new_user.username,
        "email": new_user.email,
        "message": "User Registered successfully"
    }




@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == user_data.username).first()
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    token = auth.create_access_token(data={"sub": user.username, "is_staff": user.is_staff})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")






def require_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Only staff can access this!")
    return current_user


# Admin ပဲ ဝင်လို့ရမယ့် API
@router.get("/admin-only-data")
def get_admin_data(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Only staff can access this!")
    return {"message": "Hello Admin, here is the secret data"}




@router.post("/create-admin")
def create_admin(user_data: UserRegister, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(model.User).filter(model.User.username == user_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    hashed_pwd = auth.hash_password(user_data.password)

    new_admin = model.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        is_staff=True
    )

    db.add(new_admin)
    db.commit()
    return {
        "username": new_admin.username,
        "email": new_admin.email,
        "message": "Admin Registered successfully"
    }

# User List
@router.get("/users")
def user_list(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_staff"):
        raise HTTPException(status_code=403, detail="Only staff can access this!")
    return db.query(model.User).all()