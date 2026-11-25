import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

def collect_items(feed_urls, limit=30):
    items = []
    seen = set()
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            summary = (entry.get("summary") or "").strip()
            key = link or title
            if not title or key in seen:
                continue
            seen.add(key)
            published = entry.get("published", "")
            try:
                dt = parsedate_to_datetime(published).astimezone(timezone.utc).isoformat()
            except Exception:
                dt = datetime.now(timezone.utc).isoformat()
            items.append({
                "title": title[:300],
                "summary": summary[:1200],
                "url": link,
                "published": dt,
                "source": feed.feed.get("title", url)
            })
    return items
