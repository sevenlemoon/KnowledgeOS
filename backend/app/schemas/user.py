from datetime import datetime

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    department: str | None
    email: str | None
    phone: str | None
    total_points: int
    total_contribution: float
    knowledge_count: int
    approved_knowledge_count: int
    recent_points_count: int
    create_time: datetime
