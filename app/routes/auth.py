from flask import Blueprint, request, render_template, redirect, session, flash, make_response
from app.utils import safe_database_query
import json
import base64

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページ"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 隠しパラメータによる権限変更 (権限昇格脆弱性)
        role = request.form.get('role', 'user')  # デフォルト値は 'user'
        
        try:
            # SQLインジェクション脆弱性のあるログイン（意図的）
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            user_data = safe_database_query(query, fetch_one=True)
            
            if user_data:
                # 隠しパラメータによる権限変更
                is_admin = False
                if role == 'admin':
                    is_admin = True
                elif role == 'super_admin':
                    is_admin = 2  # スーパー管理者権限
                elif role == 'moderator':
                    is_admin = 3  # モデレーター権限
                else:
                    is_admin = user_data.get('is_admin', False)  # 元の権限を維持
                
                session['user_id'] = user_data.get('id')
                session['username'] = user_data.get('username')
                session['is_admin'] = is_admin
                session['role'] = role  # 役割情報もセッションに保存
                
                # 脆弱なCookie設定
                response = make_response(redirect('/'))
                response.set_cookie('user_id', str(user_data.get('id')), max_age=3600)
                response.set_cookie('username', user_data.get('username'), max_age=3600)
                response.set_cookie('is_admin', str(is_admin), max_age=3600)
                response.set_cookie('role', role, max_age=3600)
                
                # 脆弱なJWT風トークン (Base64エンコード)
                token_data = {
                    'user_id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'is_admin': is_admin,
                    'role': role
                }
                token = base64.b64encode(json.dumps(token_data).encode()).decode()
                response.set_cookie('auth_token', token, max_age=3600)
                
                flash(f'ログインしました (権限: {role})', 'success')
                return response
            else:
                flash('ユーザー名またはパスワードが正しくありません', 'error')
                
        except Exception as e:
            flash(f'ログイン中にエラーが発生しました: {str(e)}', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録ページ"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        try:
            # XSS脆弱性のあるユーザー登録
            safe_database_query(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                (username, password, email)
            )
            flash('ユーザー登録が完了しました', 'success')
            return redirect('/login')
        except Exception as e:
            if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                flash('このユーザー名は既に使用されています', 'error')
            else:
                flash(f'登録中にエラーが発生しました: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    """ログアウト"""
    session.clear()
    flash('ログアウトしました', 'success')
    return redirect('/')

@bp.route('/profile')
def profile():
    """ユーザープロフィール"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # SQLインジェクション脆弱性（意図的）
        user_data = safe_database_query(
            f"SELECT * FROM users WHERE id = {user_id}",
            fetch_one=True
        )
        
        if user_data:
            # 配列形式に変換（テンプレート互換性のため）
            user = [
                user_data.get('id', 0),
                user_data.get('username', ''),
                user_data.get('password', ''),  # パスワードも含む（脆弱性）
                user_data.get('email', ''),
                user_data.get('address', ''),
                user_data.get('phone', ''),
                user_data.get('is_admin', False),
                user_data.get('created_at', '')
            ]
        else:
            user = None
        
        return render_template('auth/profile.html', user=user)
        
    except Exception as e:
        flash(f'プロフィールの取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/') 