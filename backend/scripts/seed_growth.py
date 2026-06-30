"""KnowledgeOS 成长体系种子数据 - 勋章/技能树"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import engine
from app.models import Badge, SkillCategory, SkillNode


def seed_growth():
    with Session(engine) as db:
        # ==================== 勋章 ====================
        badges_data = [
            # 成长类
            {"name": "初来乍到", "description": "完成首次签到", "icon": "Sunny", "category": "growth", "condition_type": "checkin_count", "condition_value": 1, "points_reward": 5, "rarity": "common"},
            {"name": "坚持不懈", "description": "连续签到 7 天", "icon": "Calendar", "category": "streak", "condition_type": "streak_days", "condition_value": 7, "points_reward": 20, "rarity": "rare"},
            {"name": "钢铁意志", "description": "连续签到 30 天", "icon": "Medal", "category": "streak", "condition_type": "streak_days", "condition_value": 30, "points_reward": 100, "rarity": "epic"},
            {"name": "传奇之光", "description": "连续签到 100 天", "icon": "Trophy", "category": "streak", "condition_type": "streak_days", "condition_value": 100, "points_reward": 500, "rarity": "legendary"},
            # 知识类
            {"name": "知识新星", "description": "发布第 1 篇知识", "icon": "Star", "category": "knowledge", "condition_type": "knowledge_count", "condition_value": 1, "points_reward": 10, "rarity": "common"},
            {"name": "知识贡献者", "description": "发布 5 篇知识", "icon": "Collection", "category": "knowledge", "condition_type": "knowledge_count", "condition_value": 5, "points_reward": 30, "rarity": "rare"},
            {"name": "知识达人", "description": "发布 10 篇知识", "icon": "Promotion", "category": "knowledge", "condition_type": "knowledge_count", "condition_value": 10, "points_reward": 80, "rarity": "epic"},
            {"name": "知识大师", "description": "发布 20 篇知识", "icon": "Crown", "category": "knowledge", "condition_type": "knowledge_count", "condition_value": 20, "points_reward": 200, "rarity": "legendary"},
            # 互动类
            {"name": "初识社交", "description": "获得 10 个点赞", "icon": "ChatDotRound", "category": "social", "condition_type": "total_likes", "condition_value": 10, "points_reward": 10, "rarity": "common"},
            {"name": "人气之星", "description": "获得 50 个点赞", "icon": "ChatLineRound", "category": "social", "condition_type": "total_likes", "condition_value": 50, "points_reward": 50, "rarity": "rare"},
            {"name": "知识网红", "description": "获得 200 个点赞", "icon": "ChatSquare", "category": "social", "condition_type": "total_likes", "condition_value": 200, "points_reward": 150, "rarity": "epic"},
            # 积分类
            {"name": "积分新手", "description": "累计 100 积分", "icon": "Coin", "category": "growth", "condition_type": "total_points", "condition_value": 100, "points_reward": 10, "rarity": "common"},
            {"name": "积分达人", "description": "累计 500 积分", "icon": "Wallet", "category": "growth", "condition_type": "total_points", "condition_value": 500, "points_reward": 50, "rarity": "rare"},
            {"name": "积分王者", "description": "累计 2000 积分", "icon": "Present", "category": "growth", "condition_type": "total_points", "condition_value": 2000, "points_reward": 200, "rarity": "legendary"},
        ]
        for b in badges_data:
            if not db.scalar(select(Badge).where(Badge.name == b["name"])):
                db.add(Badge(**b))
        db.commit()

        # ==================== 技能分类 ====================
        skill_cats = [
            {"name": "前端开发", "description": "Web 前端技术栈", "icon": "Monitor", "sort_order": 1},
            {"name": "后端开发", "description": "服务端技术栈", "icon": "Cpu", "sort_order": 2},
            {"name": "数据库", "description": "数据库技术", "icon": "Coin", "sort_order": 3},
            {"name": "DevOps", "description": "运维与部署", "icon": "SetUp", "sort_order": 4},
            {"name": "产品设计", "description": "UI/UX 与产品思维", "icon": "Brush", "sort_order": 5},
        ]
        cat_map = {}
        for c in skill_cats:
            cat = db.scalar(select(SkillCategory).where(SkillCategory.name == c["name"]))
            if not cat:
                cat = SkillCategory(**c)
                db.add(cat)
                db.flush()
            cat_map[c["name"]] = cat.id
        db.commit()

        # ==================== 技能树节点 ====================
        skills_data = [
            # 前端开发
            {"cat": "前端开发", "name": "HTML/CSS", "level": 1, "parent": None, "points": 10},
            {"cat": "前端开发", "name": "JavaScript", "level": 1, "parent": None, "points": 15},
            {"cat": "前端开发", "name": "Vue.js", "level": 2, "parent": "JavaScript", "points": 20},
            {"cat": "前端开发", "name": "React", "level": 2, "parent": "JavaScript", "points": 20},
            {"cat": "前端开发", "name": "TypeScript", "level": 2, "parent": "JavaScript", "points": 20},
            {"cat": "前端开发", "name": "工程化(Vite/Webpack)", "level": 3, "parent": "Vue.js", "points": 30},
            # 后端开发
            {"cat": "后端开发", "name": "Python", "level": 1, "parent": None, "points": 10},
            {"cat": "后端开发", "name": "Java", "level": 1, "parent": None, "points": 15},
            {"cat": "后端开发", "name": "FastAPI", "level": 2, "parent": "Python", "points": 20},
            {"cat": "后端开发", "name": "Spring Boot", "level": 2, "parent": "Java", "points": 25},
            {"cat": "后端开发", "name": "RESTful API 设计", "level": 2, "parent": None, "points": 15},
            {"cat": "后端开发", "name": "微服务架构", "level": 3, "parent": "Spring Boot", "points": 35},
            # 数据库
            {"cat": "数据库", "name": "SQL 基础", "level": 1, "parent": None, "points": 10},
            {"cat": "数据库", "name": "MySQL", "level": 2, "parent": "SQL 基础", "points": 20},
            {"cat": "数据库", "name": "Redis", "level": 2, "parent": None, "points": 20},
            {"cat": "数据库", "name": "SQLAlchemy ORM", "level": 3, "parent": "MySQL", "points": 25},
            {"cat": "数据库", "name": "MongoDB", "level": 2, "parent": None, "points": 20},
            # DevOps
            {"cat": "DevOps", "name": "Linux 基础", "level": 1, "parent": None, "points": 10},
            {"cat": "DevOps", "name": "Docker", "level": 2, "parent": "Linux 基础", "points": 20},
            {"cat": "DevOps", "name": "Nginx", "level": 2, "parent": "Linux 基础", "points": 15},
            {"cat": "DevOps", "name": "CI/CD", "level": 3, "parent": "Docker", "points": 30},
            {"cat": "DevOps", "name": "Kubernetes", "level": 3, "parent": "Docker", "points": 40},
            # 产品设计
            {"cat": "产品设计", "name": "设计原则", "level": 1, "parent": None, "points": 10},
            {"cat": "产品设计", "name": "Figma/Sketch", "level": 1, "parent": None, "points": 10},
            {"cat": "产品设计", "name": "Design Token", "level": 2, "parent": "设计原则", "points": 20},
            {"cat": "产品设计", "name": "用户研究", "level": 2, "parent": "设计原则", "points": 15},
            {"cat": "产品设计", "name": "数据驱动设计", "level": 3, "parent": "用户研究", "points": 30},
        ]

        node_map = {}
        for s in skills_data:
            existing = db.scalar(select(SkillNode).where(
                SkillNode.name == s["name"],
                SkillNode.category_id == cat_map[s["cat"]],
            ))
            if existing:
                node_map[s["name"]] = existing.id
                continue
            node = SkillNode(
                category_id=cat_map[s["cat"]],
                name=s["name"],
                level=s["level"],
                required_points=s["points"],
            )
            if s["parent"] and s["parent"] in node_map:
                node.parent_id = node_map[s["parent"]]
            db.add(node)
            db.flush()
            node_map[s["name"]] = node.id
        db.commit()
        print(f"成长体系种子数据完成: {len(badges_data)} 个勋章, {len(skill_cats)} 个技能分类, {len(skills_data)} 个技能节点")


if __name__ == "__main__":
    seed_growth()
