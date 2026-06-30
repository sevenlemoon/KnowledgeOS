"""外部知识源聚合 API - Dev.to + GitHub + Bilibili"""
import httpx
from fastapi import APIRouter, Query
from fastapi.responses import Response
from app.core.response import success

router = APIRouter(prefix="/external", tags=["外部知识源"])


@router.get("/articles")
async def get_external_articles(
    tag: str = Query(default="", description="标签过滤"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=30),
    source: str = Query(default="devto", description="来源: devto/github/bilibili"),
):
    """获取外部技术文章（带图片、标签、跳转链接）"""
    articles = []

    if source == "devto":
        articles = await _fetch_devto(tag, page, page_size)
    elif source == "github":
        articles = await _fetch_github(tag, page, page_size)
    elif source == "bilibili":
        articles = await _fetch_bilibili(tag, page, page_size)

    return success({
        "items": articles,
        "total": len(articles) * 10,  # 估算总数用于分页
        "page": page,
        "page_size": page_size,
    })


async def _fetch_devto(tag: str, page: int, per_page: int) -> list:
    """从 Dev.to API 获取技术文章"""
    url = "https://dev.to/api/articles"
    params = {"page": page, "per_page": per_page}
    if tag:
        params["tag"] = tag

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "id": f"devto-{item['id']}",
                    "title": item.get("title", ""),
                    "summary": item.get("description", "")[:200],
                    "cover_image": item.get("cover_image") or item.get("social_image") or "",
                    "url": item.get("url", ""),
                    "tags": item.get("tag_list", []),
                    "author": item.get("user", {}).get("name", "Unknown"),
                    "author_avatar": item.get("user", {}).get("profile_image_90", ""),
                    "published_at": item.get("readable_publish_date", ""),
                    "reading_time": item.get("reading_time_minutes", 0),
                    "comments_count": item.get("comments_count", 0),
                    "reactions_count": item.get("public_reactions_count", 0),
                    "source": "Dev.to",
                }
                for item in data
            ]
    except Exception:
        return []


async def _fetch_github(tag: str, page: int, per_page: int) -> list:
    """从 GitHub Trending 获取热门开源项目"""
    if tag:
        url = f"https://api.github.com/search/repositories?q={tag}&sort=stars&order=desc&page={page}&per_page={per_page}"
    else:
        url = f"https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc&page={page}&per_page={per_page}"

    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "KnowledgeOS"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
            items = data.get("items", [])
            return [
                {
                    "id": f"github-{item.get('id', '')}",
                    "title": item.get("full_name", ""),
                    "summary": (item.get("description") or "")[:200],
                    "cover_image": "",
                    "url": item.get("html_url", ""),
                    "tags": [t for t in [item.get("language", "")] if t],
                    "author": item.get("owner", {}).get("login", ""),
                    "author_avatar": item.get("owner", {}).get("avatar_url", ""),
                    "published_at": item.get("created_at", "")[:10],
                    "reading_time": 0,
                    "comments_count": item.get("open_issues_count", 0),
                    "reactions_count": item.get("stargazers_count", 0),
                    "source": "GitHub",
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                }
                for item in items
            ]
    except Exception:
        return []


@router.get("/image-proxy")
async def image_proxy(url: str = Query(..., description="图片URL")):
    """图片代理 - 绕过防盗链"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.bilibili.com",
            })
            return Response(
                content=resp.content,
                media_type=resp.headers.get("content-type", "image/jpeg"),
            )
    except Exception:
        return Response(status_code=502)


async def _fetch_bilibili(tag: str, page: int, page_size: int) -> list:
    """从 Bilibili 获取热门视频"""
    # Bilibili 全站热门视频 API
    url = "https://api.bilibili.com/x/web-interface/popular"
    params = {
        "ps": page_size,
        "pn": page,
    }
    # 如果有标签，尝试搜索
    if tag:
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            "keyword": tag,
            "search_type": "video",
            "page": page,
            "page_size": page_size,
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code != 200:
                return []
            result = resp.json()
            if result.get("code") != 0:
                return []

            items = result.get("data", {}).get("result", []) if tag else result.get("data", {}).get("list", [])
            articles = []
            for item in items:
                if tag:
                    # 搜索结果格式
                    bvid = item.get("bvid", "")
                    articles.append({
                        "id": f"bili-{bvid}",
                        "title": _strip_html(item.get("title", "")),
                        "summary": _strip_html(item.get("description", ""))[:200],
                        "cover_image": _fix_url(item.get("pic", "")),
                        "url": f"https://www.bilibili.com/video/{bvid}",
                        "tags": [tag],
                        "author": item.get("author", ""),
                        "author_avatar": "",
                        "published_at": item.get("pubdate", ""),
                        "reading_time": round(item.get("duration", "0:00").count(":") and _parse_duration(item.get("duration", "0:00"))),
                        "comments_count": item.get("review", 0),
                        "reactions_count": item.get("play", 0),
                        "source": "Bilibili",
                        "video_duration": item.get("duration", ""),
                    })
                else:
                    # 热门视频格式
                    bvid = item.get("bvid", "")
                    owner = item.get("owner", {})
                    stat = item.get("stat", {})
                    duration_sec = item.get("duration", 0)
                    duration_str = _seconds_to_duration(duration_sec)
                    articles.append({
                        "id": f"bili-{bvid}",
                        "title": item.get("title", ""),
                        "summary": item.get("desc", "")[:200],
                        "cover_image": _fix_url(item.get("pic", "")),
                        "url": f"https://www.bilibili.com/video/{bvid}",
                        "tags": [item.get("tname", "视频")],
                        "author": owner.get("name", ""),
                        "author_avatar": _fix_url(owner.get("face", "")),
                        "published_at": "",
                        "reading_time": round(duration_sec / 60) if duration_sec else 0,
                        "comments_count": stat.get("reply", 0),
                        "reactions_count": stat.get("view", 0),
                        "source": "Bilibili",
                        "video_duration": duration_str,
                    })
            return articles
    except Exception:
        return []


def _fix_url(url: str) -> str:
    """修复 URL：// 开头或 http:// 转为 https://"""
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url


def _strip_html(text: str) -> str:
    """去除 HTML 标签"""
    import re
    return re.sub(r'<[^>]+>', '', text) if text else ""


def _parse_duration(duration: str) -> int:
    """将时长字符串转为分钟数"""
    try:
        parts = duration.split(":")
        if len(parts) == 2:
            return int(parts[0])
        elif len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    except (ValueError, IndexError):
        return 0


def _seconds_to_duration(seconds: int) -> str:
    """将秒数转为 MM:SS 或 HH:MM:SS 格式"""
    if not seconds:
        return ""
    minutes, sec = divmod(int(seconds), 60)
    hour, minute = divmod(minutes, 60)
    if hour > 0:
        return f"{hour}:{minute:02d}:{sec:02d}"
    return f"{minute}:{sec:02d}"


@router.get("/tags")
async def get_popular_tags():
    """获取热门技术标签（用于筛选）"""
    tags = [
        {"name": "python", "label": "Python", "color": "#3776AB"},
        {"name": "javascript", "label": "JavaScript", "color": "#F7DF1E"},
        {"name": "typescript", "label": "TypeScript", "color": "#3178C6"},
        {"name": "react", "label": "React", "color": "#61DAFB"},
        {"name": "vue", "label": "Vue", "color": "#4FC08D"},
        {"name": "rust", "label": "Rust", "color": "#CE422B"},
        {"name": "golang", "label": "Go", "color": "#00ADD8"},
        {"name": "docker", "label": "Docker", "color": "#2496ED"},
        {"name": "ai", "label": "AI", "color": "#FF6F61"},
        {"name": "webdev", "label": "Web Dev", "color": "#6366F1"},
        {"name": "devops", "label": "DevOps", "color": "#10B981"},
        {"name": "database", "label": "Database", "color": "#F59E0B"},
    ]
    return success(tags)
