#!/usr/bin/env python3
"""
エンティティ検出による大文字変換のテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.main import partial_decode_for_xss

def test_entity_based_case_conversion():
    print("=== エンティティベース大文字変換テスト（1文字単位） ===\n")
    
    test_cases = [
        # エンティティなし → 大文字変換されるべき（XSS失敗）
        ("<svg/onload=alert(1)>", "<SVG/ONLOAD=ALERT(1)>", "通常入力（XSS失敗）"),
        
        # 数値文字参照 → エンティティからデコードされた文字のみ小文字保持（XSS成功）
        ("<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>", "<SVG/ONLOAD=alert(1)>", "数値文字参照（XSS成功）"),
        
        # HTMLエンティティ → エンティティからデコードされた文字のみ小文字
        ("&lt;script&gt;alert(1)&lt;/script&gt;", "<SCRIPT>ALERT(1)</SCRIPT>", "HTMLエンティティ（部分的変換免除）"),
    ]
    
    for input_text, expected, description in test_cases:
        # 新しい関数を直接呼び出し
        final_item = partial_decode_for_xss(input_text)
        
        status = "✅ OK" if final_item == expected else "❌ NG"
        print(f"{status} {description}")
        print(f"  入力: {input_text}")
        print(f"  最終結果: {final_item}")
        print(f"  期待値: {expected}")
        print()

if __name__ == "__main__":
    test_entity_based_case_conversion()