def test_on_filter():
    print("=== 'on' フィルター効果テスト ===\n")
    
    # テスト用コメント
    test_comments = [
        # ブロックされるべきもの（onを含む）
        "onclick=alert(1)",
        "onmouseover=alert(1)", 
        "onerror=alert(1)",
        "onload=alert(1)",
        "onchange=alert(1)",
        "onfocus=alert(1)",
        "onblur=alert(1)",
        "onsubmit=alert(1)",
        "onauxclick=alert(1)",  # 新しいイベント
        "onwheel=alert(1)",
        "ondrag=alert(1)",
        "ondrop=alert(1)",
        "onresize=alert(1)",
        "onscroll=alert(1)",
        "この商品はonline で購入できます",  # 誤検知の例
        "この商品はcoupon で安くなります",  # 誤検知の例
        "Nintendo Switch がおすすめです",   # 誤検知の例
        
        # エンコード回避試行
        "on&#99;lick=alert(1)",
        "&#111;nclick=alert(1)", 
        "o&#110;click=alert(1)",
        
        # 通るべきもの（onを含まない）
        "この商品は素晴らしいです",
        "購入してよかった商品です",
        "友人にもおすすめしたい",
        "コスパが最高です",
        "delivery が早かった",
        "amazing product!",
    ]
    
    blocked_keywords = [
        'alert', 'script', 'prompt', 'confirm', 
        'console.log', '"', 'javascript:', 'eval',
        'document.', 'window.', '<script', '</script>'
    ]
    
    for i, comment in enumerate(test_comments, 1):
        print(f"[テスト {i}] {comment}")
        
        comment_lower = comment.lower()
        blocked = False
        reason = ""
        
        # キーワードチェック
        for keyword in blocked_keywords:
            if keyword in comment_lower:
                blocked = True
                reason = keyword
                break
        
        # 'on' チェック
        if not blocked and 'on' in comment_lower:
            blocked = True
            reason = "on"
        
        if blocked:
            print(f"  🔴 BLOCKED (理由: {reason})")
        else:
            print(f"  ✅ ALLOWED")
        
        print()

if __name__ == "__main__":
    test_on_filter()
    
    print("=== 誤検知の影響 ===")
    false_positives = [
        "online", "coupon", "Nintendo", "iPhone", "Amazon", 
        "lemon", "melon", "salmon", "ribbon", "cotton",
        "according", "polygon", "nylon", "construction"
    ]
    
    print("以下の単語が誤検知される可能性があります:")
    for word in false_positives:
        if 'on' in word.lower():
            print(f"  - {word}")
            
    print("\n解決策:")
    print("1. より具体的なパターンマッチング（スペースや=を考慮）")
    print("2. HTMLパースして属性値のみチェック")
    print("3. ホワイトリスト方式の採用")