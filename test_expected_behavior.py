#!/usr/bin/env python3
"""
大文字小文字の期待動作テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.main import partial_decode_for_xss

def test_expected_behavior():
    print("=== 期待動作テスト ===\n")
    
    test_cases = [
        # 数値文字参照から小文字へ
        ("<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>", 
         "<svg/onload=alert(1)>", 
         "数値文字参照デコード（小文字）"),
        
        # 通常のタグは保持
        ("<svg/onload=alert(1)>", 
         "<svg/onload=alert(1)>", 
         "通常のタグ（小文字保持）"),
         
        # 大文字のタグも保持
        ("<SVG/ONLOAD=ALERT(1)>", 
         "<SVG/ONLOAD=ALERT(1)>", 
         "通常のタグ（大文字保持）"),
         
        # 混合ケース
        ("<ScRiPt>aLeRt(1)</ScRiPt>", 
         "<ScRiPt>aLeRt(1)</ScRiPt>", 
         "混合大文字小文字保持"),
    ]
    
    for input_text, expected, description in test_cases:
        result = partial_decode_for_xss(input_text)
        status = "✅ OK" if result == expected else "❌ NG"
        print(f"{status} {description}")
        print(f"  入力: {input_text}")
        print(f"  期待: {expected}")
        print(f"  結果: {result}")
        print()

if __name__ == "__main__":
    test_expected_behavior()