def test_review_search_filter():
    """レビュー検索フィルターのテスト"""
    
    # ブロックキーワード
    review_search_blocked_keywords = [
        '>', ' ', '%26', '%23', '&', '#'
    ]
    
    test_payloads = [
        # ブロックされるべきもの
        "test>alert(1)",
        "test alert(1)",
        "test%26gt;alert(1)",
        "test%23script",
        "test&gt;alert(1)",
        "test#script",
        
        # 通るべきもの
        "honda",
        "nissan",
        "toyota",
        "bmw",
        "porsche",
        "review",
        "car",
        "speed",
    ]
    
    print("=== レビュー検索フィルターテスト ===\n")
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"[テスト {i}] {payload}")
        
        payload_lower = payload.lower()
        blocked = False
        detected_keyword = None
        
        for keyword in review_search_blocked_keywords:
            if keyword in payload_lower:
                blocked = True
                detected_keyword = keyword
                break
        
        if blocked:
            print(f"🔴 BLOCKED (検出: '{detected_keyword}')")
        else:
            print("🟢 ALLOWED")
        print()

def test_review_search_urls():
    """レビュー検索URLの例"""
    
    print("=== テスト用URL例 ===\n")
    
    blocked_urls = [
        "http://localhost:5000/?review_search=test>alert(1)",
        "http://localhost:5000/?review_search=test alert(1)",
        "http://localhost:5000/?review_search=test%26gt;alert(1)",
        "http://localhost:5000/?review_search=test%23script",
        "http://localhost:5000/?review_search=test&gt;alert(1)",
        "http://localhost:5000/?review_search=test#script",
    ]
    
    allowed_urls = [
        "http://localhost:5000/?review_search=honda",
        "http://localhost:5000/?review_search=nissan",
        "http://localhost:5000/?review_search=toyota",
        "http://localhost:5000/?review_search=bmw",
    ]
    
    print("🔴 ブロックされるURL:")
    for url in blocked_urls:
        print(f"   {url}")
    
    print("\n🟢 許可されるURL:")
    for url in allowed_urls:
        print(f"   {url}")

if __name__ == "__main__":
    test_review_search_filter()
    print("\n" + "="*50 + "\n")
    test_review_search_urls()