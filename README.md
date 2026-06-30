<div align="center">

# 🧠 KnowledgeOS

### AI 知识成长与能力运营平台

<p>
  <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?style=flat-square&logo=vue.js&logoColor=white" alt="Vue3">
  <img src="https://img.shields.io/badge/Vite-5.4-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Element Plus-2.9-409EFF?style=flat-square&logo=element&logoColor=white" alt="Element Plus">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License">
</p>

<p>
  <strong>不只是存储知识，而是帮助用户实现「知识 → 能力 → 成长 → 企业价值」的完整闭环。</strong>
</p>

<br>

[English](#english) | [中文](#-项目介绍)

</div>

---

## 📖 项目介绍

**KnowledgeOS** 是一个面向高校、企业团队和个人的现代化 AI 知识成长平台，集知识管理、成长体系、AI 教练、技能树、勋章系统、外部知识源聚合于一体。

与传统知识库不同，KnowledgeOS 围绕 **「成长」** 而非「存储」来设计产品：

- 🎯 **每日签到** → 养成学习习惯
- 📈 **成长等级** → 看到自己的进步
- 🏅 **勋章系统** → 获得成就激励
- 🌳 **技能树** → 规划学习路径
- 🤖 **AI 教练** → 获得个性化指导
- 🌐 **外部知识源** → 连接全球开发者社区

---

## ✨ 功能特点

<table>
<tr>
<td width="50%">

### 📚 知识管理
- 知识发布、审核、搜索、分类、标签
- 评论互动、点赞/采纳（Toggle 切换）
- 知识健康度 AI 体检（5 维雷达图）
- 质量分徽章
- 管理员删除知识

### 🌐 外部知识源
- **Dev.to** — 全球开发者文章
- **GitHub** — 热门开源项目
- **Bilibili** — 科技区热门视频
- 封面图、标签、跳转链接、播放量

### 🤖 AI 成长教练
- 今日学习目标（阅读/发布进度）
- 个性化成长建议
- 距离下一等级进度提示

</td>
<td width="50%">

### 🏆 积分激励
- 自动化积分奖励（发布、点赞、评论、采纳）
- 积分排行榜
- 管理员可配置积分规则

### 🌳 技能树
- 5 大技能分类（前端/后端/数据库/DevOps/设计）
- 27 个技能节点，3 级深度
- 用户技能进度追踪

### 👥 团队管理
- 用户管理（管理员删除用户）
- 知识审核流程
- 审核历史记录
- 操作日志审计

### 🔐 安全认证
- JWT 令牌认证
- RBAC 权限控制（管理员/成员）
- 密码加密存储（pbkdf2_sha256）

</td>
</tr>
</table>

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│  Vue 3 + Vite 5 + Pinia + Element Plus + ECharts    │
│  Aurora 渐变 + Glassmorphism + Design Token         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────┐
│                    Backend                           │
│  FastAPI + SQLAlchemy 2.0 + Pydantic v2 + httpx     │
│  JWT + passlib + 统一响应格式 + 全局异常处理          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    Database                          │
│  MySQL 8.0 (18 张表, 连接池, 软删除)                │
└─────────────────────────────────────────────────────┘
```

| 层级 | 技术栈 |
|------|--------|
| **前端框架** | Vue 3 Composition API + Vite 5 |
| **状态管理** | Pinia |
| **路由** | Vue Router 4 |
| **UI 组件** | Element Plus 2.9 |
| **图表** | ECharts 5 |
| **HTTP 客户端** | Axios |
| **后端框架** | FastAPI (Python 3.13) |
| **ORM** | SQLAlchemy 2.0 (Mapped) |
| **数据校验** | Pydantic v2 |
| **认证** | JWT (HS256) + passlib (pbkdf2_sha256) |
| **数据库** | MySQL 8.0 |
| **外部 API** | httpx (Dev.to / GitHub / Bilibili) |
| **部署** | Docker + Docker Compose + Nginx |

---

## 📂 项目结构

```
KnowledgeOS/
├── 📁 backend/                          # 后端服务
│   ├── 📁 app/
│   │   ├── 📁 api/                     # API 路由层
│   │   │   ├── auth.py                 # 认证（登录/注册）
│   │   │   ├── knowledge.py            # 知识 CRUD + 互动
│   │   │   ├── growth.py               # 成长体系（签到/勋章/技能树/AI教练）
│   │   │   ├── external.py             # 外部知识源（Dev.to/GitHub/Bilibili）
│   │   │   ├── admin.py                # 管理后台（审核/积分配置）
│   │   │   ├── points.py               # 积分系统
│   │   │   ├── users.py                # 用户管理（列表/删除）
│   │   │   └── deps.py                 # 依赖注入
│   │   ├── 📁 core/                    # 核心配置
│   │   │   ├── config.py               # 环境变量配置
│   │   │   ├── security.py             # JWT + 密码加密
│   │   │   └── response.py             # 统一响应格式
│   │   ├── 📁 db/                      # 数据库
│   │   │   └── session.py              # 连接池 + Session 管理
│   │   ├── 📁 models/                  # ORM 模型（18 张表）
│   │   ├── 📁 schemas/                 # Pydantic 数据校验
│   │   └── main.py                     # 应用入口
│   └── 📁 scripts/                     # 工具脚本
│       ├── seed_data.py                # 种子数据（用户+知识）
│       └── seed_growth.py              # 成长体系种子（勋章+技能树）
│
├── 📁 frontend/                         # 前端应用
│   ├── 📁 src/
│   │   ├── 📁 api/                     # API 调用模块
│   │   ├── 📁 layout/                  # 布局组件
│   │   ├── 📁 router/                  # 路由配置
│   │   ├── 📁 stores/                  # Pinia 状态管理
│   │   ├── 📁 views/                   # 页面组件
│   │   │   ├── DashboardView.vue       # 成长工作台
│   │   │   ├── KnowledgeListView.vue   # 知识库（内部+外部）
│   │   │   ├── PublishView.vue         # 知识发布
│   │   │   ├── ProfileView.vue         # 个人中心
│   │   │   ├── UserManageView.vue      # 用户管理
│   │   │   └── LoginView.vue           # 登录页
│   │   ├── style.css                   # 全局样式 + Design Token
│   │   └── App.vue                     # Aurora 背景
│   └── 📁 public/                      # 静态资源
│
├── docker-compose.yml                   # Docker 编排
├── Dockerfile.backend                   # 后端镜像
├── nginx.conf                           # Nginx 反向代理
├── .gitignore                           # Git 忽略规则
└── README.md
```

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| MySQL | 8.0+ |

### 1️⃣ 克隆项目

```bash
git clone https://github.com/sevenlemoon/KnowledgeOS.git
cd KnowledgeOS
```

### 2️⃣ 后端启动

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql pydantic \
  pydantic-settings python-jose[cryptography] passlib[bcrypt] \
  python-multipart httpx

# 创建数据库
mysql -u root -p -e "CREATE DATABASE bysj CHARACTER SET utf8mb4;"

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 修改数据库密码

# 启动后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3️⃣ 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 4️⃣ 访问系统

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 5️⃣ 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123456 |
| 成员 | zhangsan | 123456 |
| 成员 | lisi | 123456 |

### 🐳 Docker 部署（可选）

```bash
docker-compose up -d
# 访问 http://localhost
```

---

## 📡 API 接口

<details>
<summary>点击展开完整 API 列表</summary>

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |

### 知识管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/knowledge/list` | 知识列表（分页、筛选） |
| GET | `/api/knowledge/detail/{id}` | 知识详情 |
| POST | `/api/knowledge/add` | 发布知识 |
| POST | `/api/knowledge/comment` | 发表评论 |
| POST | `/api/knowledge/interact` | 互动（点赞/采纳/下载） |
| DELETE | `/api/knowledge/{id}` | 管理员删除知识 |

### 成长体系
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/growth/checkin` | 每日签到 |
| GET | `/api/growth/checkin/status` | 签到状态 |
| GET | `/api/growth/badges` | 勋章列表 |
| GET | `/api/growth/skill-tree` | 技能树 |
| GET | `/api/growth/ai-coach` | AI 成长教练 |
| GET | `/api/growth/knowledge-health/{id}` | 知识健康度 |
| GET | `/api/growth/stats` | 成长统计 |

### 外部知识源
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/external/articles` | 外部文章（Dev.to/GitHub/Bilibili） |
| GET | `/api/external/tags` | 热门标签 |
| GET | `/api/external/image-proxy` | 图片代理 |

### 用户管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/user/profile` | 个人资料 |
| GET | `/api/user/list` | 管理员获取用户列表 |
| DELETE | `/api/user/{id}` | 管理员删除用户 |

### 管理后台
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/knowledge/pending` | 待审核知识 |
| POST | `/api/admin/knowledge/audit` | 审核知识 |
| GET | `/api/admin/points/config` | 积分配置 |
| POST | `/api/admin/points/config` | 更新积分配置 |

### 积分系统
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/points/ranking` | 积分排行榜 |
| GET | `/api/points/records` | 积分记录 |

</details>

---

## 📸 项目截图

> 📷 Screenshots coming soon...

| 页面 | 预览 |
|------|------|
| 登录页 | 左右分栏 + 磨砂玻璃登录框 |
| 成长工作台 | 等级横幅 + 签到 + AI教练 + 趋势图 |
| 知识库 | 内部知识 + 外部知识源（Dev.to/GitHub/Bilibili） |
| 技能树 | 5大分类 + 27个节点 + 进度追踪 |
| 用户管理 | 用户列表 + 删除功能 |

---

## 📌 项目亮点

<table>
<tr>
<td align="center">🧠<br><strong>AI 知识成长</strong><br>不是知识库，是成长平台</td>
<td align="center">🌐<br><strong>外部知识源</strong><br>Dev.to + GitHub + Bilibili</td>
<td align="center">🏆<br><strong>游戏化激励</strong><br>签到/等级/勋章/技能树</td>
<td align="center">🎨<br><strong>Aurora 设计</strong><br>Glassmorphism + Design Token</td>
</tr>
<tr>
<td align="center">🔐<br><strong>企业级安全</strong><br>JWT + RBAC + 审计日志</td>
<td align="center">📊<br><strong>数据驱动</strong><br>ECharts 可视化分析</td>
<td align="center">🐳<br><strong>容器化部署</strong><br>Docker + Nginx 一键启动</td>
<td align="center">📱<br><strong>响应式设计</strong><br>桌面端 + 移动端适配</td>
</tr>
</table>

---

## 📈 后续规划

- [ ] AI 知识推荐（基于用户行为）
- [ ] 向量检索（Embedding + 语义搜索）
- [ ] RAG 问答助手
- [ ] 企业培训中心（学习路线 + 考试）
- [ ] 知识成长地图（技能树可视化）
- [ ] 学习周报 / 月报 / 年度报告
- [ ] 多语言支持（i18n）
- [ ] Kubernetes 部署
- [ ] MCP 支持 + AI Agent

---

## 🤝 贡献

欢迎提交 [Issue](https://github.com/sevenlemoon/KnowledgeOS/issues) 和 [Pull Request](https://github.com/sevenlemoon/KnowledgeOS/pulls)！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！**

Made with ❤️ by [sevenlemoon](https://github.com/sevenlemoon)

</div>
