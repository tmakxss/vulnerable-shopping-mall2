from app.utils import safe_database_query

def update_categories():
    try:
        print("=== カテゴリを日本語に更新中 ===")
        
        # electronics -> 電子機器
        result1 = safe_database_query(
            "UPDATE products SET category = '電子機器' WHERE category = 'electronics'"
        )
        print("electronics -> 電子機器 に更新")
        
        # clothing -> 雑貨 (clothing製品を雑貨に分類)
        result2 = safe_database_query(
            "UPDATE products SET category = '雑貨' WHERE category = 'clothing'"
        )
        print("clothing -> 雑貨 に更新")
        
        # food -> 家具 (food製品を家具に分類)
        result3 = safe_database_query(
            "UPDATE products SET category = '家具' WHERE category = 'food'"
        )
        print("food -> 家具 に更新")
        
        print("\n=== 更新後のカテゴリ確認 ===")
        categories = safe_database_query('SELECT DISTINCT category FROM products', fetch_all=True)
        for cat in categories:
            if isinstance(cat, dict):
                print(f"  - '{cat.get('category', 'Unknown')}'")
        
        print("\n=== 更新後の商品一覧 ===")
        all_products = safe_database_query('SELECT id, name, category FROM products ORDER BY category, id', fetch_all=True)
        for p in all_products:
            if isinstance(p, dict):
                print(f"  ID:{p.get('id')}, 名前:'{p.get('name')}', カテゴリ:'{p.get('category')}'")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_categories()