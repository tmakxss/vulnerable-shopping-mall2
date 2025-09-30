from flask import Blueprint, render_template, request, session, redirect, flash
from app.utils import safe_database_query

bp = Blueprint('cart', __name__)

@bp.route('/cart')
def view_cart():
    """カート表示"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        cart_data = safe_database_query("""
            SELECT c.id, p.name, p.price, c.quantity, p.id as product_id, p.image_url
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (user_id,), fetch_all=True, default_value=[])
        
        # カートアイテムを配列形式に変換
        cart_items = []
        for item in cart_data:
            if isinstance(item, dict):
                item_array = [
                    item.get('id', 0),
                    item.get('name', ''),
                    float(item.get('price', 0)) if item.get('price') is not None else 0.0,
                    item.get('quantity', 0),
                    item.get('product_id', 0),
                    item.get('image_url') or '/static/test.jpeg'
                ]
                cart_items.append(item_array)
        
        total = sum(item[2] * item[3] for item in cart_items)
        
        return render_template('cart/view.html', cart_items=cart_items, total=total)
        
    except Exception as e:
        flash(f'カートの取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('cart/view.html', cart_items=[], total=0)

@bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """カートに商品追加"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)
    user_id = session['user_id']
    
    try:
        # CSRFトークン検証なし - 脆弱性
        # 既存のカートアイテム確認
        existing = safe_database_query(
            "SELECT * FROM cart WHERE user_id = %s AND product_id = %s", 
            (user_id, product_id),
            fetch_one=True
        )
        
        if existing:
            # 数量更新
            safe_database_query(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND product_id = %s", 
                (quantity, user_id, product_id)
            )
        else:
            # 新規アイテム追加
            safe_database_query(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", 
                (user_id, product_id, quantity)
            )
        
        flash('カートに追加しました', 'success')
        
    except Exception as e:
        flash(f'カートへの追加中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(f'/product/{product_id}')

@bp.route('/cart/remove/<int:cart_id>', methods=['GET', 'POST'])
def remove_from_cart(cart_id):
    """カートから商品削除"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # IDOR脆弱性 - ユーザー確認なし
        safe_database_query(
            "DELETE FROM cart WHERE id = %s", 
            (cart_id,)
        )
        flash('カートから削除しました', 'success')
        
    except Exception as e:
        flash(f'削除中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect('/cart')

@bp.route('/cart/clear')
def clear_cart():
    """カートクリア"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        safe_database_query(
            "DELETE FROM cart WHERE user_id = %s", 
            (user_id,)
        )
        flash('カートをクリアしました', 'success')
        
    except Exception as e:
        flash(f'クリア中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect('/cart')

@bp.route('/cart/update', methods=['POST'])
def update_cart():
    """カート数量更新"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # 隠しフィールド操作脆弱性
        item_id = request.form.get('item_id')
        quantity = request.form.get('quantity')
        
        safe_database_query(
            "UPDATE cart SET quantity = ? WHERE id = ? AND user_id = ?", 
            (quantity, item_id, user_id)
        )
        
        flash('カートを更新しました', 'success')
        
    except Exception as e:
        flash(f'更新中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect('/cart') 