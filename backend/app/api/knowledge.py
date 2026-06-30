from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.utils import build_knowledge_item
from app.core.response import paginate, success
from app.db.session import get_db
from app.models import Knowledge, KnowledgeComment, User, UserInteraction
from app.schemas.knowledge import (
    KnowledgeCommentCreateRequest,
    KnowledgeCommentResponse,
    KnowledgeCreateRequest,
    KnowledgeDetailResponse,
    KnowledgeInteractRequest,
    KnowledgeItemResponse,
)
from app.services.points import (
    award_points,
    recompute_knowledge_contribution,
    refresh_user_contribution,
)

router = APIRouter(prefix="/knowledge", tags=["知识"])


@router.post("/add")
def add_knowledge(
    payload: KnowledgeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    knowledge = Knowledge(
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        category=payload.category,
        tags=payload.tags,
        author_id=current_user.id,
        status="pending",
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return success(build_knowledge_item(db, knowledge).model_dump())


@router.get("/list")
def list_knowledge(
    keyword: str | None = Query(default=None),
    mine: bool = Query(default=False),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base_stmt = select(Knowledge)
    if mine:
        base_stmt = base_stmt.where(Knowledge.author_id == current_user.id)
    elif current_user.role != "admin":
        base_stmt = base_stmt.where(Knowledge.status == "approved")
    if status:
        base_stmt = base_stmt.where(Knowledge.status == status)
    if keyword:
        base_stmt = base_stmt.where(
            or_(Knowledge.title.contains(keyword), Knowledge.summary.contains(keyword))
        )

    total = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    items = db.scalars(
        base_stmt.order_by(Knowledge.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    result = [build_knowledge_item(db, item).model_dump() for item in items]
    return paginate(result, total or 0, page, page_size)


@router.get("/detail/{knowledge_id}")
def get_knowledge_detail(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    knowledge = db.get(Knowledge, knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")
    if (
        current_user.role != "admin"
        and knowledge.status != "approved"
        and knowledge.author_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="无权访问该知识")
    item = build_knowledge_item(db, knowledge)
    comments = db.scalars(
        select(KnowledgeComment)
        .where(KnowledgeComment.knowledge_id == knowledge_id)
        .order_by(KnowledgeComment.create_time.desc())
    ).all()
    comment_list = []
    for comment in comments:
        comment_user = db.get(User, comment.user_id)
        comment_list.append(
            KnowledgeCommentResponse(
                id=comment.id,
                user_name=comment_user.real_name if comment_user else "未知用户",
                content=comment.content,
                create_time=comment.create_time,
            ).model_dump()
        )
    # 查询当前用户的互动状态
    user_interactions = db.scalars(
        select(UserInteraction.action).where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.knowledge_id == knowledge_id,
        )
    ).all()

    data = item.model_dump()
    data.update(
        content=knowledge.content,
        audit_remark=knowledge.audit_remark,
        comments=comment_list,
        user_liked = "like" in user_interactions,
        user_adopted = "adopt" in user_interactions,
    )
    return success(data)


@router.post("/comment")
def comment_knowledge(
    payload: KnowledgeCommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    knowledge = db.get(Knowledge, payload.knowledge_id)
    if not knowledge or knowledge.status != "approved":
        raise HTTPException(status_code=404, detail="知识不存在或未通过审核")
    comment = KnowledgeComment(
        knowledge_id=knowledge.id, user_id=current_user.id, content=payload.content
    )
    knowledge.comment_count += 1
    db.add(comment)
    author = db.get(User, knowledge.author_id)
    if author:
        award_points(
            db,
            user=author,
            points_type="comment_reward",
            change_value=3,
            knowledge_id=knowledge.id,
            remark="知识收到评论反馈",
        )
        recompute_knowledge_contribution(db, knowledge)
        refresh_user_contribution(db, author.id)
    db.commit()
    db.refresh(comment)
    return success(
        KnowledgeCommentResponse(
            id=comment.id,
            user_name=current_user.real_name,
            content=comment.content,
            create_time=comment.create_time,
        ).model_dump()
    )


@router.post("/interact")
def interact_knowledge(
    payload: KnowledgeInteractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    knowledge = db.get(Knowledge, payload.knowledge_id)
    if not knowledge or knowledge.status != "approved":
        raise HTTPException(status_code=404, detail="知识不存在或未通过审核")
    author = db.get(User, knowledge.author_id)
    message = "操作成功"

    if payload.action == "view":
        before_bucket = knowledge.view_count // 10
        knowledge.view_count += 1
        after_bucket = knowledge.view_count // 10
        if author and after_bucket > before_bucket:
            award_points(db, author, "view_reward", 1, knowledge.id, remark="知识浏览量达到新的里程碑")
        message = "浏览量已更新"
    elif payload.action == "download":
        knowledge.download_count += 1
        if author:
            award_points(db, author, "download_reward", 2, knowledge.id, remark="知识被下载")
        message = "下载量已更新"
    elif payload.action == "like":
        existing = db.scalar(
            select(UserInteraction).where(
                UserInteraction.user_id == current_user.id,
                UserInteraction.knowledge_id == knowledge.id,
                UserInteraction.action == "like",
            )
        )
        if existing:
            # 取消点赞
            db.delete(existing)
            knowledge.like_count = max(0, knowledge.like_count - 1)
            message = "已取消点赞"
        else:
            knowledge.like_count += 1
            db.add(UserInteraction(user_id=current_user.id, knowledge_id=knowledge.id, action="like"))
            if author:
                award_points(db, author, "like_reward", 2, knowledge.id, remark="知识获得点赞")
            message = "点赞成功"
    elif payload.action == "adopt":
        existing = db.scalar(
            select(UserInteraction).where(
                UserInteraction.user_id == current_user.id,
                UserInteraction.knowledge_id == knowledge.id,
                UserInteraction.action == "adopt",
            )
        )
        if existing:
            # 取消采纳
            db.delete(existing)
            knowledge.adopt_count = max(0, knowledge.adopt_count - 1)
            message = "已取消采纳"
        else:
            knowledge.adopt_count += 1
            db.add(UserInteraction(user_id=current_user.id, knowledge_id=knowledge.id, action="adopt"))
            if author:
                award_points(db, author, "adopt_reward", 20, knowledge.id, remark="知识方案被采纳")
            message = "采纳成功"

    if author:
        recompute_knowledge_contribution(db, knowledge)
        refresh_user_contribution(db, author.id)
    db.commit()
    return success({"operator": current_user.real_name}, message)


@router.delete("/{knowledge_id}")
def delete_knowledge(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员删除知识"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除知识")
    knowledge = db.get(Knowledge, knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    db.query(KnowledgeComment).filter(KnowledgeComment.knowledge_id == knowledge_id).delete()
    db.query(UserInteraction).filter(UserInteraction.knowledge_id == knowledge_id).delete()
    from app.models import PointsRecord, AuditHistory
    db.query(PointsRecord).filter(PointsRecord.knowledge_id == knowledge_id).delete()
    db.query(AuditHistory).filter(AuditHistory.knowledge_id == knowledge_id).delete()
    db.delete(knowledge)
    db.commit()
    return success(None, "删除成功")
