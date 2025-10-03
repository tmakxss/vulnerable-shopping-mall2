import sys
import os

# パスを追加してapp.routes.adminをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 実際のadmin.pyからフィルタリング関数を抽出してテスト
import re

def filter_dangerous_commands(command_str):
    """危険なコマンドをフィルタリングし、安全なコマンドのみ許可"""
    
    # 許可されるコマンドのホワイトリスト（Windows + Linux両対応）
    allowed_commands = [
        'dir', 'ls', 'whoami', 'id', 'pwd', 'echo', 'date', 'time',
        'hostname', 'uname', 'ping', 'tracert', 'traceroute', 'nslookup',
        'systeminfo', 'ver', 'cat', 'head', 'tail', 'wc', 'grep',
        'find', 'locate', 'which', 'where', 'type', 'ps', 'top',
        'tasklist', 'tree', 'ipconfig', 'arp', 'netstat', 'vol',
        'fsutil', 'wmic', 'sc', 'reg'  # Windows特有コマンドを追加
    ]
    
    # 危険なパターンの直接チェック
    cmd_lower = command_str.lower()
    dangerous_patterns = [
        'rm -rf', 'del /s', 'format c:', 'shutdown', 'reboot',
        'python -c', 'powershell -c', 'cmd /c', 'bash -c',
        'curl http', 'wget http', 'certutil -url', 'msiexec'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in cmd_lower:
            return f"Dangerous pattern '{pattern}' detected and blocked."
    
    # 改良版: コマンド分離でIPアドレスやホスト名を正しく処理
    import re
    
    # pingコマンドを特別処理（常に許可）
    if 'ping' in cmd_lower:
        return None
    
    # &, ;, |, && で分割してコマンドを抽出
    commands = re.split(r'\s*[;&|]+\s*', command_str)
    
    for cmd_part in commands:
        cmd_part = cmd_part.strip()
        if not cmd_part:
            continue
        
        # 完全なコマンド部分をスキップするパターン
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # localhost（大文字小文字無視）の完全一致チェック  
        if cmd_part.lower() == 'localhost':
            continue
        
        if re.match(ip_pattern, cmd_part) or re.match(domain_pattern, cmd_part):
            continue  # IPアドレスやドメイン名はスキップ
        
        # 最初の単語をコマンド名として抽出
        words = cmd_part.split()
        if not words:
            continue
            
        first_word = words[0]
        cmd_name = first_word.lower()
        
        # 数字や引数（-n 4など）もスキップ
        if cmd_name.startswith('-') or cmd_name.isdigit():
            continue
        
        # ホワイトリストチェック
        if cmd_name and not any(allowed == cmd_name for allowed in allowed_commands):
            return f"Command '{cmd_name}' is not in whitelist."
    
    return None  # 問題なし

def run_test():
    """テスト実行"""
    print("🧪 Testing Real Admin Filter Function")
    print("=" * 40)
    
    test_cases = [
        ("ping -n 4 127.0.0.1 & dir", True),
        ("127.0.0.1 & dir", True),
        ("google.com; whoami", True),
        ("localhost && tasklist", True),  # これが通るはず
        ("8.8.8.8 | systeminfo", True),
        ("example.com & hostname", True),
        ("ping google.com; dir", True),
        ("dangerous_command & dir", False),
        ("python -c print('hello')", False)
    ]
    
    for i, (cmd, should_pass) in enumerate(test_cases, 1):
        result = filter_dangerous_commands(cmd)
        passed = result is None
        
        print(f"{i}. Testing: '{cmd}'")
        
        if passed == should_pass:
            if passed:
                print("   ✅ Allowed: Command would execute")
            else:
                print(f"   ❌ Blocked: {result}")
        else:
            print(f"   🚨 UNEXPECTED: Expected {'allow' if should_pass else 'block'}, got {'allow' if passed else 'block'}")
            if result:
                print(f"   Error: {result}")
        print()

if __name__ == "__main__":
    run_test()