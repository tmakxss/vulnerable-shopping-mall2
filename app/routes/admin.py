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
                    f"SELECT id, username, email, address, phone, is_admin, created_at FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%' ORDER BY created_at ASC",
                    fetch_all=True, default_value=[]
                )
            else:
                all_users_raw = safe_database_query(
                    "SELECT id, username, email, address, phone, is_admin, created_at FROM users ORDER BY created_at ASC",
                    fetch_all=True, default_value=[]
                )
            
            # テンプレート互換性のため配列形式に変換
            all_users = []
            for i, user in enumerate(all_users_raw or [], 1):
                if isinstance(user, dict):
                    user_array = [
                        i,  # row_num
                        user.get('id', 0),
                        user.get('username', ''),
                        user.get('email', ''),
                        user.get('address', ''),
                        user.get('phone', ''),
                        user.get('is_admin', False),
                        user.get('created_at', '')
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
            # PostgreSQLでユーザー削除
            result = safe_database_query(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            
            flash('ユーザーを削除しました', 'success')
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
                username = request.form.get('username')
                email = request.form.get('email')
                address = request.form.get('address')
                phone = request.form.get('phone')
                is_admin_check = request.form.get('is_admin') == 'on'
                new_password = request.form.get('new_password')
                
                if new_password:
                    safe_database_query(
                        "UPDATE users SET username=%s, email=%s, address=%s, phone=%s, is_admin=%s, password=%s WHERE id=%s",
                        (username, email, address, phone, is_admin_check, new_password, user_id)
                    )
                else:
                    safe_database_query(
                        "UPDATE users SET username=%s, email=%s, address=%s, phone=%s, is_admin=%s WHERE id=%s",
                        (username, email, address, phone, is_admin_check, user_id)
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
                # dict形式をarray形式に変換
                user = [
                    user_dict.get('id', ''),
                    user_dict.get('username', ''),
                    user_dict.get('email', ''),
                    user_dict.get('address', ''),
                    user_dict.get('phone', ''),
                    user_dict.get('is_admin', 0),
                    user_dict.get('created_at', '')
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
    is_admin = request.cookies.get('is_admin', 'false')
    admin_check = is_admin.lower() in ['true', '1', 'yes']
    
    if admin_check:
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 20
            
            # 注文データを取得
            orders_raw = safe_database_query("""
                SELECT o.id, o.user_id, o.total_amount, o.status, o.shipping_address, o.created_at,
                       u.username
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            """, fetch_all=True, default_value=[])
            
            # テンプレート互換性のため配列形式に変換
            all_orders = []
            for order in orders_raw or []:
                if isinstance(order, dict):
                    order_array = [
                        order.get('id', 0),
                        order.get('user_id', 0),
                        order.get('total_amount', 0),
                        order.get('status', ''),
                        order.get('shipping_address', ''),
                        order.get('created_at', ''),
                        order.get('username', '')
                    ]
                    all_orders.append(order_array)
            
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
                payment_method = request.form.get('payment_method')
                total_amount = request.form.get('total_amount')
                status = request.form.get('status')
                
                safe_database_query(
                    "UPDATE orders SET shipping_address=%s, payment_method=%s, total_amount=%s, status=%s WHERE id=%s",
                    (shipping_address, payment_method, total_amount, status, order_id)
                )
                
                flash('注文を更新しました', 'success')
                return redirect('/admin/orders')
            
            # 注文情報を取得
            order_dict = safe_database_query(
                "SELECT o.id, o.user_id, o.total_amount, o.status, o.shipping_address, o.payment_method, o.created_at, u.username FROM orders o JOIN users u ON o.user_id = u.id WHERE o.id = %s",
                (order_id,),
                fetch_one=True
            )
            
            if order_dict:
                # dict形式をarray形式に変換
                order = [
                    order_dict.get('id', ''),
                    order_dict.get('user_id', ''),
                    order_dict.get('total_amount', ''),
                    order_dict.get('status', ''),
                    order_dict.get('shipping_address', ''),
                    order_dict.get('payment_method', ''),
                    order_dict.get('created_at', ''),
                    order_dict.get('username', '')
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
            safe_database_query(
                "DELETE FROM orders WHERE id = %s",
                (order_id,)
            )
            
            flash('注文を削除しました', 'success')
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
            
            if search:
                products_raw = safe_database_query(
                    f"SELECT id, name, description, price, stock, category, image_url, created_at FROM products WHERE name LIKE '%{search}%' OR category LIKE '%{search}%' ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            else:
                products_raw = safe_database_query(
                    "SELECT id, name, description, price, stock, category, image_url, created_at FROM products ORDER BY id ASC",
                    fetch_all=True, default_value=[]
                )
            
            # テンプレート互換性のため配列形式に変換
            all_products = []
            for i, product in enumerate(products_raw or [], 1):
                if isinstance(product, dict):
                    product_array = [
                        i,  # row_num
                        product.get('id', 0),
                        product.get('name', ''),
                        product.get('description', ''),
                        float(product.get('price', 0)) if product.get('price') is not None else 0.0,
                        product.get('stock', 0),
                        product.get('category', ''),
                        product.get('image_url', ''),
                        product.get('created_at', '')
                    ]
                    all_products.append(product_array)
            
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
                name = request.form.get('name')
                description = request.form.get('description')
                price = request.form.get('price')
                stock = request.form.get('stock')
                category = request.form.get('category')
                
                file = request.files.get('image')
                image_url = ''
                
                if file:
                    filename = file.filename
                    file_path = os.path.join('app/static/uploads', filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
                
                safe_database_query(
                    "INSERT INTO products (name, description, price, stock, category, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, description, price, stock, category, image_url)
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
                name = request.form.get('name')
                description = request.form.get('description')
                price = request.form.get('price')
                stock = request.form.get('stock')
                category = request.form.get('category')
                
                file = request.files.get('image')
                
                if file and file.filename:
                    filename = file.filename
                    file_path = os.path.join('app/static/uploads', filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
                    safe_database_query(
                        "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, category=%s, image_url=%s WHERE id=%s",
                        (name, description, price, stock, category, image_url, product_id)
                    )
                else:
                    safe_database_query(
                        "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, category=%s WHERE id=%s",
                        (name, description, price, stock, category, product_id)
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
            search = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            per_page = 20
            
            if search:
                reviews_raw = safe_database_query(f"""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                           u.username, p.name as product_name 
                    FROM reviews r 
                    JOIN users u ON r.user_id = u.id 
                    JOIN products p ON r.product_id = p.id 
                    WHERE p.name LIKE '%{search}%' OR u.username LIKE '%{search}%'
                    ORDER BY r.id ASC
                """)
            else:
                reviews_raw = safe_database_query("""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, r.created_at,
                           u.username, p.name as product_name 
                    FROM reviews r 
                    JOIN users u ON r.user_id = u.id 
                    JOIN products p ON r.product_id = p.id 
                    ORDER BY r.id ASC
                """)
            
            # PostgreSQLの結果をarray形式に変換
            all_reviews = []
            if reviews_raw:
                for i, review in enumerate(reviews_raw):
                    if isinstance(review, dict):
                        all_reviews.append([
                            i + 1,  # row_num
                            review.get('id', ''),
                            review.get('user_id', ''),
                            review.get('product_id', ''),
                            review.get('rating', ''),
                            review.get('comment', ''),
                            review.get('created_at', ''),
                            review.get('username', ''),
                            review.get('product_name', '')
                        ])
            
            # ページング計算
            total = len(all_reviews)
            total_pages = (total + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            reviews = all_reviews[start_idx:end_idx]
            
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
    """レビュー編集"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        try:
            if request.method == 'POST':
                rating = request.form.get('rating')
                comment = request.form.get('comment')
                
                safe_database_query(
                    "UPDATE reviews SET rating=%s, comment=%s WHERE id=%s",
                    (rating, comment, review_id)
                )
                
                flash('レビューを更新しました', 'success')
                return redirect('/admin/reviews')
            
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
                return render_template('admin/edit_review.html', review=review)
            else:
                flash('レビューが見つかりません', 'danger')
                return redirect('/admin/reviews')
        except Exception as e:
            flash(f'レビュー編集エラー: {str(e)}', 'danger')
            return redirect('/admin/reviews')
    
    return "管理者権限が必要です"

@bp.route('/admin/reviews/delete/<int:review_id>')
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
            return redirect('/admin/reviews')
        except Exception as e:
            flash(f'レビュー削除エラー: {str(e)}', 'danger')
            return redirect('/admin/reviews')
    
    return "管理者権限が必要です"

@bp.route('/admin/system')
def system_info():
    """システム情報 - Pingtest機能"""
    user_id = request.cookies.get('user_id')
    
    if user_id == '1':
        import subprocess
        import platform
        
        system_info = {
            'os': platform.system(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cwd': os.getcwd(),
            'env_vars': dict(os.environ),
            'files': os.listdir('.') if os.path.exists('.') else []
        }
        
        # Pingテスト機能
        ping_result = ""
        target = request.args.get('target', '')
        if target:
            try:
                # 脆弱性: コマンドインジェクション
                result = subprocess.check_output(f'ping -c 4 {target}', shell=True, text=True, timeout=10)
                ping_result = result
            except Exception as e:
                ping_result = f"Ping failed: {str(e)}"
        
        return render_template('admin/system.html', 
                             system_info=system_info, 
                             ping_result=ping_result,
                             target=target)
    
    return "管理者権限が必要です"



 