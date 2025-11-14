"""Routes for item CRUD operations backed by a SQLite database."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models.models import Item as ItemModel
from app.utils.helpers import get_db

router = APIRouter(prefix="/api/items", tags=["items"])


class ItemBase(BaseModel):
    """Shared fields for item input."""

    text: str


class ItemCreate(ItemBase):
    """Payload for creating an item."""

    pass


class ItemUpdate(ItemBase):
    """Payload for updating an item."""

    pass


class Item(ItemBase):
    """Representation of an item returned by the API."""

    id: int
    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=List[Item])
def list_items(db: Session = Depends(get_db)) -> List[Item]:
    """Return all items stored in the database."""

    items = db.query(ItemModel).all()
    return items


@router.post("/", response_model=Item)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> Item:
    """Create a new item and persist it to the database."""

    db_item = ItemModel(text=payload.text)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    """Retrieve a single item by its identifier."""

    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    """Update an existing item."""

    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.text = payload.text
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete an item from the database."""

    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return {"ok": True}
