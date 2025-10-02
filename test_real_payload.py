#!/usr/bin/env python3
"""
実際のペイロードテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.main import partial_decode_for_xss

def test_real_payload():
    print("=== 実際のペイロードテスト ===\n")
    
    # 実際のペイロード
    payload = "<svg/onload%3d%26%23x61;%26%23x6C;%26%23x65;%26%23x72;%26%23x74;(1)>"
    
    print(f"入力: {payload}")
    result = partial_decode_for_xss(payload)
    print(f"出力: {result}")
    print(f"期待: <svg/onload=alert(1)>")
    print(f"一致: {'✅' if result == '<svg/onload=alert(1)>' else '❌'}")

if __name__ == "__main__":
    test_real_payload()