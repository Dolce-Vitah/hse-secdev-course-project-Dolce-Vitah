from typing import List

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from src.adapters.database import get_session
from src.app.security import get_current_user
from src.domain.models import User, Wish
from src.domain.schemas import WishCreate, WishRead, WishUpdate
from src.shared.errors import AuthorizationError, NotFoundError

router = APIRouter(prefix="/wishes", tags=["wishes"])


@router.post("/", response_model=WishRead)
def create_wish(
    wish_in: WishCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_wish = Wish(
        title=wish_in.title,
        description=wish_in.notes,
        price_estimate=wish_in.price_estimate,
        link=str(wish_in.link) if wish_in.link is not None else None,
        notes=wish_in.notes,
        owner_id=user.id,
    )

    session.add(db_wish)
    session.commit()
    session.refresh(db_wish)
    return db_wish


@router.get("/", response_model=List[WishRead])
def list_wishes(
    price: float | None = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    query = select(Wish).where(Wish.owner_id == user.id)
    if price is not None:
        query = query.where(Wish.price_estimate < price)
    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


@router.get("/{wish_id}", response_model=WishRead)
def get_wish(
    wish_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError("Wish not found")
    if wish.owner_id != user.id and user.role != "admin":
        raise AuthorizationError("You don't have access to the wish")
    return wish


@router.patch("/{wish_id}", response_model=WishRead)
def update_wish(
    wish_id: int,
    wish_in: WishUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError("Wish not found")
    if wish.owner_id != user.id and user.role != "admin":
        raise AuthorizationError("You cannot update the wish")

    update_data = wish_in.dict(exclude_unset=True)
    if "link" in update_data and update_data["link"] is not None:
        update_data["link"] = str(update_data["link"])

    for field, value in update_data.items():
        setattr(wish, field, value)
    session.add(wish)
    session.commit()
    session.refresh(wish)
    return wish


@router.delete("/{wish_id}")
def delete_wish(
    wish_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError("Wish not found")
    if wish.owner_id != user.id and user.role != "admin":
        raise AuthorizationError("You cannot delete the wish")

    session.delete(wish)
    session.commit()
    return {"message": "Wish deleted successfully"}
