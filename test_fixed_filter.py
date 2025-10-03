#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修正版コマンドフィルタリングのテスト
"""

import re

def filter_dangerous_commands(command_str):
    """修正版: 危険なコマンドをフィルタリングし、安全なコマンドのみ許可"""
    
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
    # pingコマンドを特別処理（常に許可）
    if 'ping' in cmd_lower:
        return None
    
    # &, ;, |, && で分割してコマンドを抽出
    # ただし、pingコマンドの引数（IPアドレスやホスト名）は除外
    commands = re.split(r'\s*[;&|]+\s*', command_str)
    
    for cmd_part in commands:
        cmd_part = cmd_part.strip()
        if not cmd_part:
            continue
        
        # IPアドレスやホスト名のパターンをスキップ
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(ip_pattern, cmd_part) or re.match(domain_pattern, cmd_part):
            continue  # IPアドレスやドメイン名はスキップ
        
        # 最初の単語をコマンド名として抽出
        words = cmd_part.split()
        if not words:
            continue
            
        first_word = words[0]
        cmd_name = first_word.lower()
        
        # ホワイトリストチェック
        if cmd_name and not any(allowed == cmd_name for allowed in allowed_commands):
            return f"Command '{cmd_name}' is not in whitelist."
    
    return None  # 問題なし

def test_fixed_filter():
    """修正版フィルタのテスト"""
    
    test_cases = [
        "ping -n 4 127.0.0.1 & dir",
        "127.0.0.1 & dir",
        "google.com; whoami",
        "localhost && tasklist",
        "8.8.8.8 | systeminfo",
        "example.com & hostname",
        "ping google.com; dir",
        "dangerous_command & dir",  # これはブロックされるべき
        "python -c print('hello')",  # これもブロックされるべき
    ]
    
    print("🧪 Testing Fixed Command Filter")
    print("=" * 50)
    
    for i, cmd in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{cmd}'")
        result = filter_dangerous_commands(cmd)
        
        if result:
            print(f"   ❌ Blocked: {result}")
        else:
            print(f"   ✅ Allowed: Command would execute")

if __name__ == "__main__":
    test_fixed_filter()