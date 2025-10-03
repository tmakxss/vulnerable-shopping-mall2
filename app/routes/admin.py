from flask import Blueprint, render_template, request, session, redirect, flash, jsonify, make_response
from app.utils import safe_database_query
import json
import os
import subprocess
import platform
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin_dashboard():
    """管理者ダッシュボード"""
    # 脆弱な権限検証
    user_id = request.cookies.get('user_id')
    is_admin = request.cookies.get('is_admin', 'false')
    role = request.cookies.get('role', 'user')
    
    # 権限検証 (隠しパラメータによる権限昇格脆弱性デモ)
    # PostgreSQL BOOLEAN型対応
    admin_check = is_admin.lower() in ['true', '1', 'yes']
    
    if admin_check:
        try:
            # 統計情報をPostgreSQLから取得
            user_count_result = safe_database_query("SELECT COUNT(*) FROM users", fetch_one=True, default_value=(0,))
            user_count = user_count_result.get('count', 0) if isinstance(user_count_result, dict) else (user_count_result[0] if user_count_result else 0)
            
            order_count_result = safe_database_query("SELECT COUNT(*) FROM orders", fetch_one=True, default_value=(0,))
            order_count = order_count_result.get('count', 0) if isinstance(order_count_result, dict) else (order_count_result[0] if order_count_result else 0)
            
            product_count_result = safe_database_query("SELECT COUNT(*) FROM products", fetch_one=True, default_value=(0,))
            product_count = product_count_result.get('count', 0) if isinstance(product_count_result, dict) else (product_count_result[0] if product_count_result else 0)
            
            review_count_result = safe_database_query("SELECT COUNT(*) FROM reviews", fetch_one=True, default_value=(0,))
            review_count = review_count_result.get('count', 0) if isinstance(review_count_result, dict) else (review_count_result[0] if review_count_result else 0)
            
            return render_template('admin/dashboard.html', 
                                 user_count=user_count,
                                 order_count=order_count,
                                 product_count=product_count,
                                 review_count=review_count,
                                 current_role=role,
                                 is_admin=is_admin)
        except Exception as e:
            return f"管理者ダッシュボードのロード中にエラーが発生しました: {str(e)}"
    else:
        return "管理者権限が必要です"

@bp.route('/admin/users')
def admin_users():
    """ユーザー管理"""
    is_admin = request.cookies.get('is_admin', 'false')
    
    # PostgreSQL BOOLEAN型対応
    admin_check = is_admin.lower() in ['true', '1', 'yes']
    
    if admin_check:
        try:
            search = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            per_page = 20
            
            if search:
                # SQLインジェクション脆弱性を保持しつつPostgreSQL対応
                all_users_raw = safe_database_query(
                    f"SELECT id, username, email, address, phone, is_admin, created_at FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%' ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            else:
                all_users_raw = safe_database_query(
                    "SELECT id, username, email, address, phone, is_admin, created_at FROM users ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            
            # テンプレート互換性のため配列形式に変換
            all_users = []
            for i, user in enumerate(all_users_raw or [], 1):
                if isinstance(user, dict):
                    user_array = [
                        user.get('id', 0),              # 0: ID
                        user.get('username', ''),       # 1: ユーザーID(username)
                        user.get('email', ''),          # 2: メールアドレス
                        user.get('address', ''),        # 3: 住所
                        user.get('phone', ''),          # 4: 電話番号
                        user.get('is_admin', False),    # 5: 管理者
                        user.get('created_at', '')      # 6: 作成日
                    ]
                    all_users.append(user_array)
            
            # ページング計算
            total = len(all_users)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            users = all_users[start_idx:end_idx]
            
            return render_template('admin/users.html', 
                                 users=users, 
                                 search=search, 
                                 page=page, 
                                 total_pages=total_pages,
                                 total=total)
        except Exception as e:
            return f"ユーザー管理画面のロード中にエラーが発生しました: {str(e)}"
    
    return "管理者権限が必要です"

@bp.route('/admin/users/delete/<int:user_id>')
def delete_user(user_id):
    """ユーザー削除"""
    is_admin = request.cookies.get('is_admin', '0')
    
    if is_admin.lower() in ['true', '1', 'yes']:
        try:
            # 関連データをカスケード削除
            # 1. ユーザーの注文に関連するorder_itemsを削除
            safe_database_query("""
                DELETE FROM order_items 
                WHERE order_id IN (
                    SELECT id FROM orders WHERE user_id = %s
                )
            """, (user_id,))
            
            # 2. ユーザーの注文を削除
            safe_database_query(
                "DELETE FROM orders WHERE user_id = %s",
                (user_id,)
            )
            
            # 3. ユーザーのレビューを削除
            safe_database_query(
                "DELETE FROM reviews WHERE user_id = %s",
                (user_id,)
            )
            
            # 4. ユーザーのカートを削除
            safe_database_query(
                "DELETE FROM cart WHERE user_id = %s",
                (user_id,)
            )
            
            # 5. ユーザーのメールを削除
            safe_database_query(
                "DELETE FROM emails WHERE sender_id = %s OR recipient_id = %s",
                (user_id, user_id)
            )
            
            # 6. 最後にユーザーを削除
            safe_database_query(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            
            flash('ユーザーと関連データを削除しました', 'success')
            return redirect('/admin/users')
        except Exception as e:
            flash(f'ユーザー削除エラー: {str(e)}', 'danger')
            return redirect('/admin/users')
    
    return "管理者権限が必要です"

@bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """ユーザー編集"""
    is_admin = request.cookies.get('is_admin', '0')
    
    if is_admin.lower() in ['true', '1', 'yes']:
        try:
            if request.method == 'POST':
                email = request.form.get('email')
                address = request.form.get('address')
                phone = request.form.get('phone')
                is_admin_check = request.form.get('is_admin') == 'on'
                new_password = request.form.get('new_password')
                
                blocked_chars = ['><', '<script', '</script', 'javascript:', 'onclick', 'onload', '/', '-']
                for blocked in blocked_chars:
                    if address and blocked.lower() in address.lower():
                        user_dict = safe_database_query(
                            "SELECT id, username, email, address, phone, is_admin, created_at FROM users WHERE id = %s",
                            (user_id,),
                            fetch_one=True
                        )
                        user = [
                            user_dict.get('id', ''),
                            user_dict.get('username', ''), 
                            user_dict.get('email', ''),
                            address,
                            user_dict.get('phone', ''),
                            user_dict.get('is_admin', False),
                            user_dict.get('created_at', '')
                        ]
                        return render_template('admin/edit_user.html', user=user, error_address=address)
                
                phone_blocked_chars = ['>', '<', '"']
                for blocked in phone_blocked_chars:
                    if phone and blocked.lower() in phone.lower():
                        user_dict = safe_database_query(
                            "SELECT id, username, email, address, phone, is_admin, created_at FROM users WHERE id = %s",
                            (user_id,),
                            fetch_one=True
                        )
                        user = [
                            user_dict.get('id', ''),
                            user_dict.get('username', ''), 
                            user_dict.get('email', ''),
                            user_dict.get('address', ''),
                            phone,
                            user_dict.get('is_admin', False),
                            user_dict.get('created_at', '')
                        ]
                        return render_template('admin/edit_user.html', user=user, error_phone=phone)
                
                if new_password:
                    safe_database_query(
                        "UPDATE users SET email=%s, address=%s, phone=%s, is_admin=%s, password=%s WHERE id=%s",
                        (email, address, phone, is_admin_check, new_password, user_id)
                    )
                else:
                    safe_database_query(
                        "UPDATE users SET email=%s, address=%s, phone=%s, is_admin=%s WHERE id=%s",
                        (email, address, phone, is_admin_check, user_id)
                    )
                
                flash('ユーザーを更新しました', 'success')
                return redirect('/admin/users')
            
            # ユーザー情報を取得
            user_dict = safe_database_query(
                "SELECT id, username, email, address, phone, is_admin, created_at FROM users WHERE id = %s",
                (user_id,),
                fetch_one=True
            )
            
            if user_dict:
                # dict形式をarray形式に変換 (テンプレートの期待順序に合わせる)
                user = [
                    user_dict.get('id', ''),              # 0: ID
                    user_dict.get('username', ''),        # 1: ユーザーID(username)
                    user_dict.get('email', ''),           # 2: メールアドレス 
                    user_dict.get('address', ''),         # 3: 住所
                    user_dict.get('phone', ''),           # 4: 電話番号
                    user_dict.get('is_admin', False),     # 5: 管理者
                    user_dict.get('created_at', '')       # 6: 作成日
                ]
                return render_template('admin/edit_user.html', user=user)
            else:
                flash('ユーザーが見つかりません', 'danger')
                return redirect('/admin/users')
        except Exception as e:
            flash(f'ユーザー編集エラー: {str(e)}', 'danger')
            return redirect('/admin/users')
    
    return "管理者権限が必要です"

@bp.route('/admin/orders')
def admin_orders():
    """注文管理"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            page = request.args.get('page', 1, type=int)
            search = request.args.get('search', '')
            per_page = 20
            
            print("Starting order data retrieval...")
            
            # 検索機能付きの注文データを取得 (SQLi脆弱性)
            if search:
                # 注文検索専用ブロックリスト
                search_blocked_chars = ['"', 'or', 'and', 'select', 'order', 'by', '-', '#', '/', 
                                       '%20', '%22', '%6f%72', '%6F%72', '%61%6e%64', '%61%6E%64', 
                                       '%73%65%6c%65%63%74', '%73%65%6C%65%63%74']
                for blocked in search_blocked_chars:
                    if blocked.lower() in search.lower():
                        return f"注文検索で禁止された文字列が検出されました"
                
                # 脆弱なクエリ - 直接文字列結合
                query = f"""
                    SELECT o.id, o.user_id, o.total_amount, o.status, 
                           COALESCE(o.shipping_address, '未設定') as shipping_address, 
                           o.created_at,
                           COALESCE(u.username, '不明') as username,
                           COALESCE(u.email, '不明') as user_email
                    FROM orders o 
                    LEFT JOIN users u ON o.user_id = u.id 
                    WHERE u.username LIKE '%{search}%' OR o.shipping_address LIKE '%{search}%'
                    ORDER BY o.id ASC
                """
                try:
                    from app.utils import db_manager
                    orders_raw = db_manager.execute_query(query, fetch_all=True)
                except Exception as e:
                    # エラー時は特別なマーカーを含む空の結果を返す
                    print(f"SQL Error: {e}")
                    orders_raw = [{'error': True, 'message': str(e)}]
            else:
                orders_raw = safe_database_query("""
                    SELECT o.id, o.user_id, o.total_amount, o.status, 
                           COALESCE(o.shipping_address, '未設定') as shipping_address, 
                           o.created_at,
                           COALESCE(u.username, '不明') as username,
                           COALESCE(u.email, '不明') as user_email
                    FROM orders o 
                    LEFT JOIN users u ON o.user_id = u.id 
                    ORDER BY o.id ASC
                """, fetch_all=True, default_value=[])
            
            print(f"Orders raw data: {orders_raw}")  # デバッグ用
            
            # テンプレート互換性のため配列形式に変換
            all_orders = []
            if orders_raw and isinstance(orders_raw, list):
                # SQLエラーの場合は特別な処理
                if len(orders_raw) > 0 and isinstance(orders_raw[0], dict) and orders_raw[0].get('error'):
                    return f"データベースエラーが発生しました: {orders_raw[0].get('message', '不明なエラー')}"
                
                for order in orders_raw:
                    if isinstance(order, dict):
                        order_array = [
                            order.get('id', 0),                     # 0: 注文ID
                            order.get('username', '不明'),        # 1: ユーザー名(username)
                            order.get('shipping_address', '未設定'), # 2: 配送先
                            '未設定',                               # 3: 支払い方法(固定値)
                            order.get('total_amount', 0),           # 4: 合計金額
                            order.get('status', '未確定'),           # 5: ステータス
                            order.get('created_at', ''),            # 6: 注文日
                            order.get('user_id', 0)                 # 7: ユーザーID(非表示)
                        ]
                        all_orders.append(order_array)
            
            print(f"All orders processed: {len(all_orders)} orders")  # デバッグ用
            
            # ページング
            total = len(all_orders)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            orders = all_orders[start_idx:end_idx]
            
            return render_template('admin/orders.html', 
                                 orders=orders, 
                                 page=page, 
                                 total_pages=total_pages,
                                 total=total)
        except Exception as e:
            return f"注文管理画面のロード中にエラーが発生しました: {str(e)}"
    
    return "管理者権限が必要です"

@bp.route('/admin/orders/edit/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    """注文編集"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            if request.method == 'POST':
                shipping_address = request.form.get('shipping_address')
                total_amount = request.form.get('total_amount')
                status = request.form.get('status')
                
                safe_database_query(
                    "UPDATE orders SET shipping_address=%s, total_amount=%s, status=%s WHERE id=%s",
                    (shipping_address, total_amount, status, order_id)
                )
                
                flash('注文を更新しました', 'success')
                return redirect('/admin/orders')
            
            # 注文情報を取得 (実際に存在するカラムのみ)
            order_dict = safe_database_query(
                "SELECT o.id, o.user_id, o.total_amount, o.status, COALESCE(o.shipping_address, '未設定') as shipping_address, o.created_at, COALESCE(u.username, '不明') as username, COALESCE(u.email, '不明') as user_email FROM orders o LEFT JOIN users u ON o.user_id = u.id WHERE o.id = %s",
                (order_id,),
                fetch_one=True
            )
            
            if order_dict:
                # dict形式をarray形式に変換 (テンプレートの期待順序に合わせる)
                order = [
                    order_dict.get('id', ''),                    # 0: ID
                    order_dict.get('user_id', ''),               # 1: ユーザーID
                    order_dict.get('shipping_address', ''),      # 2: 配送先
                    '未設定',                                   # 3: 支払い方法(固定値)
                    order_dict.get('total_amount', ''),          # 4: 合計金額
                    order_dict.get('status', ''),                # 5: ステータス
                    order_dict.get('created_at', ''),            # 6: 作成日
                    order_dict.get('user_email', ''),            # 7: ユーザーメール
                    order_dict.get('username', '')               # 8: ユーザー名
                ]
                return render_template('admin/edit_order.html', order=order)
            else:
                flash('注文が見つかりません', 'danger')
                return redirect('/admin/orders')
        except Exception as e:
            flash(f'注文編集エラー: {str(e)}', 'danger')
            return redirect('/admin/orders')
    
    return "管理者権限が必要です"

@bp.route('/admin/orders/delete/<int:order_id>')
def delete_order(order_id):
    """注文削除"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            # 関連するorder_itemsを先に削除
            safe_database_query(
                "DELETE FROM order_items WHERE order_id = %s",
                (order_id,)
            )
            
            # 注文を削除
            result = safe_database_query(
                "DELETE FROM orders WHERE id = %s",
                (order_id,)
            )
            
            flash('注文と関連アイテムを削除しました', 'success')
            return redirect('/admin/orders')
        except Exception as e:
            flash(f'注文削除エラー: {str(e)}', 'danger')
            return redirect('/admin/orders')
    
    return "管理者権限が必要です"

@bp.route('/admin/products')
def admin_products():
    """商品管理"""
    is_admin = request.cookies.get('is_admin', 'false')
    admin_check = is_admin.lower() in ['true', '1', 'yes']
    
    if admin_check:
        try:
            search = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            per_page = 20
            
            print(f"Products page request: page={page}, search={search}")
            
            if search:
                # 商品検索専用ブロックリスト
                product_blocked_chars = ['and', 'or', '%20', '%0a', 'sleep', 'pg', 'select']
                for blocked in product_blocked_chars:
                    if blocked.lower() in search.lower():
                        return f"商品検索で禁止された文字列が検出されました"
                
                products_raw = safe_database_query(
                    f"SELECT id, name, description, price, stock, category, image_url, created_at FROM products WHERE name LIKE '%{search}%' OR category LIKE '%{search}%' ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            else:
                products_raw = safe_database_query(
                    "SELECT id, name, description, price, stock, category, image_url, created_at FROM products ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            
            print(f"Products raw data: {len(products_raw) if products_raw else 0} products")  # デバッグ
            
            # テンプレート互換性のため配列形式に変換
            all_products = []
            if products_raw and isinstance(products_raw, list):
                for i, product in enumerate(products_raw, 1):
                    if isinstance(product, dict):
                        product_array = [
                            i,  # 0: row_num
                            product.get('id', 0),               # 1: ID
                            product.get('name', ''),            # 2: 名前
                            product.get('description', ''),     # 3: 説明
                            float(product.get('price', 0)) if product.get('price') is not None else 0.0,  # 4: 価格
                            product.get('stock', 0),            # 5: 在庫
                            product.get('category', ''),        # 6: カテゴリ
                            product.get('image_url', ''),       # 7: 画像URL
                            product.get('created_at', '')       # 8: 作成日
                        ]
                        all_products.append(product_array)
            
            print(f"Products processed: {len(all_products)} products")  # デバッグ
            
            # ページング計算
            total = len(all_products)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            products = all_products[start_idx:end_idx]
            
            return render_template('admin/products.html', 
                                 products=products, 
                                 search=search, 
                                 page=page, 
                                 total_pages=total_pages,
                                 total=total)
        except Exception as e:
            return f"商品管理画面のロード中にエラーが発生しました: {str(e)}"
    
    return "管理者権限が必要です"

@bp.route('/admin/products/delete/<int:product_id>')
def delete_product(product_id):
    """商品削除 - IDOR脆弱性"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            # IDOR脆弱性: 権限チェックなしで削除
            safe_database_query(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )
            
            flash('商品を削除しました', 'success')
            return redirect('/admin/products')
        except Exception as e:
            flash(f'商品削除エラー: {str(e)}', 'danger')
            return redirect('/admin/products')
    
    return "管理者権限が必要です"

@bp.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    """商品追加"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        if request.method == 'POST':
            try:
                # 商品追加における脆弱性実装
                name = request.form.get('name', '')
                description = request.form.get('description', '')
                price = request.form.get('price')
                stock = request.form.get('stock')
                category = request.form.get('category', '')
                
                # バリデーションエラーメッセージ
                validation_errors = []
                
                # name: 18文字制限、サニタイズなし
                if len(name) > 18:
                    validation_errors.append('商品名は18文字以内で入力してください')
                
                # description: サニタイズあり
                import html
                description_sanitized = html.escape(description)
                
                # category: 17文字制限、サニタイズなし
                if len(category) > 17:
                    validation_errors.append('カテゴリは17文字以内で入力してください')
                
                # stock: 17文字制限、サニタイズなし
                stock_str = str(stock) if stock else ''
                if len(stock_str) > 17:
                    validation_errors.append('在庫数は17文字以内で入力してください')
                
                # バリデーションエラーがある場合は追加画面に戻る
                if validation_errors:
                    for error in validation_errors:
                        flash(error, 'danger')
                    return render_template('admin/add_product.html', 
                                         form_data={'name': name, 'description': description, 
                                                  'price': price, 'stock': stock, 'category': category})
                
                file = request.files.get('image')
                image_url = ''
                
                if file:
                    filename = file.filename
                    file_path = os.path.join('app/static/uploads', filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
                
                # name, categoryはサニタイズなし（脆弱性）、descriptionはサニタイズ済み
                result = safe_database_query(
                    "INSERT INTO products (name, description, price, stock, category, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, description_sanitized, price, stock, category, image_url)
                )
                
                flash('商品を追加しました', 'success')
                return redirect('/admin/products')
            except Exception as e:
                flash(f'商品追加エラー: {str(e)}', 'danger')
                return redirect('/admin/products')
        
        return render_template('admin/add_product.html')
    
    return "管理者権限が必要です"

@bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """商品編集"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            if request.method == 'POST':
                # 商品編集における脆弱性実装
                name = request.form.get('name', '')
                description = request.form.get('description', '')
                price = request.form.get('price')
                stock = request.form.get('stock')
                category = request.form.get('category', '')
                
                # バリデーションエラーメッセージ
                validation_errors = []
                
                # name: 18文字制限、サニタイズなし
                if len(name) > 18:
                    validation_errors.append('商品名は18文字以内で入力してください')
                
                # description: サニタイズあり
                import html
                description_sanitized = html.escape(description)
                
                # category: 17文字制限、サニタイズなし
                if len(category) > 17:
                    validation_errors.append('カテゴリは17文字以内で入力してください')
                
                # stock: 17文字制限、サニタイズなし
                stock_str = str(stock) if stock else ''
                if len(stock_str) > 17:
                    validation_errors.append('在庫数は17文字以内で入力してください')
                
                # バリデーションエラーがある場合は編集画面に戻る
                if validation_errors:
                    product_dict = safe_database_query(
                        "SELECT id, name, description, price, stock, category, image_url, created_at FROM products WHERE id = %s",
                        (product_id,),
                        fetch_one=True
                    )
                    
                    if product_dict:
                        product = [
                            product_dict.get('id', ''),
                            name,
                            description,
                            product_dict.get('price', ''),
                            stock,
                            category,
                            product_dict.get('image_url', ''),
                            product_dict.get('created_at', '')
                        ]
                        
                        for error in validation_errors:
                            flash(error, 'danger')
                        
                        return render_template('admin/edit_product.html', product=product)
                
                file = request.files.get('image')
                
                if file and file.filename:
                    filename = file.filename
                    file_path = os.path.join('app/static/uploads', filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
                    safe_database_query(
                        "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, category=%s, image_url=%s WHERE id=%s",
                        (name, description_sanitized, price, stock, category, image_url, product_id)
                    )
                else:
                    safe_database_query(
                        "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, category=%s WHERE id=%s",
                        (name, description_sanitized, price, stock, category, product_id)
                    )
                
                flash('商品を更新しました', 'success')
                return redirect('/admin/products')
            
            # 商品情報を取得
            product_dict = safe_database_query(
                "SELECT id, name, description, price, stock, category, image_url, created_at FROM products WHERE id = %s",
                (product_id,),
                fetch_one=True
            )
            
            if product_dict:
                # dict形式をarray形式に変換
                product = [
                    product_dict.get('id', ''),
                    product_dict.get('name', ''),
                    product_dict.get('description', ''),
                    product_dict.get('price', ''),
                    product_dict.get('stock', ''),
                    product_dict.get('category', ''),
                    product_dict.get('image_url', ''),
                    product_dict.get('created_at', '')
                ]
                return render_template('admin/edit_product.html', product=product)
            else:
                flash('商品が見つかりません', 'danger')
                return redirect('/admin/products')
        except Exception as e:
            flash(f'商品編集エラー: {str(e)}', 'danger')
            return redirect('/admin/products')
    
    return "管理者権限が必要です"

@bp.route('/admin/reviews')
def admin_reviews():
    """レビュー管理"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            # updated_comment パラメーターの文字フィルタリング (JavaScript反射XSS専用)
            updated_comment = request.args.get('updated_comment', '')
            if updated_comment:
                # >, <, - の文字をブロック (HTMLタグやコメントを防ぐ)
                blocked_chars = ['>', '<', '-']
                for char in blocked_chars:
                    if char in updated_comment:
                        # ブロックされた文字が含まれている場合はパラメーターを無効化
                        updated_comment = ''
                        break
            
            search = request.args.get('search', '')
            try:
                page = int(request.args.get('page', '1'))
            except (ValueError, TypeError):
                page = 1
            per_page = 20
            
            if search:
                reviews_raw = safe_database_query(f"""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                           COALESCE(u.email, '不明') as username, COALESCE(p.name, '削除済み') as product_name 
                    FROM reviews r 
                    LEFT JOIN users u ON r.user_id = u.id 
                    LEFT JOIN products p ON r.product_id = p.id 
                    WHERE (p.name LIKE '%{search}%' OR u.email LIKE '%{search}%')
                    ORDER BY r.id ASC
                """, fetch_all=True, default_value=[])
            else:
                reviews_raw = safe_database_query("""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                           COALESCE(u.email, '不明') as username, COALESCE(p.name, '削除済み') as product_name 
                    FROM reviews r 
                    LEFT JOIN users u ON r.user_id = u.id 
                    LEFT JOIN products p ON r.product_id = p.id 
                    ORDER BY r.id ASC
                """, fetch_all=True, default_value=[])
            
            # PostgreSQLの結果をarray形式に変換
            all_reviews = []
            if reviews_raw and isinstance(reviews_raw, list) and len(reviews_raw) > 0:
                for review in reviews_raw:
                    if isinstance(review, dict):
                        review_array = [
                            review.get('id', ''),               # 0: レビューID
                            review.get('username', ''),         # 1: ユーザー名
                            review.get('product_name', ''),     # 2: 商品名
                            int(review.get('rating', 0)) if review.get('rating') else 0,  # 3: 評価（整数）
                            review.get('comment', ''),          # 4: コメント
                            review.get('created_at', ''),       # 5: 作成日
                            review.get('user_id', ''),          # 6: ユーザーID(非表示)
                            review.get('product_id', '')        # 7: 商品ID(非表示)
                        ]
                        all_reviews.append(review_array)
            
            # ページング計算
            total = len(all_reviews) if all_reviews else 0
            total_pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            reviews = all_reviews[start_idx:end_idx] if all_reviews else []
            
            return render_template('admin/reviews.html', 
                                 reviews=reviews, 
                                 search=search, 
                                 page=page, 
                                 total_pages=total_pages,
                                 total=total)
        except Exception as e:
            return f"レビュー管理画面のロード中にエラーが発生しました: {str(e)}"
    
    return "管理者権限が必要です"

@bp.route('/admin/reviews/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    """レビュー編集 - 脆弱なCSRF保護"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            if request.method == 'POST':
                # 脆弱なCSRF検証: 誰のトークンでも有効
                submitted_token = request.form.get('csrf_token')
                
                if submitted_token:
                    # 任意のユーザーの有効なトークンであれば通す
                    is_valid_token = safe_database_query("""
                        SELECT COUNT(*) FROM csrf_tokens 
                        WHERE token = %s AND is_used = 0
                    """, (submitted_token,), fetch_one=True)
                    
                    token_count = is_valid_token.get('count', 0) if isinstance(is_valid_token, dict) else (is_valid_token[0] if is_valid_token else 0)
                    
                    if token_count > 0:
                        # トークンを使用済みにマーク
                        safe_database_query("""
                            UPDATE csrf_tokens 
                            SET is_used = 1 
                            WHERE token = %s
                        """, (submitted_token,))
                        
                        rating = request.form.get('rating')
                        comment = request.form.get('comment', '')
                        
                        # comment パラメータのブロックリスト検証
                        if '<' in comment or '>' in comment:
                            flash('コメントに使用できない文字が含まれています', 'danger')
                            return redirect(f'/admin/reviews/edit/{review_id}')
                        
                        safe_database_query(
                            "UPDATE reviews SET rating=%s, comment=%s WHERE id=%s",
                            (rating, comment, review_id)
                        )
                        
                        flash('レビューを更新しました', 'success')
                        # コメント内容をURLパラメータで渡す
                        from urllib.parse import quote
                        return redirect(f'/admin/reviews?updated_comment={quote(comment or "")}')
                    else:
                        flash('無効なCSRFトークンです', 'danger')
                        return redirect('/admin/reviews')
                else:
                    flash('CSRFトークンが必要です', 'danger')
                    return redirect('/admin/reviews')
            
            # GET時はCSRFトークンを生成
            from app.routes.main import generate_csrf_token
            csrf_token = generate_csrf_token()
            
            # レビュー情報を取得
            review_dict = safe_database_query("""
                SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                       u.username, p.name as product_name 
                FROM reviews r 
                JOIN users u ON r.user_id = u.id 
                JOIN products p ON r.product_id = p.id 
                WHERE r.id = %s
            """, (review_id,), fetch_one=True)
            
            if review_dict:
                # dict形式をarray形式に変換
                review = [
                    1,  # row_num
                    review_dict.get('id', ''),
                    review_dict.get('user_id', ''),
                    review_dict.get('product_id', ''),
                    review_dict.get('rating', ''),
                    review_dict.get('comment', ''),
                    review_dict.get('created_at', ''),
                    review_dict.get('username', ''),
                    review_dict.get('product_name', '')
                ]
                return render_template('admin/edit_review.html', review=review, csrf_token=csrf_token)
            else:
                flash('レビューが見つかりません', 'danger')
                return redirect('/admin/reviews')
        except Exception as e:
            flash(f'レビュー編集エラー: {str(e)}', 'danger')
            return redirect('/admin/reviews')
    
    return "管理者権限が必要です"

@bp.route('/admin/reviews/delete/<int:review_id>', methods=['GET'])
def delete_review(review_id):
    """レビュー削除"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            safe_database_query(
                "DELETE FROM reviews WHERE id = %s",
                (review_id,)
            )
            flash('レビューを削除しました', 'success')
        except Exception as e:
            flash(f'レビュー削除エラー: {str(e)}', 'danger')
        
        return redirect('/admin/reviews')
    
    return "管理者権限が必要です"

@bp.route('/admin/system')
def admin_system():
    """システム情報"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        import subprocess
        import platform
        
        system_info = {
            'os': platform.system(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cwd': os.getcwd(),
            'files': os.listdir('.') if os.path.exists('.') else []
        }
        
        # Pingテスト機能
        ping_result = ""
        target = request.args.get('target', '')
        if target:
            try:
                # OS判定してコマンド変更
                import platform
                import re
                os_type = platform.system().lower()
                
                if os_type == 'windows':
                    # Windows用コマンド
                    cmd = f'ping -n 4 {target}'
                else:
                    # Linux/macOS用コマンド
                    cmd = f'ping -c 4 {target}'
                
                # 脆弱性: コマンドインジェクション（意図的だが制限付き）
                # コマンド制限: 研究目的で安全なコマンドのみ許可
                def filter_dangerous_commands(command_str):
                    """危険なコマンドをフィルタリングし、安全なコマンドのみ許可"""
                    
                    # 許可されるコマンドのホワイトリスト
                    allowed_commands = [
                        'dir', 'ls', 'whoami', 'id', 'pwd', 'echo', 'date', 'time',
                        'hostname', 'uname', 'ping', 'tracert', 'traceroute', 'nslookup',
                        'systeminfo', 'ver', 'cat', 'head', 'tail', 'wc', 'grep',
                        'find', 'locate', 'which', 'where', 'type', 'ps', 'top'
                    ]
                    
                    # 危険なコマンドのブラックリスト
                    dangerous_commands = [
                        'rm', 'del', 'rmdir', 'rd', 'format', 'fdisk', 'mkfs',
                        'dd', 'mv', 'move', 'cp', 'copy', 'chmod', 'chown',
                        'kill', 'killall', 'taskkill', 'shutdown', 'reboot',
                        'halt', 'poweroff', 'init', 'service', 'systemctl',
                        'net', 'netsh', 'iptables', 'firewall-cmd', 'ufw',
                        'wget', 'curl', 'ftp', 'sftp', 'ssh', 'telnet', 'nc',
                        'netcat', 'socat', 'python', 'python3', 'node', 'php',
                        'perl', 'ruby', 'bash', 'sh', 'cmd', 'powershell',
                        'msiexec', 'regsvr32', 'rundll32', 'certutil',
                        'bitsadmin', 'schtasks', 'at', 'crontab', 'mount',
                        'umount', 'fdisk', 'parted', 'lsblk', 'blkid'
                    ]
                    
                    # コマンド文字列を分析
                    import shlex
                    try:
                        # shellexでコマンドを解析
                        tokens = shlex.split(command_str.replace('&', ' ').replace(';', ' ').replace('|', ' '))
                        
                        for token in tokens:
                            # 各トークンが危険なコマンドかチェック
                            cmd_name = token.split()[0] if ' ' in token else token
                            cmd_base = cmd_name.lower().strip()
                            
                            # 危険なコマンドが含まれているかチェック
                            if any(dangerous in cmd_base for dangerous in dangerous_commands):
                                return f"Command '{cmd_base}' is not allowed for security reasons."
                            
                            # パスやスクリプト実行を防ぐ
                            if '/' in cmd_base or '\\' in cmd_base or '.' in cmd_base:
                                if not any(allowed in cmd_base for allowed in allowed_commands):
                                    return f"Path-based execution '{cmd_base}' is not allowed."
                        
                        return None  # 問題なし
                        
                    except Exception:
                        # 解析エラーの場合は安全のため拒否
                        return "Command parsing failed, execution blocked for security."
                
                # コマンドフィルタリングを実行
                filter_result = filter_dangerous_commands(cmd)
                if filter_result:
                    ping_result = f"🚫 {filter_result}"
                else:
                    # 許可されたコマンドのみ実行
                    print(f"[VULN] Executing filtered command: {cmd}")  # デバッグ用
                    result = subprocess.check_output(cmd, shell=True, text=True, timeout=15)
                    ping_result = result
                    
            except subprocess.CalledProcessError as e:
                ping_result = f"Ping command failed (exit code {e.returncode}):\n{e.output if e.output else 'No output'}"
            except subprocess.TimeoutExpired:
                ping_result = f"Ping timeout: Command took longer than 15 seconds"
            except Exception as e:
                ping_result = f"Ping failed: {str(e)}"
        
        return render_template('admin/system.html', 
                             system_info=system_info, 
                             ping_result=ping_result,
                             target=target)
    
    return "管理者権限が必要です"



 