"""填充示例数据，让演示时系统看起来真实可用。"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import engine
from app.models import Base, Knowledge, KnowledgeComment, PointRecord, User, SystemConfig
from app.services.points import ensure_default_configs, ensure_init_admin

# 创建表
Base.metadata.create_all(bind=engine)

# 示例用户
USERS = [
    {"username": "admin", "password": "admin123456", "real_name": "系统管理员", "role": "admin", "department": "技术管理部"},
    {"username": "zhangsan", "password": "123456", "real_name": "张三", "role": "member", "department": "研发一部"},
    {"username": "lisi", "password": "123456", "real_name": "李四", "role": "member", "department": "研发一部"},
    {"username": "wangwu", "password": "123456", "real_name": "王五", "role": "member", "department": "研发二部"},
    {"username": "zhaoliu", "password": "123456", "real_name": "赵六", "role": "member", "department": "测试部"},
    {"username": "sunqi", "password": "123456", "real_name": "孙七", "role": "member", "department": "产品部"},
    {"username": "zhouba", "password": "123456", "real_name": "周八", "role": "member", "department": "研发二部"},
    {"username": "wujiu", "password": "123456", "real_name": "吴九", "role": "member", "department": "运维部"},
    {"username": "zhengshi", "password": "123456", "real_name": "郑十", "role": "member", "department": "数据部"},
    {"username": "liuyi", "password": "123456", "real_name": "刘一", "role": "member", "department": "研发一部"},
    {"username": "chener", "password": "123456", "real_name": "陈二", "role": "member", "department": "设计部"},
    {"username": "yangsan", "password": "123456", "real_name": "杨三", "role": "member", "department": "产品部"},
    {"username": "huangsi", "password": "123456", "real_name": "黄四", "role": "member", "department": "测试部"},
]

# 示例知识
KNOWLEDGE_DATA = [
    {
        "title": "Vue 3 Composition API 最佳实践总结",
        "summary": "本文总结了 Vue 3 Composition API 在实际项目中的最佳实践，包括 ref/reactive 的使用场景、computed 与 watch 的区别、组合式函数的封装技巧等。",
        "content": "一、ref vs reactive 的选择\n\n在 Vue 3 中，ref 和 reactive 都可以用来创建响应式数据。推荐的使用方式：\n\n1. 基础类型使用 ref\n2. 对象类型使用 reactive\n3. 需要替换整个对象时使用 ref\n\n二、computed 的正确使用\n\ncomputed 应该用于依赖其他响应式数据的派生状态，避免在 computed 中产生副作用。\n\n三、组合式函数封装\n\n将可复用的逻辑封装为 useXxx 函数，提高代码复用性。例如 usePagination、useRequest 等。\n\n四、生命周期钩子\n\nonMounted 中进行数据获取，onUnmounted 中进行清理操作（如移除事件监听器、取消定时器等）。",
        "category": "开发经验",
        "tags": "Vue3,前端,Composition API",
        "author_idx": 0,
        "status": "approved",
        "quality_score": 92,
        "view_count": 156,
        "like_count": 23,
        "download_count": 8,
        "comment_count": 5,
        "adopt_count": 3,
    },
    {
        "title": "FastAPI + SQLAlchemy 2.0 项目架构设计",
        "summary": "详细介绍如何使用 FastAPI 框架结合 SQLAlchemy 2.0 构建企业级后端服务，包括分层架构、依赖注入、统一响应、异常处理等核心设计。",
        "content": "一、项目分层\n\n采用经典的四层架构：\n- API 路由层：处理 HTTP 请求和响应\n- Schema 层：Pydantic 数据校验\n- Service 层：业务逻辑处理\n- Model 层：ORM 数据库映射\n\n二、依赖注入\n\nFastAPI 的 Depends 机制非常适合做鉴权和数据库 Session 管理。通过 get_current_user 依赖，可以优雅地实现 JWT 鉴权。\n\n三、统一响应格式\n\n所有接口统一返回 {code, message, data} 格式，前端只需一套解析逻辑。\n\n四、异常处理\n\n使用 @app.exception_handler 全局捕获异常，避免堆栈信息泄露给前端。",
        "category": "架构设计",
        "tags": "FastAPI,SQLAlchemy,Python,后端架构",
        "author_idx": 2,
        "status": "approved",
        "quality_score": 95,
        "view_count": 203,
        "like_count": 31,
        "download_count": 15,
        "comment_count": 8,
        "adopt_count": 5,
    },
    {
        "title": "MySQL 索引优化实战指南",
        "summary": "从实际项目出发，讲解 MySQL 索引的创建原则、联合索引的最左匹配原则、覆盖索引的使用场景，以及如何通过 EXPLAIN 分析慢查询。",
        "content": "一、索引创建原则\n\n1. 在 WHERE、ORDER BY、GROUP BY 涉及的列上创建索引\n2. 选择性高的列优先（区分度大的列放前面）\n3. 避免在频繁更新的列上建过多索引\n\n二、联合索引最左匹配\n\n联合索引 (a, b, c) 可以匹配 a、(a,b)、(a,b,c)，但不能跳过直接匹配 b 或 c。\n\n三、覆盖索引\n\n当查询的所有列都在索引中时，可以避免回表查询，大幅提升性能。\n\n四、EXPLAIN 分析\n\n重点关注 type、key、rows、Extra 字段，type 从好到差：system > const > eq_ref > ref > range > index > ALL。",
        "category": "开发经验",
        "tags": "MySQL,索引,性能优化,数据库",
        "author_idx": 3,
        "status": "approved",
        "quality_score": 88,
        "view_count": 178,
        "like_count": 28,
        "download_count": 12,
        "comment_count": 6,
        "adopt_count": 4,
    },
    {
        "title": "Element Plus 企业级 UI 设计规范",
        "summary": "基于 Element Plus 组件库，建立企业后台管理系统的 UI 设计规范，包括 Design Token 定义、组件使用规范、动效设计等。",
        "content": "一、Design Token 体系\n\n通过 CSS 变量统一管理设计规范：\n- 颜色系统：Primary、Success、Danger、Warning、Info\n- 圆角系统：sm(6px)、md(10px)、lg(16px)\n- 阴影系统：sm、md、lg、card、card-hover\n- 间距系统：xs(4px)、sm(8px)、md(16px)、lg(24px)\n\n二、组件规范\n\n- 按钮：统一圆角 10px，hover 上浮 1px + 阴影\n- 卡片：圆角 16px，hover 蓝色光晕\n- 表格：表头背景 #f8fafc，大写字母间距\n- 标签：药丸形状（border-radius: 9999px）\n\n三、动画规范\n\n- 页面切换：fade-slide（淡入+上滑）\n- 列表加载：fadeInUp 渐入 + stagger 延迟\n- 按钮交互：translateY(-1px) + shadow",
        "category": "UI/UX",
        "tags": "Element Plus,UI设计,Design Token,前端",
        "author_idx": 5,
        "status": "approved",
        "quality_score": 90,
        "view_count": 134,
        "like_count": 19,
        "download_count": 6,
        "comment_count": 4,
        "adopt_count": 2,
    },
    {
        "title": "JWT 认证机制原理与安全实践",
        "summary": "深入解析 JWT（JSON Web Token）的工作原理、签名机制、常见安全漏洞及防护措施，以及在前后端分离项目中的最佳实践。",
        "content": "一、JWT 结构\n\nJWT 由三部分组成：Header.Payload.Signature\n- Header：指定签名算法（如 HS256）\n- Payload：包含用户信息和过期时间\n- Signature：对前两部分的签名，防止篡改\n\n二、安全实践\n\n1. Token 不要存 localStorage（XSS 风险），推荐 HttpOnly Cookie\n2. 设置合理的过期时间（建议 2-24 小时）\n3. 使用 refresh_token 机制实现无感刷新\n4. 敏感操作需要二次验证\n\n三、常见攻击\n\n- JWT 伪造：使用弱密钥或 none 算法\n- Token 泄漏：XSS 窃取 localStorage\n- 重放攻击：缺少 Token 过期机制",
        "category": "安全运维",
        "tags": "JWT,安全,认证,Token",
        "author_idx": 0,
        "status": "approved",
        "quality_score": 86,
        "view_count": 145,
        "like_count": 21,
        "download_count": 9,
        "comment_count": 3,
        "adopt_count": 1,
    },
    {
        "title": "ECharts 数据可视化实战：企业仪表盘设计",
        "summary": "使用 ECharts 构建企业级数据可视化仪表盘，包括图表选型、配色方案、响应式适配、动态数据更新等实战技巧。",
        "content": "一、图表选型\n\n- 趋势数据：折线图（Line）\n- 对比数据：柱状图（Bar）\n- 占比数据：饼图（Pie）\n- 分布数据：散点图（Scatter）\n\n二、配色方案\n\n企业后台推荐蓝白灰配色，避免过于鲜艳的颜色。\n\n三、响应式\n\n监听 window.resize 事件，调用 chart.resize() 自适应。\n\n四、动态数据\n\n使用 chart.setOption() 动态更新数据，配合 setInterval 实时刷新。",
        "category": "开发经验",
        "tags": "ECharts,数据可视化,Dashboard,前端",
        "author_idx": 6,
        "status": "approved",
        "quality_score": 84,
        "view_count": 98,
        "like_count": 15,
        "download_count": 4,
        "comment_count": 2,
        "adopt_count": 1,
    },
    {
        "title": "Docker 容器化部署 Python 后端服务",
        "summary": "详细介绍如何使用 Docker 和 Docker Compose 容器化部署 FastAPI 后端服务，包括 Dockerfile 编写、多阶段构建、环境变量管理等。",
        "content": "一、Dockerfile 最佳实践\n\n1. 使用多阶段构建减小镜像体积\n2. 利用缓存层加速构建\n3. 使用非 root 用户运行服务\n\n二、docker-compose 编排\n\n将后端、数据库、Redis、Nginx 统一编排，一键启动。\n\n三、环境变量管理\n\n使用 .env 文件管理敏感配置，不要提交到代码仓库。\n\n四、健康检查\n\n配置 HEALTHCHECK 指令，确保服务可用性。",
        "category": "安全运维",
        "tags": "Docker,部署,容器化,DevOps",
        "author_idx": 0,
        "status": "approved",
        "quality_score": 87,
        "view_count": 112,
        "like_count": 18,
        "download_count": 7,
        "comment_count": 3,
        "adopt_count": 2,
    },
    {
        "title": "Python 异步编程：从 asyncio 到 async/await",
        "summary": "系统讲解 Python 异步编程的核心概念，包括事件循环、协程、任务调度，以及在 Web 开发中的实际应用场景。",
        "content": "一、异步编程模型\n\n异步编程不是多线程，而是单线程内的任务调度。当一个任务等待 I/O 时，切换到其他任务执行。\n\n二、async/await 语法\n\nasync def 定义协程函数，await 等待异步操作完成。\n\n三、实际应用\n\n- 异步 HTTP 请求（aiohttp）\n- 异步数据库操作（asyncpg）\n- 异步文件操作（aiofiles）\n\n四、FastAPI 中的异步\n\nFastAPI 原生支持异步，但要注意同步操作会阻塞事件循环，需要使用 run_in_executor。",
        "category": "开发经验",
        "tags": "Python,异步编程,asyncio,FastAPI",
        "author_idx": 1,
        "status": "approved",
        "quality_score": 82,
        "view_count": 89,
        "like_count": 12,
        "download_count": 3,
        "comment_count": 2,
        "adopt_count": 0,
    },
    {
        "title": "软件测试策略：单元测试、集成测试与 E2E 测试",
        "summary": "全面介绍软件测试的不同层次和策略，包括单元测试（pytest）、集成测试（httpx）和端到端测试（Playwright）的实践方法。",
        "content": "一、测试金字塔\n\n- 底层：单元测试（数量最多，速度最快）\n- 中层：集成测试（验证模块间协作）\n- 顶层：E2E 测试（模拟用户操作）\n\n二、pytest 实战\n\n使用 fixture 管理测试依赖，parametrize 实现参数化测试。\n\n三、FastAPI 测试\n\n使用 TestClient 或 httpx.AsyncClient 进行接口测试。\n\n四、测试覆盖率\n\n使用 coverage.py 统计覆盖率，目标 > 80%。",
        "category": "测试技术",
        "tags": "测试,pytest,单元测试,TDD",
        "author_idx": 4,
        "status": "approved",
        "quality_score": 80,
        "view_count": 76,
        "like_count": 10,
        "download_count": 2,
        "comment_count": 1,
        "adopt_count": 0,
    },
    {
        "title": "Git 工作流与团队协作规范",
        "summary": "介绍企业团队中常用的 Git 工作流（Git Flow、GitHub Flow），以及分支管理、代码审查、提交规范等协作最佳实践。",
        "content": "一、Git Flow\n\n- main：生产环境代码\n- develop：开发主分支\n- feature/*：功能分支\n- release/*：发布分支\n- hotfix/*：紧急修复\n\n二、提交规范\n\n使用 Conventional Commits：\n- feat: 新功能\n- fix: 修复\n- docs: 文档\n- refactor: 重构\n- test: 测试\n\n三、代码审查\n\n- PR 不超过 400 行\n- 至少一人审核\n- CI 通过后合并",
        "category": "项目管理",
        "tags": "Git,团队协作,代码审查,版本管理",
        "author_idx": 2,
        "status": "approved",
        "quality_score": 83,
        "view_count": 95,
        "like_count": 14,
        "download_count": 5,
        "comment_count": 3,
        "adopt_count": 1,
    },
    {
        "title": "需求分析方法论：用户故事与用例图",
        "summary": "介绍如何使用用户故事（User Story）和用例图（Use Case Diagram）进行需求分析，帮助团队准确理解业务需求。",
        "content": "一、用户故事格式\n\n作为<角色>，我希望<功能>，以便<价值>。\n\n示例：作为一名研发人员，我希望可以搜索知识库中的技术文档，以便快速找到解决方案。\n\n二、用例图\n\n用例图展示系统的功能和参与者之间的关系。\n\n三、需求优先级\n\n使用 MoSCoW 方法：Must have / Should have / Could have / Won't have。",
        "category": "需求分析",
        "tags": "需求分析,用户故事,用例图,产品",
        "author_idx": 5,
        "status": "approved",
        "quality_score": 78,
        "view_count": 67,
        "like_count": 8,
        "download_count": 1,
        "comment_count": 1,
        "adopt_count": 0,
    },
    {
        "title": "React vs Vue 2024 技术选型对比",
        "summary": "从生态系统、学习曲线、性能、TypeScript 支持、企业采用率等维度对比 React 和 Vue，帮助团队做出技术选型决策。",
        "content": "一、生态系统\n\nReact 生态更庞大（Next.js、React Native），Vue 生态更统一（Nuxt、Vuetify）。\n\n二、学习曲线\n\nVue 更容易上手（模板语法直观），React 需要理解 JSX 和 Hooks。\n\n三、性能\n\n两者性能接近，Vue 3 的响应式系统在某些场景下更高效。\n\n四、企业采用\n\nReact 在海外更流行，Vue 在国内更流行。",
        "category": "架构设计",
        "tags": "React,Vue,技术选型,前端框架",
        "author_idx": 3,
        "status": "pending",
        "quality_score": 0,
        "view_count": 0,
        "like_count": 0,
        "download_count": 0,
        "comment_count": 0,
        "adopt_count": 0,
    },
    {
        "title": "程序员健身指南：久坐族的办公室拉伸运动",
        "summary": "针对长期久坐的程序员，介绍一套简单有效的办公室拉伸运动，帮助缓解颈椎、腰椎疲劳，预防职业病。",
        "content": "一、为什么程序员需要运动\n\n长期久坐会导致颈椎病、腰椎间盘突出、鼠标手等职业病。每天坚持 15-30 分钟运动可以有效预防。\n\n二、办公室拉伸操\n\n1. 颈部拉伸：左右转头、前后点头、左右侧屈，每个动作保持 15 秒\n2. 肩部环绕：向前 10 圈，向后 10 圈\n3. 手腕旋转：预防鼠标手\n4. 腰部扭转：坐在椅子上，双手扶膝，缓慢转动上身\n5. 腿部拉伸：坐姿前屈，拉伸大腿后侧\n\n三、站立办公\n\n建议每坐 1 小时站立活动 5 分钟，可以使用升降桌。\n\n四、下班后运动推荐\n\n- 跑步：30 分钟有氧，释放压力\n- 游泳：全身运动，对关节友好\n- 瑜伽：改善体态，增强柔韧性",
        "category": "运动健身",
        "tags": "健身,拉伸,程序员健康,办公室运动",
        "author_idx": 2,
        "status": "approved",
        "quality_score": 85,
        "view_count": 132,
        "like_count": 28,
        "download_count": 15,
        "comment_count": 6,
        "adopt_count": 2,
    },
    {
        "title": "程序员健康饮食：一周营养食谱推荐",
        "summary": "为忙碌的程序员量身定制的一周健康食谱，简单易做、营养均衡，帮助保持精力充沛和高效工作状态。",
        "content": "一、饮食原则\n\n1. 早餐要吃好：蛋白质 + 碳水 + 维生素\n2. 午餐要吃饱：荤素搭配，多吃蔬菜\n3. 晚餐要吃少：清淡为主，避免过饱\n4. 加餐选择：坚果、水果、酸奶\n\n二、一周食谱示例\n\n周一：\n- 早餐：全麦面包 + 鸡蛋 + 牛奶 + 香蕉\n- 午餐：糙米饭 + 清蒸鱼 + 西兰花 + 紫菜汤\n- 晚餐：小米粥 + 蒸南瓜 + 凉拌黄瓜\n\n周二：\n- 早餐：燕麦粥 + 蓝莓 + 坚果\n- 午餐：杂粮饭 + 鸡胸肉 + 炒时蔬\n- 晚餐：番茄鸡蛋面 + 水果沙拉\n\n三、办公室零食推荐\n\n- 坚果（核桃、杏仁）：补脑\n- 蓝莓：保护视力\n- 黑巧克力：提神醒脑\n- 酸奶：助消化",
        "category": "健康饮食",
        "tags": "健康饮食,营养,食谱,程序员养生",
        "author_idx": 5,
        "status": "approved",
        "quality_score": 82,
        "view_count": 108,
        "like_count": 22,
        "download_count": 18,
        "comment_count": 5,
        "adopt_count": 1,
    },
    {
        "title": "程序员的音乐伴侣：适合编程时听的音乐推荐",
        "summary": "精选适合编程、学习、工作时聆听的音乐歌单，帮助提升专注力、缓解压力，让编码时光更加愉悦。",
        "content": "一、为什么编程时听音乐\n\n合适的背景音乐可以帮助：\n1. 提升专注力，屏蔽外界干扰\n2. 缓解工作压力\n3. 激发创造力\n4. 保持稳定的编码节奏\n\n二、推荐音乐类型\n\n1. 纯音乐/轻音乐\n   - 久石让钢琴曲（《Summer》《天空之城》）\n   - 班得瑞系列（《安妮的仙境》《童年》）\n   - Yiruma 李闰珉（《River Flows in You》）\n\n2. Lo-Fi Hip Hop\n   - 适合深夜加班\n   - YouTube 24 小时 Lo-Fi 直播\n\n3. 古典音乐\n   - 巴赫《哥德堡变奏曲》\n   - 莫扎特《小星星变奏曲》\n\n4. 电子/氛围音乐\n   - Tycho\n   - Boards of Canada\n\n三、音乐平台推荐\n\n- 网易云音乐：推荐算法精准\n- QQ 音乐：版权丰富\n- Spotify：国际曲库全",
        "category": "音乐艺术",
        "tags": "音乐,编程音乐,专注力,歌单推荐",
        "author_idx": 6,
        "status": "approved",
        "quality_score": 79,
        "view_count": 95,
        "like_count": 35,
        "download_count": 8,
        "comment_count": 12,
        "adopt_count": 3,
    },
    {
        "title": "TypeScript 高级类型体操实战",
        "summary": "深入讲解 TypeScript 条件类型、映射类型、模板字面量类型等高级特性，提升类型安全和代码可维护性。",
        "content": "一、条件类型\n\n条件类型根据条件选择不同的类型：\n\ntype IsString<T> = T extends string ? true : false;\n\n二、映射类型\n\n映射类型可以遍历联合类型生成新的类型：\n\ntype Readonly<T> = { readonly [K in keyof T]: T[K] };\n\n三、模板字面量类型\n\nTypeScript 4.1 引入的模板字面量类型：\n\ntype EventName = `on${Capitalize<'click' | 'focus'>}`;\n\n四、infer 关键字\n\n在条件类型中使用 infer 提取类型：\n\ntype ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;\n\n五、实战应用\n\n- API 响应类型推导\n- 路由参数类型提取\n- 表单校验类型约束",
        "category": "开发经验",
        "tags": "TypeScript,类型系统,前端,高级特性",
        "author_idx": 8,
        "status": "approved",
        "quality_score": 88,
        "view_count": 87,
        "like_count": 19,
        "download_count": 5,
        "comment_count": 3,
        "adopt_count": 1,
    },
    {
        "title": "PostgreSQL 与 MySQL 深度对比",
        "summary": "从性能、功能、生态、运维四个维度全面对比 PostgreSQL 和 MySQL，帮助团队做出数据库选型决策。",
        "content": "一、性能对比\n\nMySQL 在简单读场景下性能更优，PostgreSQL 在复杂查询和写入场景下表现更好。\n\n二、功能对比\n\n- JSON 支持：PostgreSQL 的 JSONB 更强大\n- 全文搜索：PostgreSQL 内置，MySQL 需要外部插件\n- 地理数据：PostgreSQL 有 PostGIS 扩展\n- 窗口函数：两者都支持，PostgreSQL 更完整\n\n三、生态对比\n\nMySQL 生态更成熟（更多 ORM 支持），PostgreSQL 在数据分析领域更流行。\n\n四、运维对比\n\nMySQL 运维工具更多，PostgreSQL 配置更灵活。",
        "category": "数据库",
        "tags": "PostgreSQL,MySQL,数据库选型,对比分析",
        "author_idx": 9,
        "status": "approved",
        "quality_score": 85,
        "view_count": 76,
        "like_count": 14,
        "download_count": 4,
        "comment_count": 2,
        "adopt_count": 0,
    },
    {
        "title": "产品需求文档（PRD）写作指南",
        "summary": "系统讲解如何撰写高质量的产品需求文档，包括用户故事、功能规格、验收标准、原型说明等核心要素。",
        "content": "一、PRD 核心结构\n\n1. 背景与目标\n2. 用户画像\n3. 功能需求\n4. 非功能需求\n5. 验收标准\n\n二、用户故事模板\n\n作为<角色>，我希望<功能>，以便<价值>。\n\n三、功能规格\n\n- 功能描述\n- 输入输出\n- 业务规则\n- 异常处理\n\n四、验收标准\n\n使用 Given-When-Then 格式：\nGiven 用户已登录\nWhen 点击发布按钮\nThen 弹出发布表单\n\n五、常见错误\n\n- 需求描述模糊\n- 缺少边界条件\n- 没有验收标准",
        "category": "需求分析",
        "tags": "PRD,需求文档,产品设计,用户故事",
        "author_idx": 11,
        "status": "approved",
        "quality_score": 82,
        "view_count": 65,
        "like_count": 11,
        "download_count": 3,
        "comment_count": 2,
        "adopt_count": 0,
    },
    {
        "title": "程序员职业发展规划：从初级到架构师",
        "summary": "分享程序员职业发展路径，从初级工程师到高级工程师、技术专家、架构师的成长规划和关键能力要求。",
        "content": "一、职业发展路径\n\n初级工程师 → 中级工程师 → 高级工程师 → 技术专家 → 架构师 → CTO\n\n二、初级到中级（1-3 年）\n\n- 掌握一门主力语言\n- 熟悉常用框架\n- 能独立完成需求\n- 具备基本调试能力\n\n三、中级到高级（3-5 年）\n\n- 深入理解原理\n- 具备性能优化能力\n- 能做技术选型\n- 开始带小团队\n\n四、高级到架构师（5-10 年）\n\n- 系统设计能力\n- 技术视野广阔\n- 跨团队协作\n- 技术战略规划\n\n五、关键建议\n\n- 持续学习\n- 写技术博客\n- 参与开源\n- 培养软技能",
        "category": "职场技能",
        "tags": "职业发展,程序员成长,架构师,技术管理",
        "author_idx": 2,
        "status": "approved",
        "quality_score": 90,
        "view_count": 145,
        "like_count": 42,
        "download_count": 15,
        "comment_count": 8,
        "adopt_count": 3,
    },
    {
        "title": "Figma 设计系统搭建实战",
        "summary": "手把手教你使用 Figma 搭建企业级设计系统，包括组件库、样式变量、自动布局、原型交互等核心能力。",
        "content": "一、设计系统价值\n\n- 统一设计语言\n- 提升设计效率\n- 保证产品一致性\n- 设计开发协作\n\n二、组件库搭建\n\n1. 原子设计方法论\n2. 颜色/字体/间距变量\n3. 按钮/输入框/卡片等基础组件\n4. 导航/表单/弹窗等复合组件\n\n三、Auto Layout\n\n使用 Auto Layout 实现响应式组件：\n- 填充/固定宽度\n- 堆叠/包裹\n- 间距控制\n\n四、组件变体\n\n使用变体管理组件的不同状态：\n- 按钮：primary/secondary/ghost × sm/md/lg\n- 输入框：default/focus/error/disabled\n\n五、交付规范\n\n- 标注规范\n- 切图规范\n- 设计走查",
        "category": "产品设计",
        "tags": "Figma,设计系统,UI设计,组件库",
        "author_idx": 10,
        "status": "approved",
        "quality_score": 86,
        "view_count": 72,
        "like_count": 18,
        "download_count": 6,
        "comment_count": 3,
        "adopt_count": 1,
    },
    {
        "title": "微服务架构设计与落地实践",
        "summary": "从单体到微服务的架构演进，包括服务拆分、API 网关、服务注册发现、配置中心、链路追踪等核心组件设计。",
        "content": "一、何时拆分微服务\n\n- 团队规模超过 10 人\n- 部署频率要求高\n- 不同模块有不同的伸缩需求\n- 需要技术栈多样化\n\n二、服务拆分原则\n\n- 单一职责\n- 高内聚低耦合\n- 按业务领域拆分（DDD）\n- 渐进式拆分\n\n三、核心组件\n\n1. API 网关：Kong / Nginx / Spring Cloud Gateway\n2. 服务注册：Consul / Nacos / Eureka\n3. 配置中心：Apollo / Nacos\n4. 链路追踪：Jaeger / SkyWalking\n5. 消息队列：RabbitMQ / Kafka\n\n四、常见问题\n\n- 分布式事务\n- 服务间通信\n- 数据一致性\n- 运维复杂度",
        "category": "架构设计",
        "tags": "微服务,架构设计,分布式系统,DDD",
        "author_idx": 3,
        "status": "approved",
        "quality_score": 91,
        "view_count": 118,
        "like_count": 28,
        "download_count": 10,
        "comment_count": 5,
        "adopt_count": 2,
    },
    {
        "title": "正则表达式从入门到精通",
        "summary": "系统讲解正则表达式的语法和实战技巧，包括基础匹配、分组捕获、零宽断言、性能优化等核心知识点。",
        "content": "一、基础语法\n\n- . 匹配任意字符\n- * 零次或多次\n- + 一次或多次\n- ? 零次或一次\n- {n,m} n 到 m 次\n\n二、字符类\n\n- [abc] 匹配 a 或 b 或 c\n- [^abc] 匹配非 a/b/c\n- [a-z] 匹配 a 到 z\n- \\d 数字 \\w 字母数字 \\s 空白\n\n三、分组与捕获\n\n- (...) 捕获组\n- (?:...) 非捕获组\n- (?P<name>...) 命名捕获组\n\n四、零宽断言\n\n- (?=...) 正向先行\n- (?!...) 负向先行\n- (?<=...) 正向后行\n- (?<!...) 负向后行\n\n五、实战案例\n\n- 邮箱验证\n- 手机号匹配\n- URL 提取\n- 日志解析",
        "category": "开发经验",
        "tags": "正则表达式,文本处理,编程基础",
        "author_idx": 9,
        "status": "approved",
        "quality_score": 83,
        "view_count": 92,
        "like_count": 16,
        "download_count": 7,
        "comment_count": 4,
        "adopt_count": 1,
    },
    {
        "title": "敏捷开发 Scrum 实战指南",
        "summary": "详细介绍 Scrum 敏捷开发框架的核心流程、角色定义、仪式活动和工件管理，帮助团队高效协作。",
        "content": "一、Scrum 三大角色\n\n- Product Owner：产品负责人，管理需求优先级\n- Scrum Master：流程守护者，移除障碍\n- Development Team：开发团队，自组织完成迭代\n\n二、Scrum 五大仪式\n\n1. Sprint Planning：规划迭代目标\n2. Daily Standup：每日站会（15 分钟）\n3. Sprint Review：演示迭代成果\n4. Sprint Retrospective：回顾改进\n5. Backlog Refinement：需求梳理\n\n三、Scrum 三大工件\n\n- Product Backlog：需求列表\n- Sprint Backlog：迭代任务\n- Increment：可交付增量\n\n四、常见误区\n\n- 把 Scrum 当瀑布用\n- 忽视回顾会\n- PO 不参与开发\n- 过度追求工具",
        "category": "项目管理",
        "tags": "Scrum,敏捷开发,项目管理,团队协作",
        "author_idx": 11,
        "status": "approved",
        "quality_score": 84,
        "view_count": 68,
        "like_count": 13,
        "download_count": 4,
        "comment_count": 2,
        "adopt_count": 0,
    },
    {
        "title": "Web 安全防护：XSS/CSRF/SQL注入全解析",
        "summary": "全面解析 Web 应用常见安全漏洞的原理、攻击方式和防御措施，帮助开发者构建安全可靠的应用。",
        "content": "一、XSS 攻击\n\n跨站脚本攻击，攻击者在页面注入恶意脚本。\n\n防御：\n- 输入验证和输出编码\n- Content-Security-Policy 头\n- HttpOnly Cookie\n\n二、CSRF 攻击\n\n跨站请求伪造，利用用户已登录状态执行恶意操作。\n\n防御：\n- CSRF Token\n- SameSite Cookie\n- 验证 Referer/Origin\n\n三、SQL 注入\n\n通过拼接 SQL 语句执行恶意查询。\n\n防御：\n- 参数化查询\n- ORM 框架\n- 最小权限原则\n\n四、其他安全实践\n\n- HTTPS 强制\n- 密码哈希存储\n- 限流防刷\n- 日志审计",
        "category": "安全运维",
        "tags": "Web安全,XSS,CSRF,SQL注入,安全防护",
        "author_idx": 7,
        "status": "approved",
        "quality_score": 89,
        "view_count": 103,
        "like_count": 25,
        "download_count": 9,
        "comment_count": 4,
        "adopt_count": 2,
    },
    {
        "title": "机器学习入门：从线性回归到神经网络",
        "summary": "面向程序员的机器学习入门指南，从数学原理到代码实现，涵盖线性回归、逻辑回归、神经网络等核心算法。",
        "content": "一、机器学习分类\n\n- 监督学习：分类、回归\n- 无监督学习：聚类、降维\n- 强化学习：策略优化\n\n二、线性回归\n\n目标函数：y = wx + b\n损失函数：MSE\n优化方法：梯度下降\n\n三、逻辑回归\n\n用于二分类问题\n激活函数：Sigmoid\n损失函数：交叉熵\n\n四、神经网络\n\n- 输入层\n- 隐藏层（激活函数 ReLU）\n- 输出层\n- 反向传播\n\n五、实战工具\n\n- Python + NumPy\n- Scikit-learn\n- TensorFlow / PyTorch",
        "category": "学习方法",
        "tags": "机器学习,AI,Python,算法入门",
        "author_idx": 8,
        "status": "approved",
        "quality_score": 87,
        "view_count": 134,
        "like_count": 31,
        "download_count": 12,
        "comment_count": 6,
        "adopt_count": 2,
    },
]

# 示例评论
COMMENTS = [
    (1, 2, "写得很好，Composition API 确实比 Options API 更灵活！"),
    (1, 3, "组合式函数的封装技巧很实用，已收藏。"),
    (1, 4, "建议补充一下 provide/inject 的使用场景。"),
    (2, 1, "分层架构的思路很清晰，值得学习。"),
    (2, 5, "统一响应格式这个设计很好，前端处理起来方便多了。"),
    (3, 6, "EXPLAIN 分析那部分讲得很详细，受教了。"),
    (3, 2, "联合索引的最左匹配原则之前一直搞不清楚，现在明白了。"),
    (4, 7, "Design Token 的设计思路很专业，适合团队推广。"),
    (5, 1, "JWT 安全实践那部分很重要，很多项目都忽略了。"),
    (6, 3, "ECharts 的配色方案很有参考价值。"),
]


def seed():
    with Session(engine) as db:
        # 初始化配置和管理员
        ensure_default_configs(db)
        ensure_init_admin(db)

        # 创建用户
        user_map = {}
        for u in USERS:
            user = db.scalar(
                __import__("sqlalchemy").select(User).where(User.username == u["username"])
            )
            if not user:
                user = User(
                    username=u["username"],
                    password=hash_password(u["password"]),
                    real_name=u["real_name"],
                    role=u["role"],
                    department=u["department"],
                    email=f"{u['username']}@company.com",
                    status="active",
                )
                db.add(user)
                db.flush()
            user_map[u["username"]] = user

        # 按标题检查已有知识，避免重复填充
        existing_titles = set(
            row[0] for row in db.query(Knowledge.title).all()
        )

        # 创建知识
        knowledge_list = []
        base_time = datetime.now() - timedelta(days=30)
        for i, k in enumerate(KNOWLEDGE_DATA):
            if k["title"] in existing_titles:
                # 已存在，跳过但加入列表（用于评论引用）
                existing = db.scalar(
                    __import__("sqlalchemy").select(Knowledge).where(Knowledge.title == k["title"])
                )
                if existing:
                    knowledge_list.append(existing)
                continue
            author = user_map[USERS[k["author_idx"]]["username"]]
            create_time = base_time + timedelta(days=i * 2 + random.randint(0, 2))
            knowledge = Knowledge(
                title=k["title"],
                summary=k["summary"],
                content=k["content"],
                category=k["category"],
                tags=k["tags"],
                author_id=author.id,
                status=k["status"],
                quality_score=k["quality_score"],
                view_count=k["view_count"],
                like_count=k["like_count"],
                download_count=k["download_count"],
                comment_count=k["comment_count"],
                adopt_count=k["adopt_count"],
                create_time=create_time,
                update_time=create_time,
            )
            db.add(knowledge)
            db.flush()
            knowledge_list.append(knowledge)

            # 计算贡献度
            base = float(k["quality_score"] or 0) * 0.3
            interaction = k["view_count"] * 0.01 + k["download_count"] * 0.05 + k["like_count"] * 0.05 + k["comment_count"] * 0.1 + k["adopt_count"] * 0.5
            knowledge.contribution_score = round(base + interaction, 2)

        # 创建评论
        for knowledge_idx, user_idx, content in COMMENTS:
            if knowledge_idx <= len(knowledge_list):
                comment = KnowledgeComment(
                    knowledge_id=knowledge_list[knowledge_idx - 1].id,
                    user_id=user_map[USERS[user_idx]["username"]].id,
                    content=content,
                    create_time=base_time + timedelta(days=knowledge_idx * 2 + 3, hours=random.randint(1, 12)),
                )
                db.add(comment)

        # 更新用户积分
        points_map = {
            "zhangsan": 85, "lisi": 68, "wangwu": 52, "zhaoliu": 45,
            "sunqi": 38, "zhouba": 32, "wujiu": 25, "zhengshi": 22,
            "liuyi": 18, "chener": 15, "yangsan": 12, "huangsi": 10,
        }
        contribution_map = {
            "zhangsan": 45.2, "lisi": 38.5, "wangwu": 32.1, "zhaoliu": 28.3,
            "sunqi": 22.6, "zhouba": 18.9, "wujiu": 15.4, "zhengshi": 12.8,
            "liuyi": 10.2, "chener": 8.5, "yangsan": 6.3, "huangsi": 4.8,
        }
        for username, points in points_map.items():
            user = user_map.get(username)
            if user:
                user.total_points = points
                user.total_contribution = contribution_map.get(username, 0)

        # 管理员积分
        user_map["admin"].total_points = 120
        user_map["admin"].total_contribution = 65.0

        # 创建积分记录
        point_types = ["upload_pass_reward", "view_reward", "download_reward", "like_reward", "comment_reward", "adopt_reward"]
        for username, user in user_map.items():
            if username == "admin":
                continue
            total = points_map.get(username, 0)
            remaining = total
            records_count = random.randint(3, 6)
            for j in range(records_count):
                change = random.randint(1, min(10, remaining)) if remaining > 0 else 0
                if change == 0:
                    break
                remaining -= change
                record = PointRecord(
                    user_id=user.id,
                    points_type=random.choice(point_types),
                    change_value=change,
                    before_points=total - remaining - change,
                    after_points=total - remaining,
                    contribution_value=round(change * 0.5, 2),
                    remark="系统自动奖励",
                    create_time=base_time + timedelta(days=j * 3 + random.randint(0, 2)),
                )
                db.add(record)

        db.commit()
        print(f"示例数据填充完成：{len(USERS)} 个用户，{len(KNOWLEDGE_DATA)} 篇知识，{len(COMMENTS)} 条评论")


if __name__ == "__main__":
    seed()
