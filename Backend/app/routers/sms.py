from fastapi import APIRouter, status, Form, Depends
from sqlalchemy.orm import Session
import logging

from ..models.user import User
from ..core.utils import normalize_phone_number
from ..core.sms_parser import parse_report
from ..database import get_db

sms_router = APIRouter(
    prefix = "/sms",
    tags = ["SMS"]
)

logger = logging.getLogger(__name__)

@sms_router.post("/incoming", status_code=status.HTTP_200_OK)
def receive_sms(
    from_: str = Form(..., alias="from"),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        sender = normalize_phone_number(from_)
        cleaned_text = parse_report(text)
    except ValueError:
        logger.warning("Rejected SMS: invalid phone number: %s", from_)
        return {"status": "ignored"}

    user = db.query(User).filter(User.phone_number == sender).first()

    if not user:
        user = User(phone_number=sender, role="citizen")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created new user %s", sender)

    logger.info("SMS received from %s", sender)
    return {"status": "received", "sender": sender, "text": cleaned_text}