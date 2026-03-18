import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

load_dotenv()

from database import Database
from scheduler import NewsScheduler

app = FastAPI(title="AI News Aggregator")
db = Database()
scheduler_instance: NewsScheduler = None


@app.on_event("startup")
async def startup_event():
    global scheduler_instance
    db.initialize()
    scheduler_instance = NewsScheduler(db)
    scheduler_instance.start()

    # 今日のニュースがなければ即取得
    today_news = db.get_today_news()
    if not today_news["articles"]:
        print("本日のニュースなし - 自動取得を開始します...")
        scheduler_instance.trigger_fetch()


@app.on_event("shutdown")
async def shutdown_event():
    if scheduler_instance:
        scheduler_instance.stop()


@app.get("/api/news")
async def get_news(date: str = None):
    if date:
        data = db.get_news_by_date(date)
    else:
        data = db.get_today_news()
    return data


@app.get("/api/refresh")
async def refresh_news():
    if not scheduler_instance:
        raise HTTPException(status_code=503, detail="Scheduler not ready")
    if scheduler_instance.is_running:
        return {"status": "running", "message": "既に取得中です。しばらくお待ちください。"}
    ok = scheduler_instance.trigger_fetch()
    if ok:
        return {"status": "started", "message": "ニュースの取得を開始しました（数分かかります）"}
    return {"status": "busy", "message": "既に処理中です"}


@app.get("/api/status")
async def get_status():
    return {
        "is_running": scheduler_instance.is_running if scheduler_instance else False,
    }


@app.get("/api/dates")
async def get_dates():
    return {"dates": db.get_available_dates()}


# 静的ファイル（フロントエンド）- 最後にマウント
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"サーバー起動: http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
