from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import model
from database import get_db
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import or_, desc, asc

router = APIRouter(
    prefix="/items",
    tags=["items"]
)





# Create Function

class ItemCreate(BaseModel):
    title: str
    description: str

@router.post("/create")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = model.Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item




# List Function
@router.get('/')
def list_items(
    skip: int = 0,
    limit: int = 2,
    search: Optional[str] = None,
    title: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "desc",
    db: Session = Depends(get_db)
    ):
    query = db.query(model.Item)

    if search:
        query = query.filter(
            or_(
                model.Item.title.ilike(f"%{search}%"),
                model.Item.description.ilike(f"%{search}%")
            )
        )

    if title:
        query = query.filter(model.Item.title == title)

    if hasattr(model.Item, sort_by):
        column = getattr(model.Item, sort_by)
        if order == "desc":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    else:
        query = query.order_by(asc(model.Item.created_at))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {
        "total_count": total,
        "items": items,
        "limit": limit,
        "skip": skip
    }


class ItemUpdate(BaseModel):
    title : Optional[str] = None
    description : Optional[str] = None

# Update Function
@router.patch('/update/{item_id}')
def update_item(item_id : str, item_data: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(model.Item).filter(model.Item.id == item_id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

# Delete Function
@router.delete('/delete/{item_id}')
def delete_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(model.Item).filter(model.Item.id == item_id).first()

    if db_item:
        db.delete(db_item)
        db.commit()
        return {"message": "Deleted Successfully"}
    raise HTTPException(status_code=404, detail="Item not found")
