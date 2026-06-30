import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.utils import build_knowledge_item
from app.core.response import success
from app.db.session import get_db
from app.models import AuditHistory, Knowledge, SystemConfig, User
from app.services.points import (
    award_points,
    recompute_knowledge_contribution,
    refresh_user_contribution,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["管理"])


@router.get("/knowledge/pending")
def pending_knowledge(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    items = db.scalars(
        select(Knowledge)
        .where(Knowledge.status == "pending")
        .order_by(Knowledge.create_time.desc())
    ).all()
    return success([build_knowledge_item(db, item).model_dump() for item in items])


@router.post("/knowledge/audit")
def audit_knowledge(
    payload: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    knowledge_id = payload.get("knowledge_id")
    status = payload.get("status")
    quality_score = payload.get("quality_score", 0)
    remark = payload.get("remark")

    knowledge = db.get(Knowledge, knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")
    knowledge.status = status
    knowledge.quality_score = quality_score if status == "approved" else 0
    knowledge.audit_remark = remark
    author = db.get(User, knowledge.author_id)
    if status == "approved" and author:
        award_points(db, author, "upload_pass_reward", 10, knowledge.id, remark="知识审核通过")
        if quality_score >= 90:
            award_points(
                db,
                author,
                "excellent_quality_bonus",
                5,
                knowledge.id,
                remark="高质量知识奖励",
            )
    if author:
        recompute_knowledge_contribution(db, knowledge)
        refresh_user_contribution(db, author.id)
    # 记录审核历史
    db.add(AuditHistory(
        knowledge_id=knowledge_id,
        auditor_id=current_user.id,
        status=status,
        quality_score=quality_score if status == "approved" else 0,
        remark=remark,
    ))
    db.commit()
    logger.info("管理员 %s 审核知识 #%d -> %s", current_user.username, knowledge_id, status)
    return success(None, "审核完成")


@router.get("/points/config")
def get_points_config(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(SystemConfig).order_by(SystemConfig.id.asc())).all()
    return success(
        [
            {
                "id": row.id,
                "config_key": row.config_key,
                "config_value": row.config_value,
                "description": row.description,
            }
            for row in rows
        ]
    )


@router.post("/points/config")
def update_points_config(
    payload: dict[str, str],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    for key, value in payload.items():
        row = db.scalar(select(SystemConfig).where(SystemConfig.config_key == key))
        if row:
            Decimal(str(value))
            row.config_value = str(value)
    db.commit()
    knowledges = db.scalars(select(Knowledge).where(Knowledge.status == "approved")).all()
    users = db.scalars(select(User)).all()
    for knowledge in knowledges:
        recompute_knowledge_contribution(db, knowledge)
    for user in users:
        refresh_user_contribution(db, user.id)
    db.commit()
    logger.info("管理员 %s 更新积分参数", current_user.username)
    return success(None, "积分参数已更新")


@router.get("/audit/history")
def get_audit_history(
    knowledge_id: int | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    stmt = select(AuditHistory).order_by(AuditHistory.create_time.desc())
    if knowledge_id:
        stmt = stmt.where(AuditHistory.knowledge_id == knowledge_id)
    rows = db.scalars(stmt.limit(50)).all()
    result = []
    for row in rows:
        auditor = db.get(User, row.auditor_id)
        knowledge = db.get(Knowledge, row.knowledge_id)
        result.append({
            "id": row.id,
            "knowledge_id": row.knowledge_id,
            "knowledge_title": knowledge.title if knowledge else "已删除",
            "auditor_name": auditor.real_name if auditor else "未知",
            "status": row.status,
            "quality_score": float(row.quality_score or 0),
            "remark": row.remark,
            "create_time": row.create_time.isoformat() if row.create_time else None,
        })
    return success(result)
