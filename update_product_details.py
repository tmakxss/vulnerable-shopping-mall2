from app.utils import safe_database_query

def update_product_details():
    try:
        print("=== 商品詳細を適切なカテゴリに更新中 ===")
        
        # 家具カテゴリの商品を適切な家具に変更
        safe_database_query(
            "UPDATE products SET name='オフィスチェア', description='快適な座り心地のオフィスチェア' WHERE id=5"
        )
        print("ID:5 -> オフィスチェア (家具)")
        
        safe_database_query(
            "UPDATE products SET name='木製テーブル', description='天然木を使用したダイニングテーブル' WHERE id=8"
        )
        print("ID:8 -> 木製テーブル (家具)")
        
        # 雑貨カテゴリをより適切な雑貨に変更
        safe_database_query(
            "UPDATE products SET name='文房具セット', description='ペン、ノート、消しゴムのセット' WHERE id=3"
        )
        print("ID:3 -> 文房具セット (雑貨)")
        
        safe_database_query(
            "UPDATE products SET name='キッチン用品', description='便利なキッチンツールセット' WHERE id=4"
        )
        print("ID:4 -> キッチン用品 (雑貨)")
        
        safe_database_query(
            "UPDATE products SET name='インテリア雑貨', description='おしゃれな部屋を演出する小物' WHERE id=7"
        )
        print("ID:7 -> インテリア雑貨 (雑貨)")
        
        print("\n=== 更新後の商品一覧 ===")
        all_products = safe_database_query('SELECT id, name, description, category FROM products ORDER BY category, id', fetch_all=True)
        for p in all_products:
            if isinstance(p, dict):
                print(f"  [{p.get('category')}] ID:{p.get('id')}, 名前:'{p.get('name')}', 説明:'{p.get('description')}'")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_product_details()