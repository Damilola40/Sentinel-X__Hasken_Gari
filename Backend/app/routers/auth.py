from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..schemas.user import AppUserIn, UserData, Token
from ..models.user import User
from ..database import get_db
from ..core.security import get_password_hash, verify_password, create_access_token
from ..core.utils import normalize_phone_number

auth_router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)

# Incident POST router - create a new user
@auth_router.post("/register",
             response_model=UserData,
             status_code=status.HTTP_201_CREATED
             )
def register_user(user_data: AppUserIn, db: Session = Depends(get_db)):
    # Check if user with the same email already exists
    existing_user = db.query(User).filter(or_(User.email == user_data.email, User.phone_number == user_data.phone_number)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone number already registered")

    # Normalize the phone number
    user_data.phone_number = normalize_phone_number(user_data.phone_number)

    # Create a new user instance
    new_user = User(
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        email=user_data.email,
        password=get_password_hash(user_data.password),  # Hash the password before storing
        role="citizen"  # Default role for new users
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Incident POST router -login a user
@auth_router.post("/login",
                  response_model=Token, 
                  status_code=status.HTTP_200_OK
                  )
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), 
          db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user_credentials.username).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not verify_password(user_credentials.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Crede")

    # create a token
    # return token
    access_token = create_access_token(data={"user_id": str(existing_user.id)})
    return {"access_token": access_token,  "token_type": "bearer"}
