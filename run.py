from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🔒 脆弱なショッピングモール - ウェブセキュリティ演習サイト")
    print("🌐 サーバー起動中... http://localhost:5000")
    print("⚠️  このサイトは学習目的のみで使用してください")
    app.run(debug=True, host='0.0.0.0', port=5000) 