import urllib.request
import urllib.parse

def test_comment_filter():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJxFjUEKwyAURK9SZu3CtJgEr9IEsfqlgkkhX1chd6-fLrp5M7xZzAmXiuc3MezzxK32ALcQiBkKS3to_xKmIAyzcOxmTikuzdy9FmMm4UT_bhLWa1VI7Hzc8g6bfGFSOD6FYNGYjn4g4XKEHX9995uslbgOWg-4vkqQM0Y.aNyEWw.WU_oe6wU6uh8fVnQR6l_FCRWEgA"
    
    # テスト用のペイロード
    test_comments = [
        # ブロックされるべきもの
        "この商品は最高です！<script>alert('XSS')</script>",
        "素晴らしい商品！alert(1)で確認できます",
        "おすすめです prompt('test') してください",
        "良い商品 confirm('buy') しましょう", 
        "デバッグ用 console.log('test') です",
        'この商品には"価値"があります',
        "javascript:alert(1) 素晴らしい",
        "document.cookie を確認してください",
        
        # 通るべきもの
        "この商品は本当に素晴らしいです！",
        "購入してよかった商品です",
        "友人にもおすすめしたい商品",
        "コスパが最高の商品です",
    ]
    
    print("=== レビューコメント フィルタリングテスト ===\n")
    
    for i, comment in enumerate(test_comments, 1):
        print(f"[テスト {i}] コメント: {comment[:50]}...")
        
        # POSTデータを準備
        data = urllib.parse.urlencode({
            'rating': '5',
            'comment': comment
        }).encode('utf-8')
        
        # リクエスト作成
        req = urllib.request.Request(
            "http://localhost:5000/product/1/review",
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookie
            },
            method='POST'
        )
        
        try:
            # リダイレクトを追跡してレスポンスを取得
            response = urllib.request.urlopen(req)
            content = response.read().decode('utf-8')
            
            # フラッシュメッセージを確認
            if '禁止された文字列' in content:
                print("🔴 BLOCKED: 禁止された文字列が検出されました")
            elif 'レビューを投稿しました' in content:
                print("✅ ALLOWED: コメントが正常に投稿されました")
            elif 'エラーが発生しました' in content:
                print("⚠️ ERROR: 投稿中にエラーが発生")
            else:
                print("❓ UNKNOWN: 結果が不明")
                
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("↩️ REDIRECT: リダイレクト応答")
            else:
                print(f"❌ HTTP ERROR: {e.code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()

if __name__ == "__main__":
    test_comment_filter()