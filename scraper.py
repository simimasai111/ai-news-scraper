import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

API_URL = "https://baipiao.org/api/ainews/items"
DATA_FILE = "news_data.json"
LIMIT = 30
BEIJING = timezone(timedelta(hours=8))

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def fetch_first_page():
    """用 curl 抓取第一页（只取最新 30 条，不翻页），绕过 Cloudflare"""
    headers = [
        "-H", f"User-Agent: {UA}",
        "-H", "Accept: application/json",
        "-H", "Referer: https://baipiao.org/news/",
    ]
    url = f"{API_URL}?mode=all&limit={LIMIT}"
    proc = subprocess.run(["curl", "-s", "--max-time", "60", *headers, url],
                          capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("curl 失败: " + (proc.stderr or b"").decode(errors="replace")[-500:])
    data = json.loads(proc.stdout.decode("utf-8"))
    return data.get("items", [])


def format_date(iso_str):
    """2026-08-02T13:58:42.000Z -> 2026年8月2日13时58分（北京时间）"""
    if not iso_str:
        return ""
    s = str(iso_str).replace("Z", "+00:00")
    dt = datetime.fromisoformat(s).astimezone(BEIJING)
    return f"{dt.year}年{dt.month}月{dt.day}日{dt.hour}时{dt.minute}分"


def main():
    items = fetch_first_page()
    print(f"抓到第一页 {len(items)} 条")

    existing = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing = {it["id"]: it for it in json.load(f)}

    new_items = []
    for it in items:
        if it["id"] in existing:
            continue
        rec = {
            "id": it["id"],
            "title": it.get("title"),
            "url": it.get("url"),
            "summary": it.get("summary"),
            "source": it.get("source"),
            "date": format_date(it.get("publishedAt")),
        }
        existing[rec["id"]] = rec
        new_items.append(rec)

    merged = list(existing.values())
    merged.sort(key=lambda x: x.get("date", ""), reverse=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"新增 {len(new_items)} 条，累计 {len(merged)} 条")
    for it in new_items:
        print(f"  [{it['date']}] {it['title']} -> {it['url']}")


if __name__ == "__main__":
    main()
