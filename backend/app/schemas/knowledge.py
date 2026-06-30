from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    summary: str = Field(min_length=5, max_length=500)
    content: str = Field(min_length=10)
    category: str = Field(default="General", max_length=50)
    tags: str | None = None


class KnowledgeAuditRequest(BaseModel):
    knowledge_id: int
    status: Literal["approved", "rejected"]
    quality_score: float = Field(default=0, ge=0, le=100)
    remark: str | None = None


class KnowledgeInteractRequest(BaseModel):
    knowledge_id: int
    action: Literal["view", "download", "like", "adopt"]


class KnowledgeCommentCreateRequest(BaseModel):
    knowledge_id: int
    content: str = Field(min_length=1, max_length=500)


class KnowledgeCommentResponse(BaseModel):
    id: int
    user_name: str
    content: str
    create_time: datetime


class KnowledgeItemResponse(BaseModel):
    id: int
    title: str
    summary: str
    category: str
    tags: str | None
    author_id: int
    author_name: str
    status: str
    view_count: int
    download_count: int
    comment_count: int
    like_count: int
    adopt_count: int
    quality_score: float
    contribution_score: float
    create_time: datetime


class KnowledgeDetailResponse(KnowledgeItemResponse):
    content: str
    audit_remark: str | None
    comments: list[KnowledgeCommentResponse]
