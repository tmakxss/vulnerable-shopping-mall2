from flask import Blueprint, request, render_template, render_template_string, session, redirect, flash, send_file
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
        
        # メール本文にブロックフィルターを適用
        filtered_content = filter_mail_content(content)
        
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
                """, (session['user_id'], recipient_data['id'], subject, filtered_content))
                
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
                    email.get('id', 0),                    # [0] - メールID
                    email.get('sender_id', 0),             # [1] - 送信者ID
                    email.get('recipient_id', 0),          # [2] - 受信者ID
                    email.get('subject', ''),              # [3] - 件名
                    email.get('body', ''),                 # [4] - 本文
                    email.get('is_read', False),           # [5] - 既読フラグ
                    email.get('created_at', ''),           # [6] - 作成日時
                    email.get('sender_name', ''),          # [7] - 送信者名
                    1 if email.get('attachment_path') else 0,  # [8] - 添付ファイル数
                    email.get('attachment_path', ''),      # [9] - 添付ファイルパス
                ]
                emails_data.append(email_array)
        
        return render_template('mail/inbox.html', emails=emails_data, render_subject_ssti=render_subject_ssti)
        
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
                    email.get('id', 0),                    # [0] - メールID
                    email.get('sender_id', 0),             # [1] - 送信者ID
                    email.get('recipient_id', 0),          # [2] - 受信者ID
                    email.get('subject', ''),              # [3] - 件名
                    email.get('body', ''),                 # [4] - 本文
                    email.get('is_read', False),           # [5] - 既読フラグ
                    email.get('created_at', ''),           # [6] - 作成日時
                    email.get('recipient_name', ''),       # [7] - 受信者名
                    1 if email.get('attachment_path') else 0,  # [8] - 添付ファイル数
                    email.get('attachment_path', ''),      # [9] - 添付ファイルパス
                ]
                sent_emails.append(email_array)
        
        return render_template('mail/sent.html', emails=sent_emails, render_subject_ssti=render_subject_ssti)
        
    except Exception as e:
        flash(f'送信メールボックスのロード中にエラーが発生しました: {str(e)}', 'error')
        return render_template('mail/sent.html', emails=[])

def sanitize_mailid(mailid):
    """mailidのサニタイズ処理 - 危険な文字を完全にエスケープ"""
    if not mailid:
        return ''
    
    # 危険文字を完全にエスケープ
    sanitized = str(mailid)
    sanitized = sanitized.replace('<', '&lt;')
    sanitized = sanitized.replace('>', '&gt;')
    sanitized = sanitized.replace("'", '&#39;')
    sanitized = sanitized.replace('"', '&quot;')
    sanitized = sanitized.replace('/', '／')  # 全角スラッシュに変換
    sanitized = sanitized.replace('(', '&#x28;')
    sanitized = sanitized.replace(')', '&#x29;')
    
    return sanitized

def filter_mail_content(content):
    """メール本文のブロックフィルター"""
    if not content:
        return content
    
    # 危険なキーワードと文字をブロック
    blocked_patterns = [
        '<script', 'alert', 'prompt', 'console.log', 'confirm',
        'java', '&', '#', '%20', '%09', '%0a'
    ]
    
    filtered_content = str(content)
    for pattern in blocked_patterns:
        if pattern.lower() in filtered_content.lower():
            return "ブロックされたコンテンツが検出されました。"
    
    return filtered_content

def render_subject_ssti(subject):
    """件名のSST脆弱性処理 (Server-Side Template Injection)"""
    if not subject:
        return ''
    
    try:
        # 脆弱性: 件名をJinjaテンプレートとして直接実行
        return render_template_string(str(subject))
    except Exception as e:
        # エラー時は元の件名を返す
        return str(subject)

@bp.route('/mail/read')
def read_mail():
    """メール読み取り - mailidパラメーター使用"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    mailid_params = request.args.getlist('mailid')  # 複数のmailidパラメーターを取得
    
    # パラメーター汚染脆弱性: 複数のmailidがある場合の処理
    if len(mailid_params) > 1:
        # 1つ目のmailidで認証チェック、2つ目のmailidで実際のデータ取得
        auth_mailid = mailid_params[0]
        target_mailid = mailid_params[1]
        
        # 1つ目のmailidで認証チェック
        try:
            auth_email_id = int(auth_mailid)
        except (ValueError, TypeError):
            # 認証用のmailidが無効な場合はエラー
            emails_raw = safe_database_query("""
                SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                       e.attachment_path, e.is_read, e.created_at, u.username as sender_name
                FROM emails e 
                JOIN users u ON e.sender_id = u.id 
                WHERE e.recipient_id = %s 
                ORDER BY e.created_at DESC
            """, (user_id,), fetch_all=True, default_value=[])
            
            emails_data = []
            for email in emails_raw or []:
                if isinstance(email, dict):
                    email_array = [
                        email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                        email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                        email.get('created_at', ''), email.get('sender_name', ''),
                        1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                    ]
                    emails_data.append(email_array)
            
            return render_template('mail/inbox.html', 
                                 emails=emails_data, 
                                 error_alert=True,
                                 error_mailid=sanitize_mailid(auth_mailid),
                                 error_message="無効なメールIDです")
        
        # 1つ目のmailidでアクセス権限確認
        auth_check = safe_database_query("""
            SELECT id FROM emails 
            WHERE id = %s AND (sender_id = %s OR recipient_id = %s)
        """, (auth_email_id, user_id, user_id), fetch_one=True)
        
        if not auth_check:
            # 認証失敗の場合はエラー
            emails_raw = safe_database_query("""
                SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                       e.attachment_path, e.is_read, e.created_at, u.username as sender_name
                FROM emails e 
                JOIN users u ON e.sender_id = u.id 
                WHERE e.recipient_id = %s 
                ORDER BY e.created_at DESC
            """, (user_id,), fetch_all=True, default_value=[])
            
            emails_data = []
            for email in emails_raw or []:
                if isinstance(email, dict):
                    email_array = [
                        email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                        email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                        email.get('created_at', ''), email.get('sender_name', ''),
                        1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                    ]
                    emails_data.append(email_array)
            
            return render_template('mail/inbox.html', 
                                 emails=emails_data, 
                                 error_alert=True,
                                 error_mailid=sanitize_mailid(auth_mailid),
                                 error_message=f"メールID「{auth_mailid}」は存在しません")
        
        # 2つ目のmailidで実際のデータ取得（脆弱性：アクセス制御をバイパス）
        try:
            target_email_id = int(target_mailid)
        except (ValueError, TypeError):
            # ターゲットのmailidが無効な場合はエラー
            emails_raw = safe_database_query("""
                SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                       e.attachment_path, e.is_read, e.created_at, u.username as sender_name
                FROM emails e 
                JOIN users u ON e.sender_id = u.id 
                WHERE e.recipient_id = %s 
                ORDER BY e.created_at DESC
            """, (user_id,), fetch_all=True, default_value=[])
            
            emails_data = []
            for email in emails_raw or []:
                if isinstance(email, dict):
                    email_array = [
                        email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                        email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                        email.get('created_at', ''), email.get('sender_name', ''),
                        1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                    ]
                    emails_data.append(email_array)
            
            return render_template('mail/inbox.html', 
                                 emails=emails_data, 
                                 error_alert=True,
                                 error_mailid=sanitize_mailid(target_mailid),
                                 error_message="無効なメールIDです")
        
        # 脆弱性：2つ目のmailidに対してはアクセス制御チェックをしない
        target_email_data = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at,
                   sender.username as sender_name,
                   recipient.username as recipient_name
            FROM emails e 
            JOIN users sender ON e.sender_id = sender.id 
            JOIN users recipient ON e.recipient_id = recipient.id 
            WHERE e.id = %s
        """, (target_email_id,), fetch_one=True)
        
        if not target_email_data:
            # ターゲットメールが存在しない場合
            emails_raw = safe_database_query("""
                SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                       e.attachment_path, e.is_read, e.created_at, u.username as sender_name
                FROM emails e 
                JOIN users u ON e.sender_id = u.id 
                WHERE e.recipient_id = %s 
                ORDER BY e.created_at DESC
            """, (user_id,), fetch_all=True, default_value=[])
            
            emails_data = []
            for email in emails_raw or []:
                if isinstance(email, dict):
                    email_array = [
                        email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                        email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                        email.get('created_at', ''), email.get('sender_name', ''),
                        1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                    ]
                    emails_data.append(email_array)
            
            return render_template('mail/inbox.html', 
                                 emails=emails_data, 
                                 error_alert=True,
                                 error_mailid=sanitize_mailid(target_mailid),
                                 error_message=f"メールID「{target_mailid}」は存在しません")
        
        # 脆弱性：他人のメールを表示（アクセス制御バイパス成功）
        target_email_array = [
            target_email_data.get('id', 0),                    # [0] - メールID
            target_email_data.get('sender_id', 0),             # [1] - 送信者ID
            target_email_data.get('recipient_id', 0),          # [2] - 受信者ID
            target_email_data.get('subject', ''),              # [3] - 件名
            target_email_data.get('body', ''),                 # [4] - 本文
            target_email_data.get('is_read', False),           # [5] - 既読フラグ
            target_email_data.get('created_at', ''),           # [6] - 作成日時
            target_email_data.get('attachment_path', ''),      # [7] - 添付ファイルパス
            target_email_data.get('sender_name', ''),          # [8] - 送信者名
            target_email_data.get('recipient_name', ''),       # [9] - 受信者名
        ]
        
        return render_template('mail/read.html', email=target_email_array, render_subject_ssti=render_subject_ssti)
    
    # 通常の処理（mailidが1つの場合）
    mailid = request.args.get('mailid', '')
    
    # mailidの検証
    try:
        email_id = int(mailid)
    except (ValueError, TypeError):
        # 無効なmailidの場合、受信メールボックスにエラーテロップ付きで表示
        emails_raw = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at, u.username as sender_name
            FROM emails e 
            JOIN users u ON e.sender_id = u.id 
            WHERE e.recipient_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True, default_value=[])
        
        emails_data = []
        for email in emails_raw or []:
            if isinstance(email, dict):
                email_array = [
                    email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                    email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                    email.get('created_at', ''), email.get('sender_name', ''),
                    1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                ]
                emails_data.append(email_array)
        
        return render_template('mail/inbox.html', 
                             emails=emails_data, 
                             error_alert=True,
                             error_mailid=sanitize_mailid(mailid),  # サニタイズ適用
                             error_message="無効なメールIDです")
    
    try:
        # メール情報を取得
        email_data = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at,
                   sender.username as sender_name,
                   recipient.username as recipient_name
            FROM emails e 
            JOIN users sender ON e.sender_id = sender.id 
            JOIN users recipient ON e.recipient_id = recipient.id 
            WHERE e.id = %s AND (e.sender_id = %s OR e.recipient_id = %s)
        """, (email_id, user_id, user_id), fetch_one=True)
        
        if not email_data:
            # 存在しないmailidの場合、受信メールボックスにエラーテロップ付きで表示
            emails_raw = safe_database_query("""
                SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                       e.attachment_path, e.is_read, e.created_at, u.username as sender_name
                FROM emails e 
                JOIN users u ON e.sender_id = u.id 
                WHERE e.recipient_id = %s 
                ORDER BY e.created_at DESC
            """, (user_id,), fetch_all=True, default_value=[])
            
            emails_data = []
            for email in emails_raw or []:
                if isinstance(email, dict):
                    email_array = [
                        email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                        email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                        email.get('created_at', ''), email.get('sender_name', ''),
                        1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                    ]
                    emails_data.append(email_array)
            
            return render_template('mail/inbox.html', 
                                 emails=emails_data, 
                                 error_alert=True,
                                 error_mailid=sanitize_mailid(mailid),  # サニタイズ適用
                                 error_message=f"メールID「{mailid}」は存在しません")
        
        # 受信メールの場合、既読フラグを更新
        if email_data.get('recipient_id') == user_id and not email_data.get('is_read'):
            safe_database_query(
                "UPDATE emails SET is_read = TRUE WHERE id = %s", 
                (email_id,)
            )
        
        # テンプレート互換性のため配列形式に変換
        email_array = [
            email_data.get('id', 0),                    # [0] - メールID
            email_data.get('sender_id', 0),             # [1] - 送信者ID
            email_data.get('recipient_id', 0),          # [2] - 受信者ID
            email_data.get('subject', ''),              # [3] - 件名
            email_data.get('body', ''),                 # [4] - 本文
            email_data.get('is_read', False),           # [5] - 既読フラグ
            email_data.get('created_at', ''),           # [6] - 作成日時
            email_data.get('attachment_path', ''),      # [7] - 添付ファイルパス
            email_data.get('sender_name', ''),          # [8] - 送信者名
            email_data.get('recipient_name', ''),       # [9] - 受信者名
        ]
        
        return render_template('mail/read.html', email=email_array, render_subject_ssti=render_subject_ssti)
        
    except Exception as e:
        # データベースエラーの場合も受信メールボックスにエラーテロップ付きで表示
        emails_raw = safe_database_query("""
            SELECT e.id, e.sender_id, e.recipient_id, e.subject, e.body, 
                   e.attachment_path, e.is_read, e.created_at, u.username as sender_name
            FROM emails e 
            JOIN users u ON e.sender_id = u.id 
            WHERE e.recipient_id = %s 
            ORDER BY e.created_at DESC
        """, (user_id,), fetch_all=True, default_value=[])
        
        emails_data = []
        for email in emails_raw or []:
            if isinstance(email, dict):
                email_array = [
                    email.get('id', 0), email.get('sender_id', 0), email.get('recipient_id', 0),
                    email.get('subject', ''), email.get('body', ''), email.get('is_read', False),
                    email.get('created_at', ''), email.get('sender_name', ''),
                    1 if email.get('attachment_path') else 0, email.get('attachment_path', ''),
                ]
                emails_data.append(email_array)
        
        return render_template('mail/inbox.html', 
                             emails=emails_data, 
                             error_alert=True,
                             error_mailid=sanitize_mailid(mailid),  # サニタイズ適用
                             error_message=f"エラーが発生しました: {str(e)}")

@bp.route('/mail/download')
def download_attachment():
    """添付ファイルダウンロード (Directory Traversal脆弱性)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    mailid = request.args.get('mailid', '')
    
    # mailid の検証
    try:
        email_id = int(mailid)
    except (ValueError, TypeError):
        flash('無効なメールIDです', 'error')
        return redirect('/mail/inbox')
    
    try:
        # メール情報を取得
        email_data = safe_database_query("""
            SELECT attachment_path FROM emails 
            WHERE id = %s AND (sender_id = %s OR recipient_id = %s)
        """, (email_id, user_id, user_id), fetch_one=True)
        
        if not email_data or not email_data.get('attachment_path'):
            flash('添付ファイルが見つかりません', 'error')
            return redirect('/mail/inbox')
        
        attachment_path = email_data.get('attachment_path')
        
        # 脆弱性: Directory Traversal対策なし
        file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(attachment_path))
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('ファイルが見つかりません', 'error')
            return redirect('/mail/inbox')
            
    except Exception as e:
        flash(f'ファイルダウンロード中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/mail/inbox')