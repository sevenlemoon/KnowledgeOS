# KnowledgeOS

> 面向高校与企业的 AI 知识成长与能力运营平台

基于 Vue 3 + FastAPI 的全栈知识管理系统，不只是存储知识，而是帮助用户实现「知识 → 能力 → 成长 → 企业价值」的完整闭环。

## 核心特性

### 成长工作台
- 成长等级系统（Lv.1 ~ Lv.30）+ 等级称号
- 每日签到 + 连续签到奖励
- AI 成长教练（今日目标、学习建议）
- 知识贡献趋势图表

### 知识库
- 内部知识发布、审核、搜索、分类、标签
- 外部知识源接入（Dev.to / Gitee 开源社区）
- 知识健康度 AI 体检（5 维雷达图）
- 质量分徽章

### 积分激励
- 自动化积分奖励（发布、浏览、点赞、评论、采纳）
- 积分排行榜
- 勋章系统（14 个勋章，4 个稀有度）

### 技能树
- 5 大技能分类（前端/后端/数据库/DevOps/设计）
- 27 个技能节点，3 级深度
- 用户技能进度追踪

### 团队协作
- 评论互动、点赞/采纳（支持 toggle 切换）
- 知识影响力分析
- 部门知识分布

### 企业管理
- 知识审核流程
- 积分规则配置
- 审核历史记录
- 操作日志审计

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Pinia + ECharts + Vite 5 |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic v2 + httpx |
| 数据库 | MySQL 8.0 |
| 认证 | JWT (HS256) + passlib (pbkdf2_sha256) |
| 设计 | Aurora 渐变 + Glassmorphism + Design Token |
| 部署 | Docker + Docker Compose + Nginx |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone <repository-url>
cd KnowledgeOS
```

### 2. 后端启动

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart httpx

# 配置数据库
# 编辑 backend/.env 文件

# 启动后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问系统

- **前端**：http://localhost:5173
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

### 5. 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123456 |
| 普通用户 | zhangsan | 123456 |
| 普通用户 | lisi | 123456 |

## Docker 部署

```bash
docker-compose up -d
```

## 项目结构

```
KnowledgeOS/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── knowledge.py   # 知识 CRUD + 互动
│   │   │   ├── growth.py      # 成长体系（签到/勋章/技能树/AI教练）
│   │   │   ├── external.py    # 外部知识源聚合
│   │   │   ├── admin.py       # 管理后台
│   │   │   ├── points.py      # 积分系统
│   │   │   └── users.py       # 用户管理
│   │   ├── core/              # 配置、安全、响应格式
│   │   ├── db/                # 数据库连接池
│   │   ├── models/            # ORM 模型（18 张表）
│   │   ├── schemas/           # Pydantic 数据校验
│   │   └── services/          # 业务逻辑
│   └── scripts/               # 种子数据、迁移脚本
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API 调用模块
│   │   ├── layout/            # 布局组件（Header + Sidebar）
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── views/             # 页面组件
│   │   │   ├── DashboardView  # 成长工作台
│   │   │   ├── KnowledgeList  # 知识库（内部+外部）
│   │   │   ├── PublishView    # 知识发布
│   │   │   ├── ProfileView    # 个人中心
│   │   │   └── LoginView      # 登录页
│   │   ├── style.css          # 全局样式 + Design Token
│   │   └── App.vue            # Aurora 背景
│   └── public/                # 静态资源
├── docker-compose.yml          # Docker 编排
├── nginx.conf                  # Nginx 反向代理
└── README.md
```

## 数据库设计

### 核心表（18 张）

| 表名 | 说明 |
|------|------|
| sys_user | 用户表 |
| knowledge_base | 知识主表 |
| knowledge_comment | 评论表 |
| points_config | 积分规则配置 |
| points_record | 积分记录 |
| user_interaction | 用户互动（幂等） |
| operation_log | 操作日志 |
| audit_history | 审核历史 |
| daily_checkin | 每日签到 |
| badge | 勋章定义 |
| user_badge | 用户勋章 |
| skill_category | 技能分类 |
| skill_node | 技能树节点 |
| user_skill | 用户技能进度 |
| learning_goal | 学习目标 |
| knowledge_health_score | 知识健康度 |
| growth_record | 成长值记录 |

## API 接口

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 知识管理
- `GET /api/knowledge/list` - 知识列表（分页、筛选）
- `GET /api/knowledge/{id}` - 知识详情
- `POST /api/knowledge/publish` - 发布知识
- `POST /api/knowledge/comment` - 发表评论
- `POST /api/knowledge/interact` - 互动操作（点赞/采纳/下载）

### 成长体系
- `POST /api/growth/checkin` - 每日签到
- `GET /api/growth/checkin/status` - 签到状态
- `GET /api/growth/badges` - 勋章列表
- `GET /api/growth/skill-tree` - 技能树
- `GET /api/growth/ai-coach` - AI 成长教练
- `GET /api/growth/knowledge-health/{id}` - 知识健康度
- `GET /api/growth/stats` - 成长统计

### 外部知识源
- `GET /api/external/articles` - 外部文章（Dev.to / Gitee）
- `GET /api/external/tags` - 热门标签

### 管理后台
- `GET /api/admin/knowledge/pending` - 待审核知识
- `POST /api/admin/knowledge/audit` - 审核知识
- `GET /api/admin/points/config` - 积分配置

## 设计理念

### Aurora 设计系统
- 流动渐变背景（4 个极光光斑）
- Glassmorphism 磨砂玻璃卡片
- 统一 Design Token CSS 变量
- 圆角 16px + 轻阴影

### 产品定位
不是传统的知识库，而是帮助用户每天成长的平台：
- 签到 → 养成习惯
- 等级 → 看到进步
- 勋章 → 获得成就
- 技能树 → 规划路径
- AI 教练 → 获得指导

## 许可证

MIT License
