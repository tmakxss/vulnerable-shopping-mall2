from flask import Blueprint, render_template, request, session, redirect, flash
from app.utils import safe_database_query

bp = Blueprint('order', __name__)

@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """チェックアウトページ"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    if request.method == 'POST':
        user_id = session['user_id']
        
        # 注文情報 (隠しフィールド操作脆弱性)
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        total_amount = request.form.get('total_amount')  # 隠しフィールド
        
        if not shipping_address or not payment_method:
            flash('配送先住所と支払い方法を入力してください', 'error')
            return redirect('/checkout')
        
        try:
            # 注文作成（より確実な方法）
            print(f"DEBUG: Creating order for user_id={user_id}, shipping_address={shipping_address}, total_amount={total_amount}")
            
            # まず注文を作成
            result = safe_database_query("""
                INSERT INTO orders (user_id, shipping_address, total_amount, status, created_at) 
                VALUES (%s, %s, %s, 'pending', CURRENT_TIMESTAMP)
            """, (user_id, shipping_address, total_amount))
            
            print(f"DEBUG: Insert result = {result}")
            
            # 最後に挿入された注文IDを取得
            order_data = safe_database_query("""
                SELECT id FROM orders 
                WHERE user_id = %s 
                ORDER BY created_at DESC, id DESC 
                LIMIT 1
            """, (user_id,), fetch_one=True)
            
            print(f"DEBUG: order_data = {order_data}, type = {type(order_data)}")
            
            order_id = order_data['id'] if order_data else None
            print(f"DEBUG: order_id = {order_id}")
            
            if not order_id:
                flash('注文の作成に失敗しました', 'error')
                return redirect('/checkout')
            
            # カートアイテムを注文アイテムに移動
            cart_items = safe_database_query(
                "SELECT product_id, quantity FROM cart WHERE user_id = %s", 
                (user_id,), fetch_all=True
            )
            
            print(f"DEBUG: cart_items = {cart_items}")
            
            for item in cart_items:
                # 商品価格取得
                price_data = safe_database_query(
                    "SELECT price FROM products WHERE id = %s", 
                    (item['product_id'],), fetch_one=True
                )
                price = price_data['price'] if price_data else 0
                
                print(f"DEBUG: Adding order item - order_id={order_id}, product_id={item['product_id']}, quantity={item['quantity']}, price={price}")
                
                result = safe_database_query("""
                    INSERT INTO order_items (order_id, product_id, quantity, price) 
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['product_id'], item['quantity'], price))
                
                print(f"DEBUG: Order item insert result = {result}")
            
            # カートを空にする
            cart_clear_result = safe_database_query("DELETE FROM cart WHERE user_id = %s", (user_id,))
            print(f"DEBUG: Cart clear result = {cart_clear_result}")
            
            print(f"DEBUG: Order creation completed successfully, order_id = {order_id}")
            flash('注文が完了しました', 'success')
            return redirect(f'/order/{order_id}')
            
        except Exception as e:
            flash(f'注文処理中にエラーが発生しました: {str(e)}', 'error')
            return redirect('/checkout')
    
    # カート情報表示
    user_id = session['user_id']
    
    try:
        cart_data = safe_database_query("""
            SELECT p.name, p.price, c.quantity, (p.price * c.quantity) as total
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (user_id,), fetch_all=True)
        
        print(f"DEBUG: cart_data = {cart_data}, type = {type(cart_data)}")
        
        if not cart_data:
            flash('カートが空です', 'error')
            return redirect('/cart')
        
        # カートアイテムを配列形式に変換（テンプレート互換性のため）
        cart_items = []
        for item in cart_data:
            if isinstance(item, dict):
                item_array = [
                    item.get('name', ''),           # [0]: name
                    item.get('price', 0.0),         # [1]: price  
                    item.get('quantity', 0),        # [2]: quantity
                    float(item.get('total', 0.0))   # [3]: total
                ]
                cart_items.append(item_array)
        
        total = sum(float(item[3]) for item in cart_items)
        print(f"DEBUG: total = {total}")
        
        return render_template('order/checkout.html', cart_items=cart_items, total=total)
        
    except Exception as e:
        flash(f'カート情報の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/cart')

@bp.route('/order/<int:order_id>')
def order_detail(order_id):
    """注文詳細ページ"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # SQLインジェクション脆弱性を維持 - 直接文字列挿入
        query = f"SELECT * FROM orders WHERE id = {order_id} AND user_id = {user_id}"
        order_data = safe_database_query(query, fetch_all=True)
        
        if not order_data:
            flash('注文が見つかりません', 'error')
            return redirect('/orders')
        
        order = order_data[0]  # リストの最初の要素
        
        # 注文アイテム照会
        items_query = f"""
            SELECT oi.*, p.name, p.price 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = {order_id}
        """
        items = safe_database_query(items_query, fetch_all=True)
        
        return render_template('order/detail.html', order=order, items=items)
        
    except Exception as e:
        flash(f'注文詳細の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/orders')

@bp.route('/orders')
def my_orders():
    """注文履歴"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # SQLインジェクション脆弱性を維持
        query = f"SELECT * FROM orders WHERE user_id = {user_id} ORDER BY id ASC"
        orders = safe_database_query(query, fetch_all=True)
        
        return render_template('order/list.html', orders=orders)
        
    except Exception as e:
        flash(f'注文履歴の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/')

@bp.route('/order/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    """注文キャンセル"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # 本人注文のみキャンセル可能
        order_data = safe_database_query(
            "SELECT status FROM orders WHERE id = %s AND user_id = %s", 
            (order_id, user_id), fetch_one=True
        )
        
        if not order_data:
            flash('注文が見つかりません', 'error')
            return redirect('/orders')
        
        order_status = order_data['status'] if order_data else None
        
        if order_status != 'pending':
            flash('すでに処理された注文はキャンセルできません', 'error')
            return redirect('/orders')
        
        safe_database_query(
            "UPDATE orders SET status = 'cancelled' WHERE id = %s", 
            (order_id,)
        )
        
        flash('ご注文がキャンセルされました', 'success')
        return redirect('/orders')
        
    except Exception as e:
        flash(f'注文キャンセル中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/orders') 