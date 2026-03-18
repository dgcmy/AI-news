import asyncio
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import os


RSS_FEEDS = [
    # 海外
    {"name": "TechCrunch AI",  "url": "https://techcrunch.com/category/artificial-intelligence/feed/",          "source": "TechCrunch"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/",                              "source": "VentureBeat"},
    {"name": "The Verge AI",   "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",      "source": "The Verge"},
    {"name": "MIT Tech Review","url": "https://feeds.technologyreview.com/technology_review-rss_feed.xml",      "source": "MIT Technology Review"},
    {"name": "Wired AI",       "url": "https://www.wired.com/feed/category/artificial-intelligence/latest/rss", "source": "Wired"},
    {"name": "ArsTechnica",    "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",               "source": "Ars Technica"},
    # 国内（日本語）
    {"name": "ITmedia AI+",    "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",                          "source": "ITmedia AI+"},
    {"name": "ZDNet Japan",    "url": "https://japan.zdnet.com/rss/all/",                                       "source": "ZDNet Japan"},
    {"name": "ASCII.jp",       "url": "https://ascii.jp/rss.xml",                                               "source": "ASCII.jp"},
    {"name": "Impress Watch",  "url": "https://www.watch.impress.co.jp/data/rss/1.0/ict/feed.rdf",             "source": "Impress Watch"},
    {"name": "Ledge.ai",       "url": "https://ledge.ai/feed/",                                                 "source": "Ledge.ai"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def scrape_rss_feeds() -> List[Dict]:
    articles = []
    for feed_config in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])
            for entry in feed.entries[:15]:
                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()
                if title and url:
                    summary = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()[:400]
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": feed_config["source"],
                        "summary": summary,
                        "published_at": entry.get("published", ""),
                    })
            print(f"  {feed_config['source']}: {len(feed.entries)} 件取得")
        except Exception as e:
            print(f"  {feed_config['name']} エラー: {e}")
    return articles


def scrape_openai_news() -> List[Dict]:
    articles = []
    try:
        resp = requests.get("https://openai.com/news", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a[href*='/index/'], a[href*='/blog/'], a[href*='/research/']")
            seen = set()
            for link in links[:8]:   # 8件に制限
                href = link.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)
                title_el = link.select_one("h2, h3, [class*='title'], [class*='heading']")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                title = title.strip()
                if title and len(title) > 10:
                    url = f"https://openai.com{href}" if href.startswith("/") else href
                    date_str = ""
                    time_el = link.find_parent().find("time") if link.find_parent() else None
                    if time_el:
                        date_str = time_el.get("datetime", time_el.get_text(strip=True))
                    articles.append({"title": title, "url": url, "source": "OpenAI", "summary": "", "published_at": date_str})
            print(f"  OpenAI: {len(articles)} 件取得")
    except Exception as e:
        print(f"  OpenAI エラー: {e}")
    return articles


def scrape_anthropic_news() -> List[Dict]:
    articles = []
    try:
        resp = requests.get("https://www.anthropic.com/news", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a[href*='/news/']")
            seen = set()
            for link in links[:8]:   # 多すぎるので8件に制限
                href = link.get("href", "")
                if not href or href in seen or href == "/news" or href == "/news/":
                    continue
                seen.add(href)
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    url = f"https://www.anthropic.com{href}" if href.startswith("/") else href
                    # 日付を取得（<time>タグ or テキスト中の日付）
                    date_str = ""
                    time_el = link.find_parent().find("time") if link.find_parent() else None
                    if time_el:
                        date_str = time_el.get("datetime", time_el.get_text(strip=True))
                    articles.append({"title": title, "url": url, "source": "Anthropic", "summary": "", "published_at": date_str})
            print(f"  Anthropic: {len(articles)} 件取得")
    except Exception as e:
        print(f"  Anthropic エラー: {e}")
    return articles


def scrape_google_deepmind() -> List[Dict]:
    articles = []
    try:
        resp = requests.get("https://deepmind.google/discover/blog/", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a[href*='/blog/']")
            seen = set()
            for link in links[:15]:
                href = link.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)
                title_el = link.select_one("h2, h3, [class*='title']")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    title = link.get_text(strip=True)
                if title and len(title) > 10:
                    url = f"https://deepmind.google{href}" if href.startswith("/") else href
                    articles.append({"title": title, "url": url, "source": "Google DeepMind", "summary": "", "published_at": ""})
            print(f"  Google DeepMind: {len(articles)} 件取得")
    except Exception as e:
        print(f"  Google DeepMind エラー: {e}")
    return articles


def scrape_meta_ai() -> List[Dict]:
    articles = []
    try:
        resp = requests.get("https://ai.meta.com/blog/", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a[href*='/blog/']")
            seen = set()
            for link in links[:15]:
                href = link.get("href", "")
                if not href or href in seen or href == "/blog/":
                    continue
                seen.add(href)
                title_el = link.select_one("h2, h3, [class*='title']")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                if title and len(title) > 10:
                    url = f"https://ai.meta.com{href}" if href.startswith("/") else href
                    articles.append({"title": title, "url": url, "source": "Meta AI", "summary": "", "published_at": ""})
            print(f"  Meta AI: {len(articles)} 件取得")
    except Exception as e:
        print(f"  Meta AI エラー: {e}")
    return articles


async def scrape_nikkei() -> List[Dict]:
    """日経新聞をPlaywrightでスクレイピング（要ログイン）"""
    email = os.getenv("NIKKEI_EMAIL", "").strip()
    password = os.getenv("NIKKEI_PASSWORD", "").strip()

    if not email or not password:
        print("  日経新聞: 認証情報未設定のためスキップ")
        return []

    articles = []
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=HEADERS["User-Agent"])
            page = await context.new_page()

            # ログイン
            print("  日経新聞: ログイン中...")
            await page.goto("https://www.nikkei.com/", timeout=30000)
            await page.wait_for_timeout(2000)

            # ログインボタンを探す
            login_selectors = [
                "a:has-text('ログイン')",
                "[class*='login']",
                "a[href*='login']",
            ]
            logged_in = False
            for sel in login_selectors:
                try:
                    await page.click(sel, timeout=5000)
                    await page.wait_for_timeout(2000)
                    break
                except:
                    continue

            # メールとパスワードを入力
            try:
                await page.fill("input[type='email'], input[name='email']", email, timeout=10000)
                await page.fill("input[type='password'], input[name='password']", password, timeout=5000)
                await page.click("button[type='submit'], input[type='submit']", timeout=5000)
                await page.wait_for_timeout(3000)
                logged_in = True
                print("  日経新聞: ログイン成功")
            except Exception as e:
                print(f"  日経新聞: ログイン失敗 - {e}")

            # AI関連ニュースを検索
            search_queries = ["AI", "人工知能", "生成AI"]
            for query in search_queries:
                try:
                    search_url = f"https://www.nikkei.com/search?query={query}&type=news"
                    await page.goto(search_url, timeout=30000)
                    await page.wait_for_timeout(2000)

                    soup = BeautifulSoup(await page.content(), "html.parser")

                    # 記事リンクを抽出（複数のセレクターを試す）
                    selectors = [
                        "a[href*='/article/']",
                        "[class*='article'] a",
                        "[class*='news-item'] a",
                        "[class*='result'] a",
                    ]
                    for sel in selectors:
                        links = soup.select(sel)
                        for link in links[:10]:
                            href = link.get("href", "")
                            title = link.get_text(strip=True)
                            if href and title and len(title) > 8 and "/article/" in href:
                                url = f"https://www.nikkei.com{href}" if href.startswith("/") else href
                                articles.append({
                                    "title": title,
                                    "url": url,
                                    "source": "日経新聞",
                                    "summary": "",
                                    "published_at": "",
                                })
                        if articles:
                            break

                    if articles:
                        break
                except Exception as e:
                    print(f"  日経新聞 検索エラー ({query}): {e}")

            await browser.close()
            print(f"  日経新聞: {len(articles)} 件取得")

    except ImportError:
        print("  日経新聞: Playwright未インストール - setup.bat を実行してください")
    except Exception as e:
        print(f"  日経新聞 エラー: {e}")

    return articles


async def scrape_all() -> List[Dict]:
    """全ソースからニュースを取得"""
    print("ニュースソースからデータ取得中...")

    articles = []

    # 同期スクレイパー
    articles.extend(scrape_rss_feeds())
    articles.extend(scrape_openai_news())
    articles.extend(scrape_anthropic_news())
    articles.extend(scrape_google_deepmind())
    articles.extend(scrape_meta_ai())

    # 非同期スクレイパー（Playwright）
    nikkei_articles = await scrape_nikkei()
    articles.extend(nikkei_articles)

    # URLで重複排除
    seen_urls = set()
    unique_articles = []
    for article in articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    print(f"合計: {len(unique_articles)} 件（重複排除後）")
    return unique_articles
