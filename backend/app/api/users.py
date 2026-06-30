from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import success
from app.db.session import get_db
from app.models import Knowledge, PointRecord, User
from app.schemas.user import UserProfileResponse

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    knowledge_count = (
        db.scalar(select(func.count()).where(Knowledge.author_id == current_user.id))
        or 0
    )
    approved_count = (
        db.scalar(
            select(func.count()).where(
                Knowledge.author_id == current_user.id,
                Knowledge.status == "approved",
            )
        )
        or 0
    )
    recent_points_count = (
        db.scalar(select(func.count()).where(PointRecord.user_id == current_user.id))
        or 0
    )
    return success(
        UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            role=current_user.role,
            department=current_user.department,
            email=current_user.email,
            phone=current_user.phone,
            total_points=current_user.total_points,
            total_contribution=float(current_user.total_contribution or 0),
            knowledge_count=knowledge_count,
            approved_knowledge_count=approved_count,
            recent_points_count=recent_points_count,
            create_time=current_user.create_time,
        ).model_dump()
    )
