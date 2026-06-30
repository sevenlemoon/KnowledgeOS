from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import success
from app.db.session import get_db
from app.models import Knowledge, PointRecord, User, KnowledgeComment, UserInteraction, UserBadge, GrowthRecord, DailyCheckIn, UserSkill, LearningGoal
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


@router.get("/list")
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取用户列表"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    users = db.scalars(select(User).order_by(User.id)).all()
    items = []
    for u in users:
        k_count = db.scalar(select(func.count()).where(Knowledge.author_id == u.id)) or 0
        items.append({
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "role": u.role,
            "department": u.department,
            "email": u.email,
            "total_points": u.total_points,
            "knowledge_count": k_count,
            "status": u.status,
            "create_time": u.create_time.strftime("%Y-%m-%d %H:%M") if u.create_time else "",
        })
    return success({"items": items, "total": len(items)})


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员删除用户"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除用户")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")

    # 级联清理关联数据
    db.query(KnowledgeComment).filter(KnowledgeComment.author_id == user_id).delete()
    db.query(UserInteraction).filter(UserInteraction.user_id == user_id).delete()
    db.query(UserBadge).filter(UserBadge.user_id == user_id).delete()
    db.query(GrowthRecord).filter(GrowthRecord.user_id == user_id).delete()
    db.query(DailyCheckIn).filter(DailyCheckIn.user_id == user_id).delete()
    db.query(UserSkill).filter(UserSkill.user_id == user_id).delete()
    db.query(LearningGoal).filter(LearningGoal.user_id == user_id).delete()
    db.query(PointRecord).filter(PointRecord.user_id == user_id).delete()
    # 删除用户的知识（级联删除知识的评论和互动已在 knowledge delete 中处理）
    db.query(Knowledge).filter(Knowledge.author_id == user_id).delete()
    db.delete(user)
    db.commit()
    return success(None, "删除成功")
