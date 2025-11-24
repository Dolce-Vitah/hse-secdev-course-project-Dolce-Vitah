from datetime import timedelta
from unittest.mock import Mock

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlmodel import Session

from src.wishlist_api.app.security import (
    ALGORITHM,
    JWT_SECRET_CURRENT,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from src.wishlist_api.domain.models import User
from src.wishlist_api.shared.errors import AuthenticationError, NotFoundError


def test_password_hash_and_verify():
    password = "SecurePass1!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpass", hashed)


def test_create_access_token_contains_sub_and_exp():
    data = {"sub": "1"}
    token = create_access_token(data)
    decoded = jwt.decode(token, JWT_SECRET_CURRENT, algorithms=[ALGORITHM])
    assert decoded["sub"] == "1"
    assert "exp" in decoded


def test_create_access_token_with_custom_expiration():
    delta = timedelta(minutes=5)
    token = create_access_token({"sub": "42"}, expires_delta=delta)
    decoded = jwt.decode(token, JWT_SECRET_CURRENT, algorithms=[ALGORITHM])
    assert decoded["sub"] == "42"
    assert "exp" in decoded


def test_get_current_user_valid_token(mocker):
    mock_session = Mock(spec=Session)
    mock_user = User(id=1, username="john")
    mock_session.get.return_value = mock_user

    token = create_access_token({"sub": str(mock_user.id)})

    mocker.patch("src.app.security.is_token_revoked", return_value=False)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = get_current_user(credentials=credentials, session=mock_session)
    assert user.id == 1
    assert user.username == "john"


def test_get_current_user_revoked_token(mocker):
    mock_session = Mock(spec=Session)
    mock_user = User(id=2, username="alice")
    mock_session.get.return_value = mock_user

    token = create_access_token({"sub": str(mock_user.id)})
    mocker.patch("src.app.security.is_token_revoked", return_value=True)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(credentials=credentials, session=mock_session)
    assert "revoked" in str(exc_info.value)


def test_get_current_user_invalid_token(mocker):
    mock_session = Mock(spec=Session)
    mock_session.get.return_value = None

    mocker.patch("src.app.security.is_token_revoked", return_value=False)
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalidtoken"
    )

    with pytest.raises(AuthenticationError):
        get_current_user(credentials=credentials, session=mock_session)


def test_get_current_user_user_not_found(mocker):
    mock_session = Mock(spec=Session)
    mock_session.get.return_value = None

    token = create_access_token({"sub": "999"})
    mocker.patch("src.app.security.is_token_revoked", return_value=False)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(NotFoundError):
        get_current_user(credentials=credentials, session=mock_session)
