from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from .. models.user import User
from .. schemas.user import  UserData, UserPatch
from .. core.deps import get_current_user
from .. database import get_db

users_router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

@users_router.get("/me", 
                  response_model=UserData, 
                  status_code=status.HTTP_200_OK)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@users_router.patch("/me", 
                    response_model=UserData, 
                    status_code=status.HTTP_200_OK)
def update_current_user_info(updated_user: UserPatch,
                             current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if updated_user.full_name is not None:
        current_user.full_name = updated_user.full_name
    if updated_user.phone_number is not None:
        current_user.phone_number = updated_user.phone_number

    db.commit()
    db.refresh(current_user)
    return current_user
