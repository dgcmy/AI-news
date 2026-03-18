import asyncio
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from database import Database
from scraper import scrape_all
from classifier import NewsClassifier


class NewsScheduler:
    def __init__(self, db: Database):
        self.db = db
        self.classifier = NewsClassifier()
        self.scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
        self.is_running = False
        self._lock = threading.Lock()

    def start(self):
        # 毎朝7時（日本時間）に自動更新
        self.scheduler.add_job(
            self._run_fetch_thread,
            CronTrigger(hour=7, minute=0, timezone="Asia/Tokyo"),
            id="daily_news",
            name="Daily AI News",
            replace_existing=True,
        )
        self.scheduler.start()
        print("スケジューラー起動 - 毎朝7:00 JST に自動更新")

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def trigger_fetch(self):
        """手動でフェッチをトリガー（別スレッドで実行）"""
        if self.is_running:
            print("既にフェッチ中です")
            return False
        thread = threading.Thread(target=self._run_fetch_thread, daemon=True)
        thread.start()
        return True

    def _run_fetch_thread(self):
        """スレッド内でasyncioを実行"""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True

        try:
            asyncio.run(self._async_fetch())
        except Exception as e:
            print(f"フェッチエラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False

    async def _async_fetch(self):
        print(f"\n{'='*50}")
        print(f"ニュース取得開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*50)

        # スクレイピング
        articles = await scrape_all()
        if not articles:
            print("記事が取得できませんでした")
            return

        # DBに生記事を保存
        self.db.save_articles(articles)

        # Claudeでトップ10を選択
        top_news = self.classifier.select_top_ai_news(articles)
        if not top_news:
            print("ニュース選択に失敗しました")
            return

        # 本日の選択結果を保存
        self.db.save_daily_news(top_news)
        print(f"完了: {len(top_news)} 件のニュースを保存")
        print('='*50)
