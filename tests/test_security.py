from datetime import timedelta

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from src.app.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from src.domain.models import User
from src.shared.errors import AuthenticationError, NotFoundError


def test_password_hash_and_verify():
    password = "secret123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


# ---------- Token creation ----------


def test_create_access_token_contains_sub_and_exp():
    data = {"sub": "1"}
    token = create_access_token(data)
    from jose import jwt

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "1"
    assert "exp" in decoded


def test_create_access_token_with_custom_expiration():
    from jose import jwt

    delta = timedelta(minutes=5)
    token = create_access_token({"sub": "42"}, expires_delta=delta)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "42"
    assert "exp" in decoded


def test_get_current_user_valid_token(mocker):
    mock_session = mocker.Mock()
    mock_user = User(id=1, username="john")
    mock_session.get.return_value = mock_user

    mocker.patch("src.app.security.jwt.decode", return_value={"sub": "1"})
    mocker.patch("src.app.security.is_token_revoked", return_value=False)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="validtoken"
    )

    user = get_current_user(credentials=credentials, session=mock_session)
    assert user.username == "john"


def test_get_current_user_invalid_token(mocker):
    mock_session = mocker.Mock()
    mocker.patch("src.app.security.jwt.decode", side_effect=JWTError())

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalidtoken"
    )

    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(credentials=credentials, session=mock_session)

    err = exc_info.value
    assert err.status_code == 401
    assert err.detail["code"] == "UNAUTHORIZED"
    assert err.detail["message"] == "Invalid or malformed token"


def test_get_current_user_revoked_token(mocker):
    mock_session = mocker.Mock()
    mocker.patch("src.app.security.jwt.decode", return_value={"sub": "1"})
    mocker.patch("src.app.security.is_token_revoked", return_value=True)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="revokedtoken"
    )

    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(credentials=credentials, session=mock_session)

    err = exc_info.value
    assert err.status_code == 401
    assert err.detail["code"] == "UNAUTHORIZED"
    assert err.detail["message"] == "Token has been revoked"


def test_get_current_user_user_not_found(mocker):
    mock_session = mocker.Mock()
    mock_session.get.return_value = None

    mocker.patch("src.app.security.jwt.decode", return_value={"sub": "999"})
    mocker.patch("src.app.security.is_token_revoked", return_value=False)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="validtoken"
    )

    with pytest.raises(NotFoundError) as exc_info:
        get_current_user(credentials=credentials, session=mock_session)

    err = exc_info.value
    assert err.status_code == 404
    assert err.detail["code"] == "NOT_FOUND"
    assert err.detail["message"] == "User not found"


def test_get_current_user_missing_sub_field(mocker):
    mock_session = mocker.Mock()
    mocker.patch("src.app.security.jwt.decode", return_value={})
    mocker.patch("src.app.security.is_token_revoked", return_value=False)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalidtoken"
    )

    with pytest.raises(AuthenticationError) as exc_info:
        get_current_user(credentials=credentials, session=mock_session)

    err = exc_info.value
    assert err.status_code == 401
    assert err.detail["code"] == "UNAUTHORIZED"
    assert err.detail["message"] == "Invalid token: no subject field"
