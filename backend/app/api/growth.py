"""KnowledgeOS 成长体系 API - 签到/勋章/技能树/AI教练/知识体检"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import success
from app.db.session import get_db
from app.models import (
    User, Knowledge, DailyCheckIn, Badge, UserBadge,
    SkillCategory, SkillNode, UserSkill, LearningGoal,
    KnowledgeHealthScore, GrowthRecord, UserInteraction,
)

router = APIRouter(prefix="/growth", tags=["成长体系"])


# ==================== 签到系统 ====================

@router.post("/checkin")
def daily_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    # 检查今天是否已签到
    existing = db.scalar(
        select(DailyCheckIn).where(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.checkin_date == today,
        )
    )
    if existing:
        return success({"streak_days": existing.streak_days, "points": existing.points_earned}, "今日已签到")

    # 计算连续签到天数
    yesterday_record = db.scalar(
        select(DailyCheckIn).where(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.checkin_date == yesterday,
        )
    )
    streak = (yesterday_record.streak_days + 1) if yesterday_record else 1

    # 积分奖励：基础 5 分，连续 7 天额外 20 分
    points = 5
    if streak % 7 == 0:
        points += 20

    record = DailyCheckIn(
        user_id=current_user.id,
        checkin_date=today,
        streak_days=streak,
        points_earned=points,
    )
    db.add(record)

    # 更新用户积分
    current_user.total_points += points
    db.add(GrowthRecord(
        user_id=current_user.id,
        change_type="checkin",
        change_value=points,
        description=f"每日签到（连续{streak}天）",
    ))

    db.commit()
    return success({"streak_days": streak, "points": points, "total_points": current_user.total_points})


@router.get("/checkin/status")
def checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    record = db.scalar(
        select(DailyCheckIn).where(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.checkin_date == today,
        )
    )
    # 获取本月签到天数
    month_start = today[:7] + "-01"
    month_count = db.scalar(
        select(func.count()).where(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.checkin_date >= month_start,
        )
    ) or 0
    # 当前连续天数
    streak = record.streak_days if record else 0
    # 查找最近的签到记录来计算连续天数
    if not record:
        check = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for i in range(1, 365):
            prev = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            prev_record = db.scalar(
                select(DailyCheckIn).where(
                    DailyCheckIn.user_id == current_user.id,
                    DailyCheckIn.checkin_date == prev,
                )
            )
            if prev_record:
                streak = prev_record.streak_days
                break
            else:
                break

    return success({
        "checked_in_today": record is not None,
        "streak_days": streak,
        "month_count": month_count,
    })


# ==================== 勋章系统 ====================

@router.get("/badges")
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户已获得和可获得的勋章"""
    all_badges = db.scalars(select(Badge)).all()
    earned_ids = set(
        row[0] for row in db.query(UserBadge.badge_id).filter(UserBadge.user_id == current_user.id).all()
    )
    result = []
    for b in all_badges:
        result.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "icon": b.icon,
            "category": b.category,
            "rarity": b.rarity,
            "earned": b.id in earned_ids,
            "condition_type": b.condition_type,
            "condition_value": b.condition_value,
        })
    return success({"badges": result, "earned_count": len(earned_ids)})


# ==================== 技能树 ====================

@router.get("/skill-tree")
def get_skill_tree(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = db.scalars(select(SkillCategory).order_by(SkillCategory.sort_order)).all()
    user_skills = {
        us.skill_node_id: us
        for us in db.scalars(select(UserSkill).where(UserSkill.user_id == current_user.id)).all()
    }

    tree = []
    for cat in categories:
        nodes = db.scalars(
            select(SkillNode).where(SkillNode.category_id == cat.id).order_by(SkillNode.level)
        ).all()
        node_list = []
        for n in nodes:
            us = user_skills.get(n.id)
            node_list.append({
                "id": n.id,
                "name": n.name,
                "description": n.description,
                "level": n.level,
                "parent_id": n.parent_id,
                "progress": us.progress if us else 0,
                "mastered": us.mastered if us else False,
                "unlocked": us is not None,
            })
        tree.append({
            "category": {"id": cat.id, "name": cat.name, "icon": cat.icon},
            "nodes": node_list,
        })
    return success(tree)


# ==================== AI 教练 ====================

@router.get("/ai-coach")
def ai_coach_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 成长教练 - 基于用户行为数据生成建议"""
    knowledge_count = db.scalar(
        select(func.count()).where(Knowledge.author_id == current_user.id, Knowledge.status == "approved")
    ) or 0
    total_views = db.scalar(
        select(func.coalesce(func.sum(Knowledge.view_count), 0)).where(Knowledge.author_id == current_user.id)
    ) or 0
    total_likes = db.scalar(
        select(func.coalesce(func.sum(Knowledge.like_count), 0)).where(Knowledge.author_id == current_user.id)
    ) or 0
    from app.models import KnowledgeComment
    comment_count = db.scalar(
        select(func.count()).select_from(KnowledgeComment)
        .join(Knowledge, KnowledgeComment.knowledge_id == Knowledge.id)
        .where(Knowledge.author_id == current_user.id)
    ) or 0

    # 计算成长等级
    growth_points = current_user.total_points
    level = min(30, growth_points // 100 + 1)
    next_level_points = (level) * 100

    # 生成建议
    suggestions = []
    if knowledge_count < 3:
        suggestions.append({"type": "publish", "text": "再发布 {} 篇知识即可解锁「知识贡献者」勋章".format(3 - knowledge_count), "priority": "high"})
    if knowledge_count >= 3 and knowledge_count < 10:
        suggestions.append({"type": "publish", "text": "继续发布 {} 篇知识，迈向「知识达人」".format(10 - knowledge_count), "priority": "medium"})
    if total_likes < 10:
        suggestions.append({"type": "social", "text": "多与其他用户互动，提升你的知识影响力", "priority": "medium"})
    if growth_points < next_level_points:
        remaining = next_level_points - growth_points
        suggestions.append({"type": "growth", "text": "距离 Lv.{} 还需 {} 成长值".format(level + 1, remaining), "priority": "low"})

    # 今日学习目标
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    goal = db.scalar(
        select(LearningGoal).where(LearningGoal.user_id == current_user.id, LearningGoal.goal_date == today)
    )
    if not goal:
        goal = LearningGoal(user_id=current_user.id, goal_date=today)
        db.add(goal)
        db.commit()

    return success({
        "level": level,
        "growth_points": growth_points,
        "next_level_points": next_level_points,
        "knowledge_count": knowledge_count,
        "total_views": total_views,
        "total_likes": total_likes,
        "suggestions": suggestions,
        "today_goal": {
            "target_reads": goal.target_reads,
            "target_publish": goal.target_publish,
            "actual_reads": goal.actual_reads,
            "actual_publish": goal.actual_publish,
            "completed": goal.completed,
        },
    })


# ==================== 知识健康度 ====================

@router.get("/knowledge-health/{knowledge_id}")
def get_knowledge_health(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取知识健康度评分（AI体检）"""
    knowledge = db.get(Knowledge, knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")

    # 检查缓存
    cached = db.scalar(
        select(KnowledgeHealthScore).where(KnowledgeHealthScore.knowledge_id == knowledge_id)
    )
    if cached:
        return success({
            "completeness": float(cached.completeness),
            "readability": float(cached.readability),
            "structure": float(cached.structure),
            "freshness": float(cached.freshness),
            "engagement": float(cached.engagement),
            "overall_score": float(cached.overall_score),
            "ai_suggestion": cached.ai_suggestion,
        })

    # 实时计算健康度
    content = knowledge.content or ""
    word_count = len(content)
    has_summary = bool(knowledge.summary and len(knowledge.summary) > 10)
    has_tags = bool(knowledge.tags and len(knowledge.tags) > 0)
    has_sections = content.count("\n\n") >= 2

    # 完整度：基于字数、摘要、标签
    completeness = min(100, (word_count / 500) * 40 + (30 if has_summary else 0) + (30 if has_tags else 0))

    # 可读性：基于段落数和字数
    paragraphs = len([p for p in content.split("\n") if p.strip()])
    readability = min(100, paragraphs * 8 + (20 if word_count > 300 else 10))

    # 结构性：是否有分段、标题
    structure = min(100, (40 if has_sections else 10) + (30 if "一、" in content or "##" in content else 0) + (30 if paragraphs > 5 else 10))

    # 新鲜度：基于创建时间
    days_old = (datetime.now(timezone.utc) - (knowledge.create_time or datetime.now(timezone.utc))).days
    freshness = max(20, 100 - days_old * 2)

    # 互动度
    engagement = min(100, knowledge.view_count * 0.5 + knowledge.like_count * 3 + knowledge.comment_count * 5)

    overall = completeness * 0.3 + readability * 0.2 + structure * 0.2 + freshness * 0.15 + engagement * 0.15

    # AI 建议
    tips = []
    if completeness < 70:
        tips.append("建议补充更详细的摘要和标签")
    if structure < 60:
        tips.append("建议使用分段标题优化内容结构")
    if word_count < 300:
        tips.append("内容偏短，建议扩充至 500 字以上")
    if freshness < 50:
        tips.append("内容较久未更新，建议维护刷新")

    suggestion = "；".join(tips) if tips else "知识质量优秀，继续保持！"

    # 缓存结果
    score = KnowledgeHealthScore(
        knowledge_id=knowledge_id,
        completeness=round(completeness, 1),
        readability=round(readability, 1),
        structure=round(structure, 1),
        freshness=round(freshness, 1),
        engagement=round(engagement, 1),
        overall_score=round(overall, 1),
        ai_suggestion=suggestion,
    )
    db.merge(score)
    db.commit()

    return success({
        "completeness": round(completeness, 1),
        "readability": round(readability, 1),
        "structure": round(structure, 1),
        "freshness": round(freshness, 1),
        "engagement": round(engagement, 1),
        "overall_score": round(overall, 1),
        "ai_suggestion": suggestion,
    })


# ==================== 成长统计 ====================

@router.get("/stats")
def growth_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户成长统计数据"""
    # 连续签到天数
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_checkin = db.scalar(
        select(DailyCheckIn).where(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.checkin_date == today,
        )
    )
    streak = today_checkin.streak_days if today_checkin else 0

    # 总签到天数
    total_checkins = db.scalar(
        select(func.count()).where(DailyCheckIn.user_id == current_user.id)
    ) or 0

    # 勋章数
    badge_count = db.scalar(
        select(func.count()).where(UserBadge.user_id == current_user.id)
    ) or 0

    # 技能掌握数
    skill_mastered = db.scalar(
        select(func.count()).where(UserSkill.user_id == current_user.id, UserSkill.mastered == True)
    ) or 0

    # 成长等级
    level = min(30, current_user.total_points // 100 + 1)

    # 最近7天成长值趋势
    week_records = db.scalars(
        select(GrowthRecord)
        .where(GrowthRecord.user_id == current_user.id)
        .order_by(GrowthRecord.create_time.desc())
        .limit(50)
    ).all()

    daily_growth = {}
    for r in week_records:
        day = r.create_time.strftime("%m-%d")
        daily_growth[day] = daily_growth.get(day, 0) + r.change_value

    return success({
        "level": level,
        "growth_points": current_user.total_points,
        "total_contribution": float(current_user.total_contribution or 0),
        "streak_days": streak,
        "total_checkins": total_checkins,
        "badge_count": badge_count,
        "skill_mastered": skill_mastered,
        "weekly_growth": daily_growth,
    })
