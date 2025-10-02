#!/usr/bin/env python3
"""
エンティティ検出による大文字変換のテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.main import partial_decode_for_xss

def test_entity_based_case_conversion():
    print("=== エンティティベース大文字変換テスト ===\n")
    
    test_cases = [
        # エンティティなし → 大文字変換されるべき（XSS失敗）
        ("<svg/onload=alert(1)>", True, "<SVG/ONLOAD=ALERT(1)>", "通常入力（XSS失敗）"),
        
        # エンティティあり → 大文字変換されない（XSS成功）
        ("<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>", False, "<svg/onload=alert(1)>", "数値文字参照（XSS成功）"),
        
        # HTMLエンティティあり → 大文字変換されない（XSS成功）
        ("&lt;script&gt;alert(1)&lt;/script&gt;", False, "<script>alert(1)</script>", "HTMLエンティティ（XSS成功）"),
    ]
    
    for input_text, should_uppercase, expected, description in test_cases:
        # エンティティ検出ロジック
        has_entities = ('&#' in input_text or '%26%23' in input_text or '&lt;' in input_text.lower() or '&gt;' in input_text.lower())
        
        # デコード
        decoded_item = partial_decode_for_xss(input_text)
        
        # 条件分岐
        if has_entities:
            final_item = decoded_item  # エンティティあり: 大文字変換なし
        else:
            final_item = ''.join(c.upper() if c.isalpha() else c for c in decoded_item)  # エンティティなし: 大文字変換
        
        status = "✅ OK" if final_item == expected else "❌ NG"
        print(f"{status} {description}")
        print(f"  入力: {input_text}")
        print(f"  エンティティ検出: {has_entities}")
        print(f"  デコード後: {decoded_item}")
        print(f"  最終結果: {final_item}")
        print(f"  期待値: {expected}")
        print()

if __name__ == "__main__":
    test_entity_based_case_conversion()