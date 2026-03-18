import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    def __init__(self, db_path: str = "data/news.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    summary TEXT,
                    published_at TEXT,
                    fetched_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS daily_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    articles_json TEXT NOT NULL,
                    generated_at TEXT DEFAULT (datetime('now', 'localtime'))
                );

                CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
                CREATE INDEX IF NOT EXISTS idx_daily_news_date ON daily_news(date);
            """)

    def save_articles(self, articles: List[Dict]):
        with self.get_connection() as conn:
            for article in articles:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO articles (title, url, source, summary, published_at) VALUES (?, ?, ?, ?, ?)",
                        (article.get("title"), article.get("url"), article.get("source"),
                         article.get("summary", ""), article.get("published_at", ""))
                    )
                except Exception as e:
                    print(f"DB save error: {e}")

    def save_daily_news(self, news_list: List[Dict]):
        today = date.today().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO daily_news (date, articles_json) VALUES (?, ?)",
                (today, json.dumps(news_list, ensure_ascii=False))
            )

    def get_today_news(self) -> Dict:
        today = date.today().isoformat()
        return self.get_news_by_date(today)

    def get_news_by_date(self, date_str: str) -> Dict:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT articles_json, generated_at FROM daily_news WHERE date = ? ORDER BY generated_at DESC LIMIT 1",
                (date_str,)
            ).fetchone()
            if row:
                return {
                    "articles": json.loads(row["articles_json"]),
                    "generated_at": row["generated_at"],
                    "date": date_str,
                }
            return {"articles": [], "generated_at": None, "date": date_str}

    def get_available_dates(self) -> List[str]:
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT date FROM daily_news ORDER BY date DESC LIMIT 30"
            ).fetchall()
            return [row["date"] for row in rows]
