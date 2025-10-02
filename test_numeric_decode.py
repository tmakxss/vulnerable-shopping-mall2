#!/usr/bin/env python3
"""
数値文字参照のデコードテスト
"""
import re

def test_numeric_decode():
    print("=== 数値文字参照デコードテスト ===\n")
    
    # 16進数の数値文字参照
    test_cases = [
        "&#x61;",  # a (小文字)
        "&#x41;",  # A (大文字)
        "&#x6C;",  # l (小文字)
        "&#x4C;",  # L (大文字)
        "&#x65;",  # e (小文字)
        "&#x45;",  # E (大文字)
        "&#x72;",  # r (小文字)
        "&#x52;",  # R (大文字)
        "&#x74;",  # t (小文字)
        "&#x54;",  # T (大文字)
    ]
    
    for test in test_cases:
        # 現在の実装
        result = re.sub(r'&#[xX]([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), test)
        print(f"{test} → {result} (ASCII: {ord(result)})")
    
    print(f"\n=== フルテスト ===")
    full_test = "&#x61;&#x6C;&#x65;&#x72;&#x74;"  # alert
    result = re.sub(r'&#[xX]([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), full_test)
    print(f"{full_test} → {result}")

if __name__ == "__main__":
    test_numeric_decode()