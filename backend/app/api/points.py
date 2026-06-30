from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import paginate, success
from app.db.session import get_db
from app.models import PointRecord, User
from app.schemas.points import PointRecordResponse, RankingItemResponse

router = APIRouter(prefix="/points", tags=["积分"])


@router.get("/records")
def get_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(func.count()).where(PointRecord.user_id == current_user.id)
    )
    records = db.scalars(
        select(PointRecord)
        .where(PointRecord.user_id == current_user.id)
        .order_by(PointRecord.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    result = [
        PointRecordResponse(
            id=record.id,
            points_type=record.points_type,
            change_value=record.change_value,
            before_points=record.before_points,
            after_points=record.after_points,
            contribution_value=float(record.contribution_value or 0),
            remark=record.remark,
            knowledge_id=record.knowledge_id,
            create_time=record.create_time,
        ).model_dump()
        for record in records
    ]
    return paginate(result, total or 0, page, page_size)


@router.get("/ranking")
def get_ranking(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    del current_user
    total = db.scalar(
        select(func.count()).where(User.status == "active")
    )
    users = db.scalars(
        select(User)
        .where(User.status == "active")
        .order_by(desc(User.total_points), desc(User.total_contribution))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    result = [
        RankingItemResponse(
            user_id=user.id,
            real_name=user.real_name,
            department=user.department,
            total_points=user.total_points,
            total_contribution=float(user.total_contribution or 0),
        ).model_dump()
        for user in users
    ]
    return paginate(result, total or 0, page, page_size)
