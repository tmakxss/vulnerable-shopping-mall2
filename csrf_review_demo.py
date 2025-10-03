#!/usr/bin/env python3
"""
レビュー編集CSRF脆弱性デモンストレーション

この脆弱性の概要:
- レビュー編集でCSRFトークンによる保護あり
- ただし、任意のユーザーの有効なトークンが使用可能
- 攻撃者は自分のトークンでCSRF攻撃が実行可能
"""

def main():
    print("=== レビュー編集CSRF脆弱性デモ ===\n")
    
    print("脆弱性の詳細:")
    print("• CSRFトークンの検証が実装されている")
    print("• しかし、トークンの所有者を確認していない")
    print("• 任意のユーザーの有効なトークンで攻撃可能")
    print("• GETの権限昇格攻撃は無効（POSTのみ）")
    print()
    
    print("攻撃手順:")
    print("1. 攻撃者が通常ユーザーでログイン")
    print("2. /contact ページでCSRFトークンを取得")
    print("3. そのトークンを使用してCSRF攻撃HTMLを作成")
    print("4. 管理者にHTMLページを開かせる")
    print("5. レビューが攻撃者の意図通りに変更される")
    print()
    
    print("攻撃対象エンドポイント:")
    print("POST /admin/reviews/edit/[review_id]")
    print()
    
    print("必要なパラメータ:")
    print("• csrf_token: 任意のユーザーの有効なトークン")
    print("• rating: 1-5の評価値")
    print("• comment: 変更後のコメント")
    print()
    
    print("脆弱なコード部分:")
    print("```sql")
    print("SELECT COUNT(*) FROM csrf_tokens")
    print("WHERE token = %s AND is_used = 0")
    print("```")
    print("↑ user_id の確認なし")
    print()
    
    print("攻撃ペイロード例:")
    print("```html")
    print('<form action="/admin/reviews/edit/32" method="POST">')
    print('  <input type="hidden" name="csrf_token" value="[STOLEN_TOKEN]" />')
    print('  <input type="hidden" name="rating" value="1" />')
    print('  <input type="hidden" name="comment" value="CSRF攻撃成功！" />')
    print('</form>')
    print('<script>document.forms[0].submit();</script>')
    print("```")
    print()
    
    print("CSRFトークン取得方法:")
    print("1. 通常ユーザーでログイン")
    print("2. https://vulnerable-shopping-mall21.vercel.app/contact を開く")
    print("3. 開発者ツールでHTMLソースを確認")
    print("4. <input name=\"token\" value=\"...\"  の値をコピー")
    print()
    
    print("テスト手順:")
    print("1. csrf_review_attack.html のトークンを有効な値に変更")
    print("2. 管理者でブラウザを開く")
    print("3. csrf_review_attack.html を開く")
    print("4. レビュー管理画面で変更を確認")
    print()
    
    print("期待される結果:")
    print("• 管理者の知らない間にレビューが変更される")
    print("• 評価とコメントが攻撃者の指定した内容になる")
    print("• 正常な成功メッセージが表示される")
    print()
    
    print("修正方法:")
    print("• トークン検証時にuser_idも確認")
    print("• セッション内のトークンと照合")
    print("• リファラーチェックの追加")

if __name__ == "__main__":
    main()