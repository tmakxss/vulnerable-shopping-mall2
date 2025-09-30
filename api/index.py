import sys
import os

# パスを追加してアプリケーションをインポート可能にする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Flaskアプリケーションを作成
app = create_app()

# Vercel用のハンドラー関数
def handler(event, context):
    """
    Vercel用のAWS Lambda互換ハンドラー
    """
    return app

# デフォルトエクスポート（Vercelが自動検出）
application = app

if __name__ == "__main__":
    # ローカル開発用
    app.run(debug=True)