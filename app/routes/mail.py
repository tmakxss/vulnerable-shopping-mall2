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
                            
                            # Vercel対応：読み取り専用ファイルシステムのためファイル保存はスキップ
                            # デモ版として添付ファイル受け取りのみ
                            flash(f'添付ファイル {original_filename} を受け取りました（デモ版）', 'info')
                
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
        emails_raw = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at, u.username as sender_name
            FROM emails e 
            JOIN users u ON e.sender_id = u.id 
            WHERE e.recipient_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True, default_value=[])
        
        # テンプレート互換性のため配列形式に変換
        emails_data = []
        for email in emails_raw or []:
            if isinstance(email, dict):
                email_array = [
                    email.get('id', 0),
                    email.get('sender_id', 0),
                    email.get('recipient_id', 0),
                    email.get('subject', ''),
                    email.get('body', ''),
                    email.get('attachment_path', ''),
                    email.get('is_read', False),
                    email.get('created_at', ''),
                    len(email.get('attachment_path', '') or ''),  # 添付ファイル数（簡易判定）
                    email.get('sender_name', '')
                ]
                emails_data.append(email_array)
        
        return render_template('mail/inbox.html', emails=emails_data)
        
    except Exception as e:
        flash(f'受信メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return render_template('mail/inbox.html', emails=emails_data)
        
    except Exception as e:
        flash(f'受信メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return render_template('mail/inbox.html', emails=[])

@bp.route('/mail/sent')
def sent_mail():
    """送信メールボックス"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    try:
        # 送信メールを取得
        sent_emails_raw = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at, u.username as recipient_name
            FROM emails e 
            JOIN users u ON e.recipient_id = u.id 
            WHERE e.sender_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True, default_value=[])
        
        # テンプレート互換性のため配列形式に変換
        sent_emails = []
        for email in sent_emails_raw or []:
            if isinstance(email, dict):
                email_array = [
                    email.get('id', 0),
                    email.get('sender_id', 0),
                    email.get('recipient_id', 0),
                    email.get('subject', ''),
                    email.get('body', ''),
                    email.get('attachment_path', ''),
                    email.get('is_read', False),
                    email.get('created_at', ''),
                    len(email.get('attachment_path', '') or ''),  # 添付ファイル数（簡易判定）
                    email.get('recipient_name', '')
                ]
                sent_emails.append(email_array)
        
        return render_template('mail/sent.html', emails=sent_emails)
        
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
        flash(f'メールの読み込み中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')

@bp.route('/mail/attachment/<int:attachment_id>')
def download_attachment(attachment_id):
    """添付ファイルダウンロード (脆弱性含む)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    # 脆弱性: 添付ファイルの権限チェックなし
    # 任意のファイルダウンロード可能
    try:
        file_path = f"/tmp/attachment_{attachment_id}"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('ファイルが見つかりません', 'error')
            return redirect('/mail/inbox')
            
    except Exception as e:
        flash(f'ファイルダウンロード中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')