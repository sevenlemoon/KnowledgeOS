import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.external import router as external_router
from app.api.growth import router as growth_router
from app.api.knowledge import router as knowledge_router
from app.api.points import router as points_router
from app.api.users import router as users_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base
from app.services.points import ensure_default_configs, ensure_init_admin

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("正在初始化数据库...")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        ensure_default_configs(db)
        ensure_init_admin(db)
    logger.info("数据库初始化完成，应用启动")
    yield
    logger.info("应用关闭")


app = FastAPI(
    title="KnowledgeOS - AI知识成长与能力运营平台",
    description="面向高校与企业的 AI 知识成长与能力运营平台，提供知识管理、成长体系、AI教练、技能树、勋章系统等功能。",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置 - 开发环境允许前端地址
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("数据库错误: %s %s -> %s", request.method, request.url.path, exc)
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "数据完整性错误，请检查输入", "data": None},
        )
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("未处理异常: %s %s -> %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


@app.get("/")
def root():
    return {"code": 200, "message": f"{settings.app_name} API is running", "data": None}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(knowledge_router, prefix=settings.api_prefix)
app.include_router(points_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(growth_router, prefix=settings.api_prefix)
app.include_router(external_router, prefix=settings.api_prefix)
