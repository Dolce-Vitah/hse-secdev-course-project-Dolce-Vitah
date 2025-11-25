import imghdr
import os
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import Numeric, cast
from sqlmodel import Session, select

from src.wishlist_api.adapters.database import get_session
from src.wishlist_api.app.security import get_current_user
from src.wishlist_api.domain.models import User, Wish
from src.wishlist_api.domain.schemas import WishCreate, WishRead, WishUpdate
from src.wishlist_api.shared.errors import NotFoundError, problem

router = APIRouter(prefix="/wishes", tags=["wishes"])


UPLOAD_DIR = Path("uploads").resolve()
MAX_FILE_SIZE = 2 * 1024 * 1024
ALLOWED_MIME = {"image/png", "image/jpeg"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def as_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(value)


@router.post("/", response_model=WishRead)
def create_wish(
    wish_in: WishCreate,
    session: Session = Depends(get_session),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Wish:
    db_wish = Wish(
        title=wish_in.title,
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
    price: Decimal | None = Query(None),  # noqa: B008
    limit: int = Query(50, ge=1, le=100),  # noqa: B008
    offset: int = Query(0, ge=0),  # noqa: B008
    session: Session = Depends(get_session),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Sequence[Wish]:
    query = select(Wish).where(Wish.owner_id == user.id)
    if price is not None:
        query = query.where(cast(Wish.price_estimate, Numeric) <= price)
    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


@router.get("/{wish_id}", response_model=WishRead)
def get_wish(
    wish_id: int,
    session: Session = Depends(get_session),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Wish:
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError()
    if wish.owner_id != user.id and user.role != "admin":
        raise NotFoundError()
    return wish


@router.patch("/{wish_id}", response_model=WishRead)
def update_wish(
    wish_id: int,
    wish_in: WishUpdate,
    session: Session = Depends(get_session),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Wish:
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError()
    if wish.owner_id != user.id and user.role != "admin":
        raise NotFoundError()

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
    session: Session = Depends(get_session),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Dict[str, str]:
    wish = session.get(Wish, wish_id)
    if not wish:
        raise NotFoundError()
    if wish.owner_id != user.id and user.role != "admin":
        raise NotFoundError()

    session.delete(wish)
    session.commit()
    return {"message": "Wish deleted successfully"}


@router.post("/upload", response_model=None)
async def upload_wish_file(
    file: UploadFile = File(...),  # noqa: B008
    user: User = Depends(get_current_user),  # noqa: B008
) -> Union[Dict[str, Optional[Union[str, int]]], Response]:

    if file.content_type not in ALLOWED_MIME:
        return problem(
            status=415,
            title="Unsupported Media Type",
            detail="File type is not supported.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return problem(
            status=413,
            title="Payload Too Large",
            detail="File exceeds allowed limit",
        )
    image_type = imghdr.what(None, content)
    detected_mime = f"image/{image_type}" if image_type else None

    if detected_mime not in ALLOWED_MIME:
        return problem(
            status=415,
            title="Invalid File Content",
            detail="File content does not match allowed formats",
        )

    filename = f"{uuid.uuid4()}.{'png' if 'png' in detected_mime else 'jpg'}"
    safe_path = (UPLOAD_DIR / filename).resolve()

    if not str(safe_path).startswith(str(UPLOAD_DIR)):
        return problem(
            status=400,
            title="Invalid File Path",
            detail="Invalid file destination",
        )

    if UPLOAD_DIR.is_symlink():
        return problem(
            status=500,
            title="Storage Configuration Error",
            detail="Upload directory misconfigured.",
        )

    try:
        fd = os.open(safe_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(content)
    except FileExistsError:
        return problem(
            status=409,
            title="File Conflict",
            detail="File already exists.",
        )
    except Exception:
        return problem(
            status=500,
            title="File Save Error",
            detail="Could not save file due to internal error.",
        )

    return {
        "filename": filename,
        "mime": detected_mime,
        "size": len(content),
        "owner_id": int(user.id) if user.id is not None else None,
    }
