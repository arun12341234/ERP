"""Item CRUD endpoints - sample resource."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.item import Item
from app.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


def apply_tenant_filter(query, user: User):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and hasattr(user, "tenant_id"):
        query = query.filter(Item.tenant_id == user.tenant_id)
    return query


@router.get("", response_model=List[ItemSchema])
def list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all items (filtered by tenant if enabled)."""
    query = db.query(Item)
    query = apply_tenant_filter(query, current_user)
    items = query.offset(skip).limit(limit).all()
    return items


@router.post("", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new item."""
    item_data = item_in.model_dump()
    item_data["owner_id"] = current_user.id

    # Add tenant_id if multi-tenancy is enabled
    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        item_data["tenant_id"] = current_user.tenant_id

    db_item = Item(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemSchema)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get item by ID."""
    query = db.query(Item).filter(Item.id == item_id)
    query = apply_tenant_filter(query, current_user)
    item = query.first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/{item_id}", response_model=ItemSchema)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an item."""
    query = db.query(Item).filter(Item.id == item_id)
    query = apply_tenant_filter(query, current_user)
    item = query.first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Only owner or admin can update
    if item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an item."""
    query = db.query(Item).filter(Item.id == item_id)
    query = apply_tenant_filter(query, current_user)
    item = query.first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Only owner or admin can delete
    if item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(item)
    db.commit()
    return None
