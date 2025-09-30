from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from app.utils import safe_database_query
import os
from werkzeug.utils import secure_filename

bp = Blueprint('user', __name__)

# アップロード設定 (脆弱性テスト用)
UPLOAD_FOLDER = 'app/static/uploads/profiles'
# 危険な拡張子も許可 (脆弱性テスト用)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'php', 'jsp', 'asp', 'exe', 'bat', 'sh', 'txt', 'html', 'js'}

def allowed_file(filename):
    # 脆弱性: 拡張子チェックを無効化
    return True  # すべてのファイルを許可

@bp.route('/user/profile')
def user_profile():
    """ユーザープロフィール"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # SQLインジェクション脆弱性を維持
        query = f"SELECT * FROM users WHERE id = {user_id}"
        user_data = safe_database_query(query, fetch_one=True)
        
        if user_data:
            # テンプレート互換性のため辞書を配列に変換
            user = [
                user_data.get('id', 0),                    # [0]: id
                user_data.get('username', ''),             # [1]: username
                user_data.get('password', ''),             # [2]: password
                user_data.get('email', ''),                # [3]: email
                user_data.get('address', ''),              # [4]: address
                user_data.get('phone', ''),                # [5]: phone
                user_data.get('is_admin', False),          # [6]: is_admin
                user_data.get('created_at', ''),           # [7]: created_at
                user_data.get('profile_image', None),      # [8]: profile_image
            ]
        else:
            user = None
        
        return render_template('user/profile.html', user=user)
        
    except Exception as e:
        flash(f'プロフィールの取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/')

@bp.route('/user/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """プロフィール編集"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        
        # プロフィール画像アップロード処理 (脆弱性あり)
        profile_image = None
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Vercel対応：読み取り専用ファイルシステムのためファイル保存をスキップ
                filename = file.filename  # secure_filename使わず
                
                # デモ版としてデフォルト画像を使用
                profile_image = f"uploads/profiles/default.jpg"
                
                flash(f'ファイル {filename} を受け取りました（デモ版）', 'info')
        
        try:
            # プロフィール更新
            if profile_image:
                safe_database_query(
                    "UPDATE users SET email = %s, address = %s, phone = %s, profile_image = %s WHERE id = %s", 
                    (email, address, phone, profile_image, user_id)
                )
            else:
                safe_database_query(
                    "UPDATE users SET email = %s, address = %s, phone = %s WHERE id = %s", 
                    (email, address, phone, user_id)
                )
            
            flash('プロフィールを更新しました', 'success')
            return redirect('/user/profile')
            
        except Exception as e:
            flash(f'プロフィール更新中にエラーが発生しました: {str(e)}', 'error')
            return redirect('/user/profile')
    
    try:
        query = f"SELECT * FROM users WHERE id = {user_id}"
        user_data = safe_database_query(query, fetch_one=True)
        
        if user_data:
            # テンプレート互換性のため辞書を配列に変換
            user = [
                user_data.get('id', 0),                    # [0]: id
                user_data.get('username', ''),             # [1]: username
                user_data.get('password', ''),             # [2]: password
                user_data.get('email', ''),                # [3]: email
                user_data.get('address', ''),              # [4]: address
                user_data.get('phone', ''),                # [5]: phone
                user_data.get('is_admin', False),          # [6]: is_admin
                user_data.get('created_at', ''),           # [7]: created_at
                user_data.get('profile_image', None),      # [8]: profile_image
            ]
        else:
            user = None
            
        return render_template('user/edit_profile.html', user=user)
        
    except Exception as e:
        flash(f'プロフィール情報の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/')

# 脆弱性: 任意のファイルダウンロードが可能
@bp.route('/uploads/profiles/<filename>')
def download_file(filename):
    """ファイルダウンロード (脆弱性あり)"""
    # 脆弱性: パストラバーサル攻撃が可能
    file_path = os.path.join('app/static/uploads/profiles', filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 脆弱性: Content-Typeを適切に設定しない
        return content, 200, {'Content-Type': 'application/octet-stream'}
    else:
        flash('ファイルが見つかりません', 'error')
        return redirect('/user/profile')

@bp.route('/user/change_password', methods=['GET', 'POST'])
def change_password():
    """パスワード変更 (脆弱性含む)"""
    if 'user_id' not in session:
        flash('ログインが必要です', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password:
            flash('現在のパスワードと新しいパスワードを入力してください', 'error')
            return render_template('user/change_password.html')
        
        if new_password != confirm_password:
            flash('新しいパスワードが一致しません', 'error')
            return render_template('user/change_password.html')
        
        if len(new_password) < 6:
            flash('パスワードは6文字以上で入力してください', 'error')
            return render_template('user/change_password.html')
        
        try:
            # 現在のパスワード確認
            query = f"SELECT password FROM users WHERE id = {user_id}"
            user_data = safe_database_query(query, fetch_one=True)
            
            if not user_data:
                flash('ユーザーが見つかりません', 'error')
                return render_template('user/change_password.html')
            
            # 脆弱性: 平文パスワード比較
            if user_data['password'] != current_password:
                flash('現在のパスワードが正しくありません', 'error')
                return render_template('user/change_password.html')
            
            # パスワード更新 - SQLインジェクション脆弱性を維持
            update_query = f"UPDATE users SET password = '{new_password}' WHERE id = {user_id}"
            safe_database_query(update_query)
            
            flash('パスワードを変更しました', 'success')
            return redirect('/user/profile')
            
        except Exception as e:
            flash(f'パスワード変更中にエラーが発生しました: {str(e)}', 'error')
            return render_template('user/change_password.html') 