#!/usr/bin/env python3
"""
アプリケーション初期化テスト
"""

try:
    from app import create_app
    
    print("✅ アプリケーション初期化テスト開始...")
    app = create_app()
    print("✅ Flaskアプリケーション作成成功")
    
    # ルート確認
    with app.app_context():
        print("✅ アプリケーションコンテキスト正常")
        
        # 基本的なテストリクエスト
        with app.test_client() as client:
            response = client.get('/health')
            print(f"✅ ヘルスチェック: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ レスポンス: {response.get_json()}")
            else:
                print(f"❌ エラーレスポンス: {response.data}")
    
except Exception as e:
    print(f"❌ アプリケーション初期化エラー: {e}")
    import traceback
    traceback.print_exc()