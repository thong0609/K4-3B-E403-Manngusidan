"""
agents/search_agent.py — Tìm tài liệu web bằng Tavily API thật
"""
import logging
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tavily import TavilyClient

from config import settings

logger = logging.getLogger(__name__)

_tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

# Các domain có thể yêu cầu đăng nhập hoặc chặn scrape
_BLOCKED_DOMAINS = {
    "facebook.com", "twitter.com", "x.com", "instagram.com",
    "linkedin.com", "tiktok.com", "youtube.com",
}

# Nội dung trang quá ngắn → không đáng tin / không load được
_MIN_CONTENT_LENGTH = 300


def _build_queries(topic: str, learning_goal: str) -> list[str]:
    """Tạo 3 query tìm kiếm: 2 tiếng Việt, 1 tiếng Anh."""
    return [
        f"{topic} bài giảng kiến thức",
        f"{topic} {learning_goal}",
        f"{topic} explained overview",
    ]


def _domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _is_blocked(url: str) -> bool:
    domain = _domain_of(url)
    return any(blocked in domain for blocked in _BLOCKED_DOMAINS)


def _scrape_content(url: str) -> str | None:
    """Scrape nội dung văn bản của một trang web."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
        resp = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        if resp.status_code != 200:
            logger.warning("HTTP %s for %s", resp.status_code, url)
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        # Xoá script, style, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Normalise whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) >= _MIN_CONTENT_LENGTH else None

    except Exception as exc:
        logger.warning("Scrape failed for %s: %s", url, exc)
        return None


def _extract_date(result: dict) -> str | None:
    """Lấy published_date từ kết quả Tavily nếu có."""
    return result.get("published_date") or result.get("published") or None


def search_sources(topic: str, learning_goal: str, max_sources: int = 8, is_cancelled=None) -> list[dict]:
    """
    Tìm và trả về danh sách nguồn thô (chưa chấm tin cậy).
    Hỗ trợ is_cancelled callback để dừng ngay tức khắc khi người dùng bấm dừng.
    """
    queries = _build_queries(topic, learning_goal)
    seen_urls: set[str] = set()
    sources: list[dict] = []

    for query in queries:
        if is_cancelled and is_cancelled():
            logger.info("search_sources: detected cancellation, stopping immediately.")
            break
        if len(sources) >= max_sources:
            break

        try:
            logger.info("Tavily search: %r", query)
            results = _tavily.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_raw_content=True,
            )
            for r in results.get("results", []):
                if is_cancelled and is_cancelled():
                    logger.info("search_sources: detected cancellation during results processing.")
                    return sources

                url = r.get("url", "")
                if not url or url in seen_urls or _is_blocked(url):
                    continue

                seen_urls.add(url)

                # Dùng raw_content từ Tavily nếu có, nếu không thì scrape
                raw = r.get("raw_content")
                if not raw:
                    if is_cancelled and is_cancelled():
                        return sources
                    raw = _scrape_content(url)

                if raw and len(raw) < _MIN_CONTENT_LENGTH:
                    raw = None

                sources.append(
                    {
                        "code": f"t{len(sources) + 1:02d}",
                        "url": url,
                        "title": r.get("title"),
                        "author": None,  # Tavily không trả author, trust_agent sẽ đoán
                        "published_date": _extract_date(r),
                        "domain": _domain_of(url),
                        "excerpt": (r.get("content") or "")[:800],
                        "raw_content": raw,
                    }
                )

                if len(sources) >= max_sources:
                    break

        except Exception as exc:
            logger.error("Tavily search error for query %r: %s", query, exc)
            continue

    logger.info("search_agent: found %d sources", len(sources))
    return sources
