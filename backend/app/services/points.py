from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import Knowledge, PointRecord, SystemConfig, User

DEFAULT_CONFIGS = {
    "upload_weight": ("0.30", "上传得分权重"),
    "quality_weight": ("0.35", "质量得分权重"),
    "influence_weight": ("0.25", "影响力得分权重"),
    "collaboration_weight": ("0.10", "协作得分权重"),
    "innovation_ratio": ("1.00", "贡献度映射积分系数"),
    "upload_pass_points": ("10", "知识审核通过基础积分"),
    "download_points": ("2", "下载奖励积分"),
    "like_points": ("2", "点赞奖励积分"),
    "adopt_points": ("20", "采纳奖励积分"),
    "comment_points": ("3", "评论奖励积分"),
    "view_milestone_points": ("1", "每10次浏览奖励积分"),
    "excellent_quality_bonus": ("5", "高质量知识额外奖励"),
}


def ensure_default_configs(db: Session) -> None:
    for key, (value, description) in DEFAULT_CONFIGS.items():
        config = db.scalar(select(SystemConfig).where(SystemConfig.config_key == key))
        if not config:
            db.add(
                SystemConfig(
                    config_key=key, config_value=value, description=description
                )
            )
    db.commit()


def ensure_init_admin(db: Session) -> None:
    admin = db.scalar(select(User).where(User.username == settings.init_admin_username))
    if admin:
        return
    db.add(
        User(
            username=settings.init_admin_username,
            password=hash_password(settings.init_admin_password),
            real_name="系统管理员",
            role="admin",
            department="平台管理",
            email="admin@example.com",
        )
    )
    db.commit()


def get_config_map(db: Session) -> dict[str, Decimal]:
    rows = db.scalars(select(SystemConfig)).all()
    return {row.config_key: Decimal(row.config_value) for row in rows}


def award_points(
    db: Session,
    user: User,
    points_type: str,
    change_value: int,
    knowledge_id: int | None = None,
    contribution_value: float = 0,
    remark: str | None = None,
) -> PointRecord:
    before_points = user.total_points
    user.total_points = before_points + change_value
    record = PointRecord(
        user_id=user.id,
        knowledge_id=knowledge_id,
        points_type=points_type,
        change_value=change_value,
        before_points=before_points,
        after_points=user.total_points,
        contribution_value=contribution_value,
        remark=remark,
    )
    db.add(record)
    db.flush()
    return record


def recompute_knowledge_contribution(db: Session, knowledge: Knowledge) -> float:
    config = get_config_map(db)
    upload_score = Decimal("10") if knowledge.status == "approved" else Decimal("0")
    quality_score = Decimal(str(knowledge.quality_score or 0))
    influence_score = (
        Decimal(str(knowledge.adopt_count or 0)) * Decimal("20")
        + Decimal(str(knowledge.download_count or 0)) * Decimal("2")
        + Decimal(str((knowledge.view_count or 0) // 10))
        + Decimal(str(knowledge.like_count or 0)) * Decimal("2")
    )
    collaboration_score = Decimal(str(knowledge.comment_count or 0)) * Decimal("3")
    contribution = (
        config["upload_weight"] * upload_score
        + config["quality_weight"] * quality_score
        + config["influence_weight"] * influence_score
        + config["collaboration_weight"] * collaboration_score
    )
    knowledge.contribution_score = contribution.quantize(Decimal("0.01"))
    return float(knowledge.contribution_score)


def refresh_user_contribution(db: Session, user_id: int) -> None:
    total = db.scalar(
        select(func.coalesce(func.sum(Knowledge.contribution_score), 0)).where(
            Knowledge.author_id == user_id,
            Knowledge.status == "approved",
        )
    )
    user = db.get(User, user_id)
    if user:
        user.total_contribution = total
        db.flush()
