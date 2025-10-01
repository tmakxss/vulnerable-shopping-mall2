import requests

def test_review_search_xss_protection():
    """レビュー検索のXSS保護をテスト"""
    
    base_url = "http://localhost:5000"
    
    # XSSペイロードのテスト
    xss_payloads = [
        "<script>alert(1)</script>",
        "<iframe src=javascript:alert(1)>",
        "test>alert(1)",
        "test alert(1)",
        "test%26gt;alert(1)",
        "test%23script",
        "test&gt;alert(1)",
        "test#script",
    ]
    
    print("=== レビュー検索XSS保護テスト ===\n")
    
    for i, payload in enumerate(xss_payloads, 1):
        print(f"[テスト {i}] ペイロード: {payload}")
        
        try:
            # リクエスト送信
            response = requests.get(f"{base_url}/", params={'review_search': payload})
            
            print(f"   ステータス: {response.status_code}")
            
            # レスポンスでペイロードが反射されているかチェック
            if payload in response.text:
                print("   🔴 VULNERABLE - ペイロードが反射されています")
            else:
                print("   🟢 PROTECTED - ペイロードは反射されていません")
                
            # エラーメッセージが表示されているかチェック
            if "不正な検索クエリが検出されました" in response.text:
                print("   ✅ フィルターが作動しました")
            else:
                print("   ⚠️  フィルターが作動していない可能性があります")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ リクエストエラー: {e}")
        
        print()

def test_normal_search():
    """正常な検索のテスト"""
    
    base_url = "http://localhost:5000"
    normal_queries = ["honda", "toyota", "nissan", "car"]
    
    print("=== 正常な検索テスト ===\n")
    
    for query in normal_queries:
        try:
            response = requests.get(f"{base_url}/", params={'review_search': query})
            print(f"[正常] {query}: {response.status_code}")
            
            if "不正な検索クエリが検出されました" in response.text:
                print("   ⚠️  正常なクエリがブロックされています")
            else:
                print("   ✅ 正常に検索できました")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ エラー: {e}")

if __name__ == "__main__":
    print("サーバーが http://localhost:5000 で起動していることを確認してください。\n")
    test_review_search_xss_protection()
    print("\n" + "="*50 + "\n")
    test_normal_search()