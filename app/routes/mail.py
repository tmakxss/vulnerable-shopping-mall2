from flask import Blueprint, request, render_template, session, redirect, flash, send_file
from app.utils import safe_database_query
import os
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('mail', __name__)

# 脆弱な設定 (学習用)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'attachments')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'php', 'jsp', 'asp', 'exe', 'bat', 'sh'}

def allowed_file(filename):
    # 脆弱性: すべてのファイルを許可
    return True

@bp.route('/mail/compose', methods=['GET', 'POST'])
def compose_mail():
    """メール作成 (添付ファイル含む)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        recipient_username = request.form.get('recipient')
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        try:
            # 受信者を探す
            recipient_data = safe_database_query(
                "SELECT id FROM users WHERE username = %s", 
                (recipient_username,), fetch_one=True
            )
            
            if recipient_data:
                # メールを保存
                safe_database_query("""
                    INSERT INTO emails (sender_id, recipient_id, subject, body) 
                    VALUES (%s, %s, %s, %s)
                """, (session['user_id'], recipient_data['id'], subject, content))
                
                # 添付ファイル処理 (脆弱性含む)
                if 'attachments' in request.files:
                    files = request.files.getlist('attachments')
                    
                    for file in files:
                        if file and file.filename != '':
                            # 脆弱性: ファイル名検証なし
                            original_filename = file.filename
                            stored_filename = f"{uuid.uuid4()}_{original_filename}"
                            
                            # 脆弱性: Directory Traversal可能
                            file_path = os.path.join(UPLOAD_FOLDER, stored_filename)
                            
                            # ディレクトリ作成
                            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                            
                            # ファイル保存
                            file.save(file_path)
                            
                            flash(f'添付ファイル {original_filename} をアップロードしました', 'info')
                
                flash('メールを送信しました', 'success')
                return redirect('/mail/sent')
            else:
                flash('受信者が見つかりません', 'error')
                
        except Exception as e:
            flash(f'メールの送信中にエラーが発生しました: {str(e)}', 'error')
    
    return render_template('mail/compose.html')

@bp.route('/mail/inbox')
def inbox():
    """受信メールボックス"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # 受信メールを取得
        emails_data = safe_database_query("""
            SELECT e.*, u.username as sender_name
            FROM emails e 
            JOIN users u ON e.sender_id = u.id 
            WHERE e.recipient_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True)
        
        return render_template('mail/inbox.html', emails=emails_data)
        
    except Exception as e:
        flash(f'受信メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return render_template('mail/inbox.html', emails=[])
        return render_template('mail/inbox.html', emails=emails)
    except Exception as e:
        flash(f'メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/')
    finally:
        if conn:
            conn.close()

@bp.route('/mail/sent')
def sent_mail():
    """送信メールボックス"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # 送信メールを取得
        emails_data = safe_database_query("""
            SELECT e.*, u.username as recipient_name
            FROM emails e 
            JOIN users u ON e.recipient_id = u.id 
            WHERE e.sender_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True)
        
        return render_template('mail/sent.html', emails=emails_data)
        
    except Exception as e:
        flash(f'送信メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return render_template('mail/sent.html', emails=[])

@bp.route('/mail/read/<int:email_id>')
def read_mail(email_id):
    """メール読み取り"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # メール情報を取得
        email_data = safe_database_query("""
            SELECT e.*, 
                   sender.username as sender_name,
                   recipient.username as recipient_name
            FROM emails e 
            JOIN users sender ON e.sender_id = sender.id 
            JOIN users recipient ON e.recipient_id = recipient.id 
            WHERE e.id = %s AND (e.sender_id = %s OR e.recipient_id = %s)
        """, (email_id, user_id, user_id), fetch_one=True)
        
        if not email_data:
            flash('メールが見つかりません', 'error')
            return redirect('/mail/inbox')
        
        # 既読フラグを更新
        if email_data['recipient_id'] == user_id:
            safe_database_query(
                "UPDATE emails SET is_read = TRUE WHERE id = %s", 
                (email_id,)
            )
        
        return render_template('mail/read.html', email=email_data)
        
    except Exception as e:
        flash(f'メールの読み込み中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')
        cursor = conn.cursor()
        
        # メールを取得
        cursor.execute("""
            SELECT e.*, u.username as sender_name
            FROM emails e 
            JOIN users u ON e.sender_id = u.id 
            WHERE e.id = ? AND (e.recipient_id = ? OR e.sender_id = ?)
        """, (email_id, user_id, user_id))
        
        email = cursor.fetchone()
        
        if email:
            # 添付ファイルを取得
            cursor.execute("""
                SELECT * FROM email_attachments WHERE email_id = ?
            """, (email_id,))
            
            attachments = cursor.fetchall()
            
            # 既読マーク (受信者の場合)
            if email[2] == user_id:  # recipient_id
                cursor.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (email_id,))
                conn.commit()
            
            return render_template('mail/read.html', email=email, attachments=attachments)
        else:
            flash('メールが見つかりません', 'error')
            return redirect('/mail/inbox')
    except Exception as e:
        flash(f'メールの読み取り中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')
    finally:
        if conn:
            conn.close()

@bp.route('/mail/attachment/<int:attachment_id>')
def download_attachment(attachment_id):
    """添付ファイルダウンロード (脆弱性含む)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = None
    try:
        conn = sqlite3.connect('database/shop.db')
        cursor = conn.cursor()
        
        # 添付ファイル情報を取得
        cursor.execute("""
            SELECT ea.*, e.sender_id, e.recipient_id 
            FROM email_attachments ea
            JOIN emails e ON ea.email_id = e.id
            WHERE ea.id = ?
        """, (attachment_id,))
        
    except Exception as e:
        flash(f'ファイルダウンロード中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')