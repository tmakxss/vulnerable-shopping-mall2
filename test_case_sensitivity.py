#!/usr/bin/env python3
"""
XSS大文字小文字保持テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.main import partial_decode_for_xss

def test_case_sensitivity():
    print("=== XSS大文字小文字保持テスト ===\n")
    
    test_cases = [
        # HTMLエンティティテスト（数値文字参照）
        ("<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>", 
         "<svg/onload=alert(1)>"),
        
        # 通常のHTMLタグ（大文字小文字保持）
        ("<SVG/ONLOAD=ALERT(1)>", "<SVG/ONLOAD=ALERT(1)>"),
        ("<svg/onload=alert(1)>", "<svg/onload=alert(1)>"),
        ("<ScRiPt>alert(1)</ScRiPt>", "<ScRiPt>alert(1)</ScRiPt>"),
        
        # HTMLエンティティ（&lt; &gt;）
        ("&lt;script&gt;alert(1)&lt;/script&gt;", "<script>alert(1)</script>"),
        ("&lt;script&gt;ALERT(1)&lt;/script&gt;", "<script>ALERT(1)</script>"),
        ("&LT;SCRIPT&GT;ALERT(1)&LT;/SCRIPT&GT;", "<SCRIPT>ALERT(1)</SCRIPT>"),
        
        # 混合テスト
        ("&lt;SVG/ONLOAD=ALERT(1)&gt;", "<SVG/ONLOAD=ALERT(1)>"),
    ]
    
    for input_text, expected in test_cases:
        result = partial_decode_for_xss(input_text)
        status = "✅ OK" if result == expected else "❌ NG"
        print(f"{status}")
        print(f"  入力: {input_text}")
        print(f"  期待: {expected}")
        print(f"  結果: {result}")
        print()

if __name__ == "__main__":
    test_case_sensitivity()