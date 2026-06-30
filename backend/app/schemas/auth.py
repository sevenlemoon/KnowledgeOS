from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=6, max_length=20)
    real_name: str = Field(min_length=2, max_length=20)
    department: str | None = None
    email: EmailStr | None = None

    @field_validator("department", "email", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    total_points: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser
