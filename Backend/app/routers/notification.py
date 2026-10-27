from fastapi import APIRouter, status, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from ..schemas.common import APIResponse, Meta
from ..schemas.notification import NotificationData
from ..core.deps import get_current_user
from ..models.user import User
from ..models.notification import Notification
from ..database import get_db

notification_router = APIRouter(
    prefix = "/notifications",
    tags = ["Notifications"]
)

@notification_router.get(
    "",
    response_model=APIResponse[List[NotificationData]],
    status_code=status.HTTP_200_OK,
)
def get_notifications(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    query = query.filter(Notification.user_id == current_user.id)
    query = query.order_by(Notification.created_at.desc())

    total = query.count()
    notifications = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = (total + limit - 1) // limit

    meta = Meta(
        page=page, limit=limit, total=total, total_pages=total_pages,
        has_next_page=page < total_pages, has_previous_page=page > 1,
    )

    return APIResponse(success=True, message="Notifications retrieved successfully", data=notifications, meta=meta)
