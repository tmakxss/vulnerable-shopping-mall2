def test_new_filter():
    # 新しいフィルターのテスト
    blocked_keywords = [
        'alert', 'script', 'prompt', 'confirm', 
        'console.log', '"', 'javascript:', 'eval',
        'document.', 'window.', 'on', '\\u',
        '<script', '</script>'
    ]
    
    test_payloads = [
        # ブロックされるべきもの
        "onclick=alert(1)",
        "onmouseover=alert(1)", 
        "onerror=alert(1)",
        "onload=alert(1)",
        "onauxclick=alert(1)",
        "\\u0061lert(1)",
        "j\\u0061vascript:alert(1)",
        "\\u006Fnerror=alert(1)",
        
        # 通るべきもの
        "この商品は素晴らしいです！",
        "購入してよかった商品です",
        "友人にもおすすめしたい商品",
        "価格も手頃で満足です",
    ]
    
    print("=== 新しいフィルターテスト (on + \\u ブロック) ===\n")
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"[テスト {i}] {payload}")
        
        payload_lower = payload.lower()
        blocked = False
        detected_keyword = None
        
        for keyword in blocked_keywords:
            if keyword in payload_lower:
                blocked = True
                detected_keyword = keyword
                break
        
        if blocked:
            print(f"🔴 BLOCKED (検出: {detected_keyword})")
        else:
            print("🟢 ALLOWED")
        print()

if __name__ == "__main__":
    test_new_filter()