from sqlalchemy.orm import Session

from app.models import Knowledge, User
from app.schemas.knowledge import KnowledgeItemResponse


def build_knowledge_item(db: Session, knowledge: Knowledge) -> KnowledgeItemResponse:
    author = db.get(User, knowledge.author_id)
    return KnowledgeItemResponse(
        id=knowledge.id,
        title=knowledge.title,
        summary=knowledge.summary,
        category=knowledge.category,
        tags=knowledge.tags,
        author_id=knowledge.author_id,
        author_name=author.real_name if author else "未知用户",
        status=knowledge.status,
        view_count=knowledge.view_count,
        download_count=knowledge.download_count,
        comment_count=knowledge.comment_count,
        like_count=knowledge.like_count,
        adopt_count=knowledge.adopt_count,
        quality_score=float(knowledge.quality_score or 0),
        contribution_score=float(knowledge.contribution_score or 0),
        create_time=knowledge.create_time,
    )
