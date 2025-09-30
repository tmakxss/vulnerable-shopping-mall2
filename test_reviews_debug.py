from app.utils import safe_database_query

def test_reviews_data():
    """レビューデータの確認とエラー診断"""
    print("=== レビューデータ確認 ===")
    
    try:
        # レビューテーブルの存在確認
        print("1. レビューテーブルの確認")
        reviews_count = safe_database_query("SELECT COUNT(*) as count FROM reviews", fetch_one=True)
        print(f"レビュー数: {reviews_count}")
        
        # レビューデータの構造確認
        print("2. レビューデータの構造確認")
        reviews_raw = safe_database_query("""
            SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                   COALESCE(u.username, '不明') as username, COALESCE(p.name, '削除済み') as product_name 
            FROM reviews r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN products p ON r.product_id = p.id 
            ORDER BY r.id ASC
            LIMIT 5
        """, fetch_all=True, default_value=[])
        
        print(f"取得したデータ: {reviews_raw}")
        
        if reviews_raw:
            print("3. 配列変換テスト")
            all_reviews = []
            for review in reviews_raw:
                if isinstance(review, dict):
                    review_array = [
                        review.get('id', ''),               # 0: レビューID
                        review.get('username', ''),         # 1: ユーザー名
                        review.get('product_name', ''),     # 2: 商品名
                        review.get('rating', ''),           # 3: 評価
                        review.get('comment', ''),          # 4: コメント
                        review.get('created_at', ''),       # 5: 作成日
                        review.get('user_id', ''),          # 6: ユーザーID(非表示)
                        review.get('product_id', '')        # 7: 商品ID(非表示)
                    ]
                    all_reviews.append(review_array)
                    print(f"変換結果: {review_array}")
            
            print("4. ページング計算テスト")
            page = 1
            per_page = 20
            total = len(all_reviews)
            total_pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            reviews = all_reviews[start_idx:end_idx] if all_reviews else []
            
            print(f"total: {total}")
            print(f"total_pages: {total_pages}")
            print(f"start_idx: {start_idx}")
            print(f"end_idx: {end_idx}")
            print(f"reviews: {reviews}")
        
        # URL パラメータのテスト
        print("5. URLパラメータテスト")
        test_params = ['1', '2', '', 'abc', None]
        for param in test_params:
            try:
                page_test = int(param) if param else 1
                print(f"'{param}' → {page_test}")
            except (ValueError, TypeError) as e:
                print(f"'{param}' → エラー: {e}, デフォルト値: 1")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reviews_data()