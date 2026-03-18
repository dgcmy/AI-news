@echo off
echo ================================================
echo  AI ニュースダイジェスト - セットアップ
echo ================================================
echo.

echo [1/3] Pythonパッケージをインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo エラー: pip install に失敗しました
    pause
    exit /b 1
)

echo.
echo [2/3] Playwright (日経新聞用ブラウザ) をインストール中...
playwright install chromium
if %errorlevel% neq 0 (
    echo 警告: Playwright のインストールに失敗しました
    echo 日経新聞のスクレイピングは無効になります
)

echo.
echo [3/3] 環境設定ファイルを確認中...
if not exist .env (
    copy .env.example .env
    echo .env ファイルを作成しました
    echo.
    echo !! 重要 !! .env ファイルを編集して以下を設定してください:
    echo   - ANTHROPIC_API_KEY: Anthropic APIキー (必須)
    echo   - NIKKEI_EMAIL: 日経新聞のメールアドレス (任意)
    echo   - NIKKEI_PASSWORD: 日経新聞のパスワード (任意)
    echo.
    echo 設定後、run.bat を実行してください
) else (
    echo .env ファイルは既に存在します
)

echo.
echo ================================================
echo  セットアップ完了！
echo  .env を設定後、run.bat を実行してください
echo ================================================
pause
