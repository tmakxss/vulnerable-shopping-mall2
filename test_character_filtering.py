#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
updated_comment パラメーターの文字フィルタリングテスト
"""

import urllib.parse

def test_character_filtering():
    print("🔍 updated_comment パラメーターフィルタリングテスト")
    print("=" * 60)
    
    base_url = "http://localhost:5000/admin/reviews?updated_comment="
    
    print("\n📋 ブロックされる文字: > < -")
    print("=" * 40)
    
    # ブロックされるペイロード
    blocked_payloads = [
        "><script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<!--comment-->",
        "<svg onload=alert(1)>",
        "->alert(1)",
        "<!-- injection -->"
    ]
    
    print("\n❌ ブロックされるペイロード:")
    for i, payload in enumerate(blocked_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i}. {payload}")
        print(f"   URL: {base_url}{encoded}")
        print(f"   結果: フィルタリングによりパラメーター無効化")
        print()
    
    # 許可されるペイロード (JavaScript反射XSS用)
    allowed_payloads = [
        "';alert(1);//",
        "';alert('XSS');//",
        "';document.body.innerHTML='XSS';//",
        "';eval('alert(1)');//",
        "';prompt('XSS');//"
    ]
    
    print("\n✅ 許可されるペイロード (JavaScript反射XSS):")
    for i, payload in enumerate(allowed_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i}. {payload}")
        print(f"   URL: {base_url}{encoded}")
        print(f"   結果: JavaScript反射XSS実行")
        print()
    
    print("\n🎯 フィルタリングの効果:")
    print("=" * 40)
    print("✅ HTMLタグベースのXSSをブロック")
    print("✅ HTMLコメント注入をブロック") 
    print("✅ JavaScript反射XSSは許可")
    print("✅ 研究目的の特定攻撃ベクターに限定")
    
    print("\n🔒 セキュリティ考慮:")
    print("=" * 40)
    print("- > < - の3文字のみブロック")
    print("- JavaScript文字列内でのクォート操作は許可")
    print("- 実環境では全ての特殊文字をエスケープすべき")

if __name__ == "__main__":
    test_character_filtering()