import imghdr
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlmodel import Session, select

from src.adapters.database import get_session
from src.app.security import get_current_user
from src.domain.models import User, Wish
from src.domain.schemas import WishCreate, WishRead, WishUpdate
from src.shared.errors import AuthorizationError, NotFoundError, problem

router = APIRouter(prefix="/wishes", tags=["wishes"])


UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_MIME = {"image/png", "image/jpeg"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


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


@router.post("/upload")
async def upload_wish_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_MIME:
        return problem(
            status=415,
            title="Unsupported Media Type",
            detail=f"Invalid MIME type: {file.content_type}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return problem(
            status=413,
            title="Payload Too Large",
            detail="File exceeds 2MB limit",
        )

    image_type = imghdr.what(None, content)
    detected_mime = f"image/{image_type}" if image_type else None

    if detected_mime not in ALLOWED_MIME:
        return problem(
            status=415,
            title="Invalid File Content",
            detail=f"File content type ({detected_mime}) is not allowed",
        )

    filename = f"{uuid.uuid4()}.{'png' if 'png' in detected_mime else 'jpg'}"
    safe_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(safe_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return problem(
            status=500,
            title="File Save Error",
            detail=f"Could not save file: {e}",
        )

    return {
        "filename": filename,
        "mime": detected_mime,
        "size": len(content),
        "owner_id": user.id,
    }
