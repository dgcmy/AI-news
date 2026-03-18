# AI News

AI 関連ニュースを自動収集し、日次で整理して表示する FastAPI アプリです。  
複数の RSS フィードや各社のニュースページから記事を集め、Claude を使って重要度順に並べ替えたうえで、ブラウザで見やすく表示します。

## 主な機能

- AI 関連ニュースの自動収集
- OpenAI、Anthropic、Google DeepMind、Meta AI などの公式ニュース取得
- TechCrunch、VentureBeat、The Verge、MIT Technology Review などの RSS 取得
- 日本語ニュースソースの収集
- Claude による上位ニュースの選定と要約
- FastAPI ベースのシンプルな Web UI
- APScheduler による毎朝 7:00 JST の定期実行
- 手動更新 API と日付別の閲覧機能

## 技術スタック

- Python
- FastAPI
- APScheduler
- Requests / BeautifulSoup / feedparser
- Playwright
- Anthropic API
- SQLite

## ディレクトリ構成

```text
AI news/
├─ app.py            # FastAPI アプリ本体
├─ scraper.py        # ニュース収集
├─ classifier.py     # Claude による選定・要約
├─ scheduler.py      # 定期実行
├─ database.py       # SQLite 保存処理
├─ static/
│  └─ index.html     # フロントエンド
├─ data/
│  └─ news.db        # SQLite データベース
├─ requirements.txt
├─ setup.bat
└─ run.bat
```

## セットアップ

### 1. リポジトリを取得

```bash
git clone https://github.com/dgcmy/AI-news.git
cd AI-news
```

### 2. 依存関係をインストール

Windows では `setup.bat` を使うのが簡単です。

```bat
setup.bat
```

手動で行う場合:

```bash
pip install -r requirements.txt
playwright install chromium
```

## 環境変数

`.env.example` をもとに `.env` を作成し、必要な値を設定してください。

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NIKKEI_EMAIL=your_email_here
NIKKEI_PASSWORD=your_password_here
PORT=8080
```

### 各項目

- `ANTHROPIC_API_KEY`
  Claude でニュースを選定・要約するために必要です。

- `NIKKEI_EMAIL`
- `NIKKEI_PASSWORD`
  日経サイトの追加取得に使います。未設定でもアプリは動作しますが、日経ニュースの収集はスキップされます。

- `PORT`
  Web サーバーのポート番号です。省略時は `8080` です。

## 起動方法

Windows:

```bat
run.bat
```

または直接実行:

```bash
python app.py
```

起動後、ブラウザで以下を開きます。

[http://localhost:8080](http://localhost:8080)

## 動作の流れ

1. スクレイパーが各ニュースソースから記事を収集
2. 重複 URL を除外
3. Claude が重要ニュースを選定し、日本語タイトル・要約を生成
4. 結果を SQLite に保存
5. フロントエンドで日付ごとに表示

起動時に当日のニュースが存在しなければ、自動で初回取得を行います。  
また、スケジューラが毎朝 7:00 JST に自動取得を実行します。

## API

### `GET /api/news`

当日のニュースを返します。

### `GET /api/news?date=YYYY-MM-DD`

指定日のニュースを返します。

### `GET /api/refresh`

ニュースの手動取得を開始します。

### `GET /api/status`

現在の取得処理の実行状態を返します。

### `GET /api/dates`

保存済みの日付一覧を返します。

## 注意点

- Anthropic API キーがない場合、Claude による分類は失敗しますが、フォールバックで最低限の表示は行われます。
- 一部サイトは HTML 構造の変更によって取得できなくなることがあります。
- Playwright が使えない環境では、日経の取得はスキップされます。
- 取得先の利用規約や robots.txt には注意してください。

## ライセンス

必要に応じて追記してください。
