#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
コマンドフィルタリングのデバッグテスト
"""

import subprocess
import re

def debug_filter_dangerous_commands(command_str):
    """デバッグ版: 危険なコマンドをフィルタリング"""
    
    print(f"🔍 Debug: Analyzing command: '{command_str}'")
    
    # 許可されるコマンドのホワイトリスト（Windows + Linux両対応）
    allowed_commands = [
        'dir', 'ls', 'whoami', 'id', 'pwd', 'echo', 'date', 'time',
        'hostname', 'uname', 'ping', 'tracert', 'traceroute', 'nslookup',
        'systeminfo', 'ver', 'cat', 'head', 'tail', 'wc', 'grep',
        'find', 'locate', 'which', 'where', 'type', 'ps', 'top',
        'tasklist', 'tree', 'ipconfig', 'arp', 'netstat', 'vol',
        'fsutil', 'wmic', 'sc', 'reg'  # Windows特有コマンドを追加
    ]
    
    print(f"📋 Allowed commands: {allowed_commands}")
    
    # 危険なパターンの直接チェック
    cmd_lower = command_str.lower()
    dangerous_patterns = [
        'rm -rf', 'del /s', 'format c:', 'shutdown', 'reboot',
        'python -c', 'powershell -c', 'cmd /c', 'bash -c',
        'curl http', 'wget http', 'certutil -url', 'msiexec'
    ]
    
    print(f"🚨 Checking dangerous patterns...")
    for pattern in dangerous_patterns:
        if pattern in cmd_lower:
            print(f"❌ Found dangerous pattern: '{pattern}'")
            return f"Dangerous pattern '{pattern}' detected and blocked."
    
    print("✅ No dangerous patterns found")
    
    # 基本的なコマンド抽出（改良版）
    print(f"🔍 Splitting command by separators...")
    commands = re.split(r'[;&|]+', command_str)
    print(f"📝 Split commands: {commands}")
    
    for i, cmd_part in enumerate(commands):
        cmd_part = cmd_part.strip()
        print(f"  {i+1}. Processing: '{cmd_part}'")
        
        if not cmd_part:
            print(f"     → Empty, skipping")
            continue
            
        # 最初の単語をコマンド名として抽出
        words = cmd_part.split()
        if not words:
            print(f"     → No words found, skipping")
            continue
            
        first_word = words[0]
        cmd_name = first_word.lower()
        print(f"     → Command name: '{cmd_name}'")
        
        # ホワイトリストチェック
        is_allowed = any(allowed == cmd_name for allowed in allowed_commands)
        is_ping = 'ping' in cmd_name
        
        print(f"     → In whitelist: {is_allowed}")
        print(f"     → Contains 'ping': {is_ping}")
        
        if cmd_name and not is_allowed and not is_ping:
            print(f"     ❌ Command '{cmd_name}' is not in whitelist.")
            return f"Command '{cmd_name}' is not in whitelist."
        else:
            print(f"     ✅ Command '{cmd_name}' is allowed")
    
    print("🎉 All commands passed filtering!")
    return None  # 問題なし

def test_commands():
    """テストコマンドの実行"""
    
    test_cases = [
        "ping -n 4 127.0.0.1 & dir",
        "ping localhost; whoami",
        "127.0.0.1 && dir",
        "google.com | tasklist"
    ]
    
    print("🧪 Testing command filtering...")
    print("=" * 60)
    
    for i, cmd in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {cmd}")
        print("-" * 40)
        
        result = debug_filter_dangerous_commands(cmd)
        if result:
            print(f"❌ Blocked: {result}")
        else:
            print("✅ Command passed filtering - would execute")
            
            # 実際に実行してみる（安全なコマンドのみ）
            try:
                print("🚀 Executing...")
                output = subprocess.check_output(cmd, shell=True, text=True, timeout=10)
                print(f"📤 Output (first 200 chars): {output[:200]}...")
            except subprocess.CalledProcessError as e:
                print(f"❌ Execution failed (exit code {e.returncode}): {e.output}")
            except Exception as e:
                print(f"❌ Execution error: {str(e)}")

if __name__ == "__main__":
    test_commands()