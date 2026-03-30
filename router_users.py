from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

from auth import create_access_token
import dal_users


router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)


class UserUpdate(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)


class LoginRequest(BaseModel):
    user_name: str
    password: str

###### GET action ######
@router.get("/users")
def get_users():
    return dal_users.get_all_users()

###### GET-BY-ID action ######
@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = dal_users.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

###### POST action ######
@router.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_user = dal_users.insert_user(
        user_name=user.user_name,
        email=user.email,
        password=user.password
    )

    if new_user is None:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return new_user

###### PUT action ######
@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    updated_user = dal_users.update_user(
        user_id=user_id,
        user_name=user.user_name,
        email=user.email,
        password=user.password
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user == "duplicate":
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return updated_user

###### DELETE action ######
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    deleted_user = dal_users.delete_user(user_id)

    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User deleted successfully",
        "user": deleted_user
    }

###### POST action ######
@router.post("/auth/login")
def login(login_data: LoginRequest):
    is_valid = dal_users.login_user(
        user_name=login_data.user_name,
        password=login_data.password
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(login_data.user_name)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.delete("/users/tables/recreate")
def recreate_users_table():
    dal_users.recreate_table_users()
    return {"message": "Users table dropped and recreated successfully"}