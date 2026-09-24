from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .. core.security import verify_access_token
from sqlalchemy.orm import Session
from .. database import get_db
from ..models.user import User

deps_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(deps_scheme), 
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(token, credentials_exception)

    user = db.query(User).filter(User.id == token_data.id).first()
    if not user:
        raise credentials_exception

    return user