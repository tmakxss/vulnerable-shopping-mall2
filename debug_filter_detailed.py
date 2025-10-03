import re

def filter_dangerous_commands(command_str):
    """危険なコマンドをフィルタリングし、安全なコマンドのみ許可"""
    
    print(f"\n🔍 Debugging command: '{command_str}'")
    
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
            result = f"Dangerous pattern '{pattern}' detected and blocked."
            print(f"❌ {result}")
            return result
    
    # 改良版: コマンド分離でIPアドレスやホスト名を正しく処理
    import re
    
    # pingコマンドを特別処理（常に許可）
    if 'ping' in cmd_lower:
        print("✅ ping command detected - allowing")
        return None
    
    # &, ;, |, && で分割してコマンドを抽出
    commands = re.split(r'\s*[;&|]+\s*', command_str)
    print(f"📋 Split commands: {commands}")
    
    for i, cmd_part in enumerate(commands):
        cmd_part = cmd_part.strip()
        print(f"\n🔍 Processing part {i}: '{cmd_part}'")
        
        if not cmd_part:
            print("  ⏭️ Empty part, skipping")
            continue
        
        # 完全なコマンド部分をスキップするパターン
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # localhost（大文字小文字無視）の完全一致チェック  
        if cmd_part.lower() == 'localhost':
            print("  ✅ localhost recognized - skipping")
            continue
        
        if re.match(ip_pattern, cmd_part):
            print(f"  ✅ IP address '{cmd_part}' - skipping")
            continue
            
        if re.match(domain_pattern, cmd_part):
            print(f"  ✅ Domain name '{cmd_part}' - skipping")
            continue
        
        # 最初の単語をコマンド名として抽出
        words = cmd_part.split()
        if not words:
            print("  ⏭️ No words in part, skipping")
            continue
            
        first_word = words[0]
        cmd_name = first_word.lower()
        print(f"  🎯 First word: '{first_word}', cmd_name: '{cmd_name}'")
        
        # 数字や引数（-n 4など）もスキップ
        if cmd_name.startswith('-') or cmd_name.isdigit():
            print(f"  ⏭️ Argument or number '{cmd_name}' - skipping")
            continue
        
        # ホワイトリストチェック
        if cmd_name and not any(allowed == cmd_name for allowed in allowed_commands):
            result = f"Command '{cmd_name}' is not in whitelist."
            print(f"  ❌ {result}")
            return result
        else:
            print(f"  ✅ Command '{cmd_name}' is allowed")
    
    print("✅ All commands passed filter")
    return None  # 問題なし

# テスト
test_commands = [
    "localhost && tasklist",
    "127.0.0.1 & dir",
    "google.com; whoami"
]

for cmd in test_commands:
    result = filter_dangerous_commands(cmd)
    if result:
        print(f"❌ BLOCKED: {result}")
    else:
        print(f"✅ ALLOWED: Command would execute")
    print("-" * 50)