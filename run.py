from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🔒 脆弱なショッピングモール - ウェブセキュリティ演習サイト")
    print("🌐 サーバー起動中... http://localhost:8000")
    print("⚠️  このサイトは学習目的のみで使用してください")
    app.run(host='0.0.0.0', port=8000, debug=True) 