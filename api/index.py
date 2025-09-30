from app import create_app
import os

app = create_app()

# Vercel用のエントリーポイント
def handler(request):
    return app(request.environ, request.start_response)

# 通常のWSGI対応
if __name__ == '__main__':
    print("🔒 脆弱なショッピングモール - ウェブセキュリティ演習サイト")
    print("🌐 サーバー起動中...")
    print("⚠️  このサイトは学習目的のみで使用してください")
    
    # 環境に応じてポートを設定
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)