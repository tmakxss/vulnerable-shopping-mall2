from flask import Blueprint, render_template, request, session, redirect, flash, render_template_string
from app.utils import safe_database_query, get_database_status

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """メインページ"""
    try:
        # データベース状態確認
        db_status, db_message = get_database_status()
        
        if not db_status:
            # データベース接続できない場合のフォールバック
            return render_template_string('''
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>脆弱なショッピングモール - 初期化中</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="alert alert-danger alert-dismissible fade show m-0 rounded-0 text-center" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <strong>⚠️ セキュリティ学習専用サイト ⚠️</strong>
                    このサイトは教育目的でのみ使用してください。実際の攻撃は違法です。
                </div>
                
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-header bg-warning">
                                    <h2 class="mb-0">🔒 脆弱なショッピングモール</h2>
                                </div>
                                <div class="card-body">
                                    <div class="alert alert-info">
                                        <h4>🚧 サイト初期化中</h4>
                                        <p>現在データベースの初期化を行っています。</p>
                                        <p><strong>状態:</strong> {{ db_message }}</p>
                                        
                                        <h5 class="mt-3">🔧 管理者向け手順:</h5>
                                        <ol>
                                            <li>Supabaseダッシュボードでプロジェクトが稼働中か確認</li>
                                            <li>ローカルで <code>py database/init_supabase.py</code> を実行</li>
                                            <li>データベース初期化完了後にサイトを再読み込み</li>
                                        </ol>
                                        
                                        <div class="mt-3">
                                            <a href="/health" class="btn btn-primary">詳細状態確認</a>
                                            <a href="/" class="btn btn-secondary ms-2">再読み込み</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            ''', db_message=db_message)
        
        # 人気商品を取得（安全バージョン）
        try:
            featured_products = safe_database_query(
                "SELECT id, name, description, price, stock, category FROM products ORDER BY id DESC LIMIT 4",
                fetch_all=True,
                default_value=[]
            )
            
            # 商品データの安全な処理（テンプレート互換性のため配列形式で提供）
            safe_featured_products = []
            for product in featured_products or []:
                if isinstance(product, dict):
                    # テンプレートが期待する配列形式に変換
                    product_array = [
                        product.get('id', 0),
                        product.get('name', ''),
                        product.get('description', ''),
                        float(product.get('price', 0)) if product.get('price') is not None else 0.0,
                        product.get('stock', 0),
                        product.get('category', ''),
                        product.get('image_url') or '/static/test.jpeg'  # デフォルト画像
                    ]
                    safe_featured_products.append(product_array)
            
            featured_products = safe_featured_products
            
        except Exception as e:
            print(f"Featured products error: {e}")
            featured_products = []
        
        # レビュー検索機能（安全バージョン）
        review_query = request.args.get('review_search', '')
        recent_reviews = []
        
        try:
            if review_query:
                # レビュー検索 (SQLインジェクション対策済み、XSS脆弱性は残存)
                recent_reviews = safe_database_query("""
                    SELECT r.id, r.product_id, r.user_id, r.rating, r.comment, r.created_at,
                           u.username, p.name as product_name
                    FROM reviews r 
                    JOIN users u ON r.user_id = u.id 
                    JOIN products p ON r.product_id = p.id 
                    WHERE r.comment LIKE ? OR u.username LIKE ? OR p.name LIKE ?
                    ORDER BY r.created_at DESC LIMIT 10
                """, (f'%{review_query}%', f'%{review_query}%', f'%{review_query}%'),
                fetch_all=True,
                default_value=[]
                )
            else:
                # 最新レビューを取得（安全バージョン）
                recent_reviews = safe_database_query("""
                    SELECT r.id, r.product_id, r.user_id, r.rating, r.comment, r.created_at,
                           u.username, p.name as product_name
                    FROM reviews r 
                    JOIN users u ON r.user_id = u.id 
                    JOIN products p ON r.product_id = p.id 
                    ORDER BY r.created_at DESC LIMIT 10
                """, fetch_all=True, default_value=[])
                
        except Exception as e:
            print(f"Reviews error: {e}")
            recent_reviews = []
        
        return render_template('main/index.html', 
                             featured_products=featured_products, 
                             recent_reviews=recent_reviews,
                             review_query=review_query)
                             
    except Exception as e:
        # エラーハンドリング
        return render_template_string('''
        <div class="alert alert-danger">
            <h4>エラーが発生しました</h4>
            <p>{{ error }}</p>
            <a href="/health" class="btn btn-primary">システム状態確認</a>
        </div>
        ''', error=str(e))

@bp.route('/products')
def products():
    """商品一覧ページ"""
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page
    
    try:
        if category:
            # SQLインジェクション脆弱性（意図的）
            all_products = safe_database_query(
                f"SELECT id, name, description, price, stock, category, image_url FROM products WHERE category = '{category}'",
                fetch_all=True,
                default_value=[]
            )
        else:
            all_products = safe_database_query(
                "SELECT id, name, description, price, stock, category, image_url FROM products",
                fetch_all=True,
                default_value=[]
            )
        
        # 商品データを配列形式に変換（テンプレート互換性のため）
        converted_products = []
        for product in all_products:
            if isinstance(product, dict):
                product_array = [
                    product.get('id', 0),
                    product.get('name', ''),
                    product.get('description', ''),
                    float(product.get('price', 0)) if product.get('price') is not None else 0.0,
                    product.get('stock', 0),
                    product.get('category', ''),
                    product.get('image_url') or '/static/test.jpeg'
                ]
                converted_products.append(product_array)
        
        # ページング処理
        total_products = len(converted_products)
        total_pages = (total_products + per_page - 1) // per_page if total_products > 0 else 1
        
        # 現在のページの商品を取得
        products = converted_products[offset:offset + per_page]
        
        # デバッグ情報を追加
        print(f"Debug - Products count: {len(products)}")
        if products:
            print(f"Debug - First product: {products[0]}")
            print(f"Debug - Product type: {type(products[0])}")
        
        return render_template('main/products.html', 
                             products=products, 
                             category=category,
                             current_page=page,
                             total_pages=total_pages,
                             total_products=total_products)
                             
    except Exception as e:
        flash(f'商品の取得中にエラーが発生しました: {str(e)}', 'danger')
        return render_template('main/products.html', 
                             products=[], 
                             category=category,
                             current_page=1,
                             total_pages=1,
                             total_products=0)

@bp.route('/search')
def search():
    """商品検索ページ"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page
    
    if query:
        try:
            # SQLインジェクション脆弱性（意図的）
            sql_query = f"SELECT id, name, description, price, stock, category, image_url FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
            all_results = safe_database_query(sql_query, fetch_all=True, default_value=[])
            
            # 検索結果を配列形式に変換（テンプレート互換性のため）
            converted_results = []
            for product in all_results:
                if isinstance(product, dict):
                    product_array = [
                        product.get('id', 0),
                        product.get('name', ''),
                        product.get('description', ''),
                        float(product.get('price', 0)) if product.get('price') is not None else 0.0,
                        product.get('stock', 0),
                        product.get('category', ''),
                        product.get('image_url') or '/static/test.jpeg'
                    ]
                    converted_results.append(product_array)
            
            # ページング処理
            total_results = len(converted_results)
            total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 1
            
            # 現在のページの結果を取得
            results = converted_results[offset:offset + per_page]
            
            return render_template('main/search.html', 
                                 results=results, 
                                 query=query,
                                 current_page=page,
                                 total_pages=total_pages,
                                 total_results=total_results)
                                 
        except Exception as e:
            flash(f'検索中にエラーが発生しました: {str(e)}', 'danger')
            return render_template('main/search.html', 
                                 results=[], 
                                 query=query,
                                 current_page=1,
                                 total_pages=1,
                                 total_results=0)
    
    return render_template('main/search.html')

@bp.route('/about')
def about():
    """サイトについて"""
    return render_template('main/about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        
        if title and message:
            # メッセージ保存（ここでは処理をスキップ）
            flash('お問い合わせを送信しました。', 'success')
        else:
            flash('タイトルとメッセージを入力してください。', 'danger')
    
    return render_template('main/contact.html')