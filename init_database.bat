@echo off
echo ========================================
echo 🗄️ Supabaseデータベース初期化
echo ========================================
echo.

echo 📋 設定確認:
echo   プロジェクト: afflutcsdwloxkdinhch
echo   URL: https://afflutcsdwloxkdinhch.supabase.co
echo   データベース: PostgreSQL
echo.

echo ⚠️ 実行前の確認:
echo   1. Vercelデプロイが完了していること
echo   2. 環境変数が正しく設定されていること
echo   3. Supabaseプロジェクトが起動していること
echo.

set /p confirm="データベース初期化を実行しますか？ (y/N): "
if /i "%confirm%" NEQ "y" (
    echo キャンセルされました。
    pause
    exit /b
)

echo.
echo 🚀 データベース初期化開始...

copy /Y .env.production .env
python database/init_supabase.py

echo.
echo ✅ データベース初期化完了！
echo.
echo 🌐 サイトURL確認:
echo   Vercel URL でサイトにアクセスして動作確認してください
echo.
echo 📊 確認項目:
echo   ✓ サイトが表示される
echo   ✓ セキュリティ警告バナーが表示される  
echo   ✓ ログイン機能が動作する
echo   ✓ 商品一覧が表示される
echo.

pause