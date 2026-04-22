from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
import model, schemas, auth
import auth
from database import get_db
from pydantic import BaseModel, EmailStr
from typing import List
from uuid import UUID


router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"],
    dependencies=[Depends(auth.require_admin)] # ဒီ Router တစ်ခုလုံးကို Admin ပဲ ပေးဝင်မယ်
)



@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
def create_admin(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(model.User).filter(model.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_staff = model.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=auth.hash_password(user_data.password),
        is_staff=True
    )
    db.add(new_staff)
    db.commit()

    return {"message": f"Admin {new_staff.username} created successfully"}




@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    users = db.query(model.User).offset(skip).limit(limit).all()
    return users


@router.delete("/users/{user_id}/delete")
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == str(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"} 
