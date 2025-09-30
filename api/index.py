from app import create_app

# Flaskアプリケーションを作成
app = create_app()

# Vercel用 - アプリをそのままエクスポート
# Vercelは自動的にWSGI互換のハンドラーを生成します