from datetime import datetime

from pydantic import BaseModel


class PointRecordResponse(BaseModel):
    id: int
    points_type: str
    change_value: int
    before_points: int
    after_points: int
    contribution_value: float
    remark: str | None
    knowledge_id: int | None
    create_time: datetime


class RankingItemResponse(BaseModel):
    user_id: int
    real_name: str
    department: str | None
    total_points: int
    total_contribution: float
