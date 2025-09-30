from flask import Blueprint, render_template, request, session, redirect, flash
from app.utils import safe_database_query

bp = Blueprint('product', __name__)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """商品詳細ページ"""
    try:
        # 商品情報取得
        product_data = safe_database_query(
            "SELECT id, name, description, price, stock, category, image_url FROM products WHERE id = ?",
            (product_id,),
            fetch_one=True
        )
        
        if not product_data:
            flash('商品が見つかりません', 'error')
            return redirect('/products')
        
        # 配列形式に変換（テンプレート互換性のため）
        product = [
            product_data.get('id', 0),
            product_data.get('name', ''),
            product_data.get('description', ''),
            float(product_data.get('price', 0)) if product_data.get('price') is not None else 0.0,
            product_data.get('stock', 0),
            product_data.get('category', ''),
            product_data.get('image_url') or '/static/test.jpeg'
        ]
        
        # レビュー取得
        reviews_data = safe_database_query(
            "SELECT r.id, r.rating, r.comment, r.created_at, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = ? ORDER BY r.created_at DESC",
            (product_id,),
            fetch_all=True,
            default_value=[]
        )
        
        # レビューも配列形式に変換
        reviews = []
        for review in reviews_data:
            if isinstance(review, dict):
                review_array = [
                    review.get('id', 0),
                    product_id,  # product_id
                    0,  # user_id (使用されていない)
                    review.get('rating', 0),
                    review.get('comment', ''),
                    review.get('created_at', ''),
                    review.get('username', '')
                ]
                reviews.append(review_array)
        
        return render_template('product/detail.html', product=product, reviews=reviews)
        
    except Exception as e:
        flash(f'商品の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/products')

@bp.route('/product/<int:product_id>/review', methods=['POST'])
def add_review(product_id):
    """レビュー投稿"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']
    
    if not rating or not comment:
        flash('評価とコメントを入力してください', 'error')
        return redirect(f'/product/{product_id}')
    
    try:
        # XSS脆弱性 - コメント内容をフィルタリングせずに保存
        safe_database_query(
            "INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)", 
            (product_id, user_id, rating, comment)
        )
        
        flash('レビューを投稿しました', 'success')
        return redirect(f'/product/{product_id}')
        
    except Exception as e:
        flash(f'レビューの投稿中にエラーが発生しました: {str(e)}', 'error')
        return redirect(f'/product/{product_id}')

@bp.route('/categories')
def categories():
    """カテゴリ一覧"""
    try:
        categories_data = safe_database_query(
            "SELECT DISTINCT category FROM products",
            fetch_all=True,
            default_value=[]
        )
        
        # カテゴリを配列形式に変換
        categories = []
        for cat in categories_data:
            if isinstance(cat, dict):
                categories.append([cat.get('category', '')])
            else:
                categories.append([cat])
        
        return render_template('product/categories.html', categories=categories)
        
    except Exception as e:
        flash(f'カテゴリの取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('product/categories.html', categories=[]) 