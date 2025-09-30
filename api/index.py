from app import create_app
import os

# Flaskアプリケーションを作成
app = create_app()

# Vercel用のエントリーポイント（必須）
def handler(environ, start_response):
    return app(environ, start_response)

# デバッグ用のローカル実行
if __name__ == '__main__':
    print("🔒 脆弱なショッピングモール - ウェブセキュリティ演習サイト")
    print("🌐 サーバー起動中...")
    print("⚠️  このサイトは学習目的のみで使用してください")
    
    # 環境に応じてポートを設定
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)