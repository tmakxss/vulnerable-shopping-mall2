from flask import Blueprint, render_template, request, session, redirect, flash, render_template_string
from app.utils import safe_database_query, get_database_status
import secrets
import time

bp = Blueprint('main', __name__)

def generate_csrf_token():
    """一度きりのCSRFトークンを生成してSupabaseに記録"""
    token = secrets.token_urlsafe(32)
    timestamp = int(time.time())
    user_id = session.get('user_id')
    
    session['csrf_token'] = token
    session['csrf_timestamp'] = str(timestamp)
    
    # Supabaseにトークンを記録
    try:
        safe_database_query("""
            INSERT INTO csrf_tokens (user_id, token, created_at, is_used) 
            VALUES (%s, %s, %s, 0)
            ON CONFLICT (token) DO UPDATE SET created_at = EXCLUDED.created_at
        """, (user_id, token, timestamp))
        print(f"[CSRF] 新しいトークンをSupabaseに記録: {token[:8]}...")
    except Exception as e:
        print(f"[CSRF] Supabaseエラー: {e}")
    
    # 古いトークンをクリーンアップ（1時間以上古いものを削除）
    old_timestamp = timestamp - 3600
    try:
        safe_database_query("""
            DELETE FROM csrf_tokens 
            WHERE user_id = %s AND created_at < %s
        """, (user_id, old_timestamp))
    except Exception as e:
        print(f"[CSRF] クリーンアップエラー: {e}")
    
    return token

def validate_csrf_token(submitted_token):
    """提出されたCSRFトークンをSupabaseで検証し、一度使用後は無効化"""
    if not submitted_token:
        print(f"[CSRF] トークンが提出されていません")
        return False
        
    user_id = session.get('user_id')
    if not user_id:
        print(f"[CSRF] ユーザーIDがセッションにありません")
        return False
    
    print(f"[CSRF] 提出されたトークン: {submitted_token[:8]}...")
    print(f"[CSRF] ユーザーID: {user_id}")
    
    try:
        # Supabaseでトークンの状態を確認
        token_data = safe_database_query("""
            SELECT token, is_used FROM csrf_tokens 
            WHERE user_id = %s AND token = %s
        """, (user_id, submitted_token), fetch_one=True)
        
        if not token_data:
            print(f"[CSRF] Supabaseにトークンが見つかりません")
            return False
        
        if token_data.get('is_used', 0) == 1:
            print(f"[CSRF] 既に使用済みのトークンです: {submitted_token[:8]}...")
            return False
        
        # トークンを使用済みにマーク（原子的操作）
        result = safe_database_query("""
            UPDATE csrf_tokens 
            SET is_used = 1 
            WHERE user_id = %s AND token = %s AND is_used = 0
        """, (user_id, submitted_token))
        
        # PostgreSQLではrowcountを確認
        if hasattr(result, 'rowcount'):
            affected_rows = result.rowcount
        else:
            # 更新されたかどうかを再確認
            check_data = safe_database_query("""
                SELECT is_used FROM csrf_tokens 
                WHERE user_id = %s AND token = %s
            """, (user_id, submitted_token), fetch_one=True)
            affected_rows = 1 if check_data and check_data.get('is_used') == 1 else 0
        
        if affected_rows > 0:
            # セッションからも削除
            session.pop('csrf_token', None)
            session.pop('csrf_timestamp', None)
            
            print(f"[CSRF] トークンが正常に検証され、Supabaseで使用済みにマークされました: {submitted_token[:8]}...")
            return True
        else:
            print(f"[CSRF] トークンの更新に失敗しました（競合状態の可能性）")
            return False
            
    except Exception as e:
        print(f"[CSRF] Supabaseエラー: {e}")
        return False

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
                "SELECT id, name, description, price, stock, category, image_url FROM products ORDER BY id DESC LIMIT 4",
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
        
        # レビュー検索機能（XSSフィルター付き）
        review_query = request.args.get('review_search', '')
        recent_reviews = []
        
        try:
            if review_query:
                # XSSフィルターチェック
                review_search_blocked_keywords = [
                    '>', ' ', '%26', '%23', '&', '#'
                ]
                
                review_query_lower = review_query.lower()
                blocked = False
                detected_keyword = None
                
                for keyword in review_search_blocked_keywords:
                    if keyword in review_query_lower:
                        blocked = True
                        detected_keyword = keyword
                        break
                
                if blocked:
                    # ブロックされた場合はエラーメッセージと空の結果を返し、クエリもクリア
                    flash('不正な検索クエリが検出されました。検索をブロックしました。', 'danger')
                    recent_reviews_raw = []
                    review_query = ""  # 反射攻撃を防ぐためクエリをクリア
                else:
                    # レビュー検索 (SQLインジェクション対策済み、XSSフィルター付き)
                    recent_reviews_raw = safe_database_query("""
                        SELECT r.id, r.product_id, r.user_id, r.rating, r.comment, r.created_at,
                               u.username, p.name as product_name, p.image_url
                        FROM reviews r 
                        JOIN users u ON r.user_id = u.id 
                        JOIN products p ON r.product_id = p.id 
                        WHERE r.comment LIKE %s OR u.username LIKE %s OR p.name LIKE %s
                        ORDER BY r.created_at DESC LIMIT 10
                    """, (f'%{review_query}%', f'%{review_query}%', f'%{review_query}%'),
                    fetch_all=True,
                    default_value=[]
                    )
            else:
                # 最新レビューを取得（安全バージョン）
                recent_reviews_raw = safe_database_query("""
                    SELECT r.id, r.product_id, r.user_id, r.rating, r.comment, r.created_at,
                           u.username, p.name as product_name, p.image_url
                    FROM reviews r 
                    JOIN users u ON r.user_id = u.id 
                    JOIN products p ON r.product_id = p.id 
                    ORDER BY r.created_at DESC LIMIT 10
                """, fetch_all=True, default_value=[])
                
            # テンプレート互換性のため配列形式に変換
            recent_reviews = []
            for review in recent_reviews_raw or []:
                if isinstance(review, dict):
                    review_array = [
                        review.get('id', 0),
                        review.get('product_id', 0),
                        review.get('user_id', 0),
                        review.get('rating', 0),
                        review.get('comment', ''),
                        review.get('created_at', ''),
                        review.get('username', ''),
                        review.get('product_name', ''),
                        review.get('image_url') or '/static/test.jpeg'  # 商品画像URL
                    ]
                    recent_reviews.append(review_array)
                
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
    
    # 脆弱性：GETパラメーターでのリクエストを処理（CSRFバイパス）
    # パラメーターが存在する場合は送信処理を実行
    if request.method == 'GET' and (request.args.get('title') or request.args.get('email') or request.args.get('content') or request.args.getlist('title[]')):
        title = request.args.get('title', '').strip()
        content = request.args.get('content', '').strip()
        email = request.args.get('email', '').strip()
        
        # 配列パラメーター処理（XSS脆弱性）
        title_array = request.args.getlist('title[]')
        
        # より柔軟な配列検出（title[任意の文字]の形式もチェック）
        if not title_array:
            for key in request.args.keys():
                if key.startswith('title[') and key.endswith(']'):
                    # title[anything]形式を検出 - []内の文字列を取得
                    bracket_content = key[6:-1]  # "title["と"]"を除いた部分
                    if bracket_content:
                        title_array = [bracket_content]
                        print(f"[XSS VULN] GET柔軟検出: {key} -> 配列内容: {bracket_content}")
                        break
        
        if title_array:
            # 配列の中身を大文字に変換してflashメッセージに表示（空文字でも処理）
            upper_titles = []
            for item in title_array:
                # 大文字変換
                upper_item = item.upper()
                # 特定の文字のHTMLエンティティを復元（XSS脆弱性）
                upper_item = upper_item.replace('&LT;', '<')
                upper_item = upper_item.replace('&GT;', '>')
                upper_item = upper_item.replace('&EQUALS;', '=')
                upper_item = upper_item.replace('&#X60;', '`')
                upper_item = upper_item.replace('&GRAVE;', '`')
                # 数値文字参照も処理
                upper_item = upper_item.replace('&#X61;', 'A')  # a -> A
                upper_item = upper_item.replace('&#X6C;', 'L')  # l -> L  
                upper_item = upper_item.replace('&#X65;', 'E')  # e -> E
                upper_item = upper_item.replace('&#X72;', 'R')  # r -> R
                upper_item = upper_item.replace('&#X74;', 'T')  # t -> T
                upper_titles.append(upper_item)
            
            flash(f'件名がありません: {", ".join(upper_titles)}', 'error')
            print(f"[XSS VULN] 配列パラメーター検出: {upper_titles}")
            return redirect('/contact')
        
        print(f"[CSRF BYPASS] GET パラメーター検出: title={title}, email={email}, content={content}")
        
        if title and content and email:
            # 脆弱性：GETリクエストではCSRFトークン検証をスキップ
            flash(f'お問い合わせ「{title}」を送信しました。', 'success')
            print(f"[CSRF BYPASS] 送信成功: {title}")
        else:
            flash(f'一部の項目が不足しています。送信に失敗しました。', 'warning')
            print(f"[CSRF BYPASS] 送信失敗: 不完全なパラメーター")
        
        # パラメーターをクリアしてリダイレクト
        return redirect('/contact')
    
    # GETリクエストの場合：CSRFトークンを生成してフォーム表示
    if request.method == 'GET':
        csrf_token = generate_csrf_token()
        return render_template('main/contact.html', csrf_token=csrf_token)
    
    # POSTリクエストの場合：通常のCSRF検証を実行
    elif request.method == 'POST':
        submitted_token = request.form.get('token')
        
        # デバッグ：すべてのPOSTパラメーターを表示
        print(f"[DEBUG] POSTパラメーター: {dict(request.form)}")
        
        # 配列パラメーター処理（XSS脆弱性） - POSTでも対応
        title_array = request.form.getlist('title[]')
        
        # より柔軟な配列検出（title[任意の文字]の形式もチェック）
        if not title_array:
            for key in request.form.keys():
                if key.startswith('title[') and key.endswith(']'):
                    # title[anything]形式を検出 - []内の文字列を取得
                    bracket_content = key[6:-1]  # "title["と"]"を除いた部分
                    if bracket_content:
                        title_array = [bracket_content]
                        print(f"[XSS VULN] 柔軟検出: {key} -> 配列内容: {bracket_content}")
                        break
        
        if title_array:
            # 配列の中身を大文字に変換してflashメッセージに表示（空文字でも処理）
            upper_titles = []
            for item in title_array:
                # 大文字変換
                upper_item = item.upper()
                # 特定の文字のHTMLエンティティを復元（XSS脆弱性）
                upper_item = upper_item.replace('&LT;', '<')
                upper_item = upper_item.replace('&GT;', '>')
                upper_item = upper_item.replace('&EQUALS;', '=')
                upper_item = upper_item.replace('&#X60;', '`')
                upper_item = upper_item.replace('&GRAVE;', '`')
                # 数値文字参照も処理
                upper_item = upper_item.replace('&#X61;', 'A')  # a -> A
                upper_item = upper_item.replace('&#X6C;', 'L')  # l -> L  
                upper_item = upper_item.replace('&#X65;', 'E')  # e -> E
                upper_item = upper_item.replace('&#X72;', 'R')  # r -> R
                upper_item = upper_item.replace('&#X74;', 'T')  # t -> T
                upper_titles.append(upper_item)
            
            flash(f'件名がありません: {", ".join(upper_titles)}', 'error')
            print(f"[XSS VULN] POST配列パラメーター検出: {upper_titles}")
            return redirect('/contact')
        
        # CSRFトークン検証
        if not validate_csrf_token(submitted_token):
            flash('セキュリティトークンが無効です。フォームを再読み込みしてください。', 'error')
            return redirect('/contact')
        
        title = request.form.get('title')
        content = request.form.get('content')
        email = request.form.get('email')
        
        if title and content and email:
            # お問い合わせ処理（デモ版のためスキップ）
            flash(f'お問い合わせ「{title}」を送信しました。', 'success')
            # 送信後は新しいトークンを生成せずにリダイレクト
            return redirect('/contact')
        else:
            flash('すべての項目を入力してください。', 'error')
            return redirect('/contact')
    
    # デフォルト：フォーム表示
    csrf_token = generate_csrf_token()
    return render_template('main/contact.html', csrf_token=csrf_token)