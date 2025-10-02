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
        ("<svg/onload=alert(1)>", "<SVG/ONLOAD=ALERT(1)>", "通常入力（XSS失敗）"),
        
        # 数値文字参照 → 大文字変換されない（XSS成功）
        ("<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>", "<svg/onload=alert(1)>", "数値文字参照（XSS成功）"),
        
        # HTMLエンティティ → デコード後に大文字変換される（期待される動作）
        ("&lt;script&gt;alert(1)&lt;/script&gt;", "<SCRIPT>ALERT(1)</SCRIPT>", "HTMLエンティティ（デコード後大文字変換）"),
    ]
    
    for input_text, expected, description in test_cases:
        # デコード
        decode_result = partial_decode_for_xss(input_text)
        decoded_text = decode_result['text']
        has_numeric_entities = decode_result['has_numeric_entities']
        has_html_entities = decode_result['has_html_entities']
        
        # 条件分岐
        if has_numeric_entities:
            final_item = decoded_text  # 数値文字参照: 大文字変換なし
        elif has_html_entities:
            final_item = ''.join(c.upper() if c.isalpha() else c for c in decoded_text)  # HTMLエンティティ: デコード後大文字変換
        else:
            final_item = ''.join(c.upper() if c.isalpha() else c for c in decoded_text)  # エンティティなし: 大文字変換
        
        status = "✅ OK" if final_item == expected else "❌ NG"
        print(f"{status} {description}")
        print(f"  入力: {input_text}")
        print(f"  数値文字参照: {has_numeric_entities}, HTMLエンティティ: {has_html_entities}")
        print(f"  デコード後: {decoded_text}")
        print(f"  最終結果: {final_item}")
        print(f"  期待値: {expected}")
        print()

if __name__ == "__main__":
    test_entity_based_case_conversion()