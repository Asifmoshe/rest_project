from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

from auth import create_access_token
import dal_users

"""
API routes for user management and authentication.

This router provides CRUD endpoints for users and a login endpoint that returns
a JWT token for authenticated access to model routes.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

import dal_users
from auth import create_access_token

router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    """
    Request body for creating a new user.
    """

    user_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)


class UserUpdate(BaseModel):
    """
    Request body for updating an existing user.
    """

    user_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)


class LoginRequest(BaseModel):
    """
    Request body for user login.
    """

    user_name: str
    password: str


@router.get("/users")
def get_users():
    """
    Retrieve all users.

    Returns:
        list[dict]: List of all user records.
    """
    return dal_users.get_all_users()


@router.get("/users/{user_id}")
def get_user(user_id: int):
    """
    Retrieve a single user by id.

    Args:
        user_id (int): User id.

    Raises:
        HTTPException: If the user does not exist.

    Returns:
        dict: User record.
    """
    user = dal_users.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", status_code=201)
def create_user(user: UserCreate):
    """
    Create a new user.

    Args:
        user (UserCreate): New user payload.

    Raises:
        HTTPException: If the username or email already exists.

    Returns:
        dict: Created user record.
    """
    new_user = dal_users.insert_user(
        user_name=user.user_name,
        email=user.email,
        password=user.password,
    )

    if new_user is None:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    return new_user


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    """
    Update an existing user.

    Args:
        user_id (int): User id.
        user (UserUpdate): Updated user payload.

    Raises:
        HTTPException: If the user does not exist or if the username/email is duplicated.

    Returns:
        dict: Updated user record.
    """
    updated_user = dal_users.update_user(
        user_id=user_id,
        user_name=user.user_name,
        email=user.email,
        password=user.password,
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user == "duplicate":
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    return updated_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    """
    Delete a user by id.

    Args:
        user_id (int): User id.

    Raises:
        HTTPException: If the user does not exist.

    Returns:
        dict: Confirmation message and deleted user record.
    """
    deleted_user = dal_users.delete_user(user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User deleted successfully",
        "user": deleted_user,
    }


@router.post("/auth/login")
def login(login_data: LoginRequest):
    """
    Authenticate a user and return a JWT token.

    Args:
        login_data (LoginRequest): Login payload with username and password.

    Raises:
        HTTPException: If username or password is invalid.

    Returns:
        dict: JWT access token and token type.
    """
    is_valid = dal_users.login_user(
        user_name=login_data.user_name,
        password=login_data.password,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(login_data.user_name)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.delete("/users/tables/recreate")
def recreate_users_table():
    """
    Drop and recreate the users table.

    Useful for local testing or resetting the database.

    Returns:
        dict: Confirmation message.
    """
    dal_users.recreate_table_users()
    return {"message": "Users table dropped and recreated successfully"}