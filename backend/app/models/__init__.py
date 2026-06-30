from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="member", index=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    total_contribution: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    login_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")


class Knowledge(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="General", index=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    adopt_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    contribution_score: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    audit_remark: Mapped[str | None] = mapped_column(String(500), nullable=True)


class KnowledgeComment(Base, SoftDeleteMixin):
    __tablename__ = "knowledge_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_comment.id"), nullable=True
    )
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class UserInteraction(Base):
    """用户互动记录，确保点赞/采纳的幂等性。"""
    __tablename__ = "user_interaction"
    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", "action", name="uq_user_knowledge_action"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id"), nullable=False, index=True
    )
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # like/adopt
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PointRecord(Base):
    __tablename__ = "points_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id"), nullable=False, index=True
    )
    knowledge_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_base.id"), nullable=True, index=True
    )
    points_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    change_value: Mapped[int] = mapped_column(Integer, nullable=False)
    before_points: Mapped[int] = mapped_column(Integer, nullable=False)
    after_points: Mapped[int] = mapped_column(Integer, nullable=False)
    contribution_value: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    config_value: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class OperationLog(Base):
    """操作日志，记录关键操作用于审计。"""
    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operation: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )


class AuditHistory(Base):
    """审核历史记录。"""
    __tablename__ = "audit_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id"), nullable=False, index=True
    )
    auditor_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    quality_score: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ==================== KnowledgeOS 成长体系 ====================


class DailyCheckIn(Base):
    """每日签到"""
    __tablename__ = "daily_checkin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    checkin_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=1)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Badge(Base):
    """勋章定义"""
    __tablename__ = "badge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="Trophy")
    category: Mapped[str] = mapped_column(String(30), default="growth")
    condition_type: Mapped[str] = mapped_column(String(30), nullable=False)
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False)
    points_reward: Mapped[int] = mapped_column(Integer, default=0)
    rarity: Mapped[str] = mapped_column(String(20), default="common")


class UserBadge(Base):
    """用户勋章"""
    __tablename__ = "user_badge"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badge.id"), nullable=False, index=True)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SkillCategory(Base):
    """技能分类"""
    __tablename__ = "skill_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), default="Collection")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class SkillNode(Base):
    """技能树节点"""
    __tablename__ = "skill_node"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("skill_category.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("skill_node.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    required_points: Mapped[int] = mapped_column(Integer, default=10)
    icon: Mapped[str] = mapped_column(String(50), default="Aim")


class UserSkill(Base):
    """用户技能进度"""
    __tablename__ = "user_skill"
    __table_args__ = (UniqueConstraint("user_id", "skill_node_id", name="uq_user_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    skill_node_id: Mapped[int] = mapped_column(ForeignKey("skill_node.id"), nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    mastered: Mapped[bool] = mapped_column(Boolean, default=False)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mastered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LearningGoal(Base):
    """每日学习目标"""
    __tablename__ = "learning_goal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    goal_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    target_reads: Mapped[int] = mapped_column(Integer, default=3)
    target_publish: Mapped[int] = mapped_column(Integer, default=1)
    actual_reads: Mapped[int] = mapped_column(Integer, default=0)
    actual_publish: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)


class KnowledgeHealthScore(Base):
    """知识健康度评分"""
    __tablename__ = "knowledge_health_score"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id"), unique=True, nullable=False, index=True
    )
    completeness: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    readability: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    structure: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    freshness: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    engagement: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    ai_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GrowthRecord(Base):
    """成长值变更记录"""
    __tablename__ = "growth_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    change_value: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
