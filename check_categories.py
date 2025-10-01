from app.utils import safe_database_query

def check_categories():
    try:
        print("=== 現在のカテゴリ一覧 ===")
        categories = safe_database_query('SELECT DISTINCT category FROM products', fetch_all=True)
        for cat in categories:
            if isinstance(cat, dict):
                print(f"  - '{cat.get('category', 'Unknown')}'")
            else:
                print(f"  - '{cat}'")
        
        print("\n=== 全商品のカテゴリ詳細 ===")
        all_products = safe_database_query('SELECT id, name, category FROM products ORDER BY id', fetch_all=True)
        for p in all_products:
            if isinstance(p, dict):
                print(f"  ID:{p.get('id')}, 名前:'{p.get('name')}', カテゴリ:'{p.get('category')}'")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_categories()