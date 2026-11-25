import feedparser
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def traffic_to_number(value):
    """
    Converte estimativas do Google Trends em números.
    Exemplos: 200+ -> 200; 5K+ -> 5000; 1M+ -> 1000000.
    """
    if not value:
        return 0

    value = str(value).strip().upper().replace(",", "")

    match = re.search(r"(\d+(?:\.\d+)?)\s*([KM]?)", value)

    if not match:
        return 0

    number = float(match.group(1))
    suffix = match.group(2)

    if suffix == "K":
        number *= 1000
    elif suffix == "M":
        number *= 1000000

    return int(number)


def get_published_date(entry):
    for field in ("published", "updated"):
        value = entry.get(field)

        if value:
            try:
                return parsedate_to_datetime(value).astimezone(
                    timezone.utc
                )
            except Exception:
                pass

    return datetime.min.replace(tzinfo=timezone.utc)


def collect_items(feed_urls, limit=30):
    items = []
    seen = set()

    for url in feed_urls:
        try:
            feed = feedparser.parse(
                url,
                request_headers={"User-Agent": "Mozilla/5.0"}
            )

            for entry in feed.entries[:limit]:
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                summary = (entry.get("summary") or "").strip()

                key = link or title

                if not title or key in seen:
                    continue

                seen.add(key)

                published_date = get_published_date(entry)

                traffic = traffic_to_number(
                    entry.get("ht_approx_traffic", "")
                )

                items.append({
                    "title": title[:300],
                    "summary": summary[:1200],
                    "url": link,
                    "published": (
                        published_date.isoformat()
                        if published_date.year > 1
                        else ""
                    ),
                    "source": feed.feed.get("title", url),
                    "traffic": traffic
                })

        except Exception as error:
            print(f"Aviso: falha ao consultar {url}: {error}")

    # Primeiro, tendências com maior volume de pesquisa.
    # Em seguida, notícias mais recentes.
    items.sort(
        key=lambda item: (
            item["traffic"],
            item["published"]
        ),
        reverse=True
    )

    print(f"Total de pautas coletadas: {len(items)}")

    return items
