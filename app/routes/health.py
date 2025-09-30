from flask import Blueprint, render_template_string
from app.utils import get_database_status
import os

bp = Blueprint('health', __name__)

@bp.route('/health')
def health_check():
    """ヘルスチェックエンドポイント"""
    db_status, db_message = get_database_status()
    
    # 環境変数の確認
    env_vars = {
        'DB_TYPE': os.getenv('DB_TYPE', 'Not set'),
        'SUPABASE_URL': 'Set' if os.getenv('SUPABASE_URL') else 'Not set',
        'SUPABASE_KEY': 'Set' if os.getenv('SUPABASE_KEY') else 'Not set',
        'SECRET_KEY': 'Set' if os.getenv('SECRET_KEY') else 'Not set'
    }
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Health Check - 脆弱なショッピングモール</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        </style>
    </head>
    <body>
        <h1>🔒 脆弱なショッピングモール - ヘルスチェック</h1>
        
        <div class="status warning">
            <strong>⚠️ セキュリティ警告</strong><br>
            このサイトは教育目的でのみ使用してください。実際の攻撃は違法です。
        </div>
        
        <h2>📊 システム状態</h2>
        
        <h3>🗄️ データベース接続</h3>
        <div class="status {{ 'success' if db_status else 'error' }}">
            <strong>状態:</strong> {{ 'OK' if db_status else 'Error' }}<br>
            <strong>詳細:</strong> {{ db_message }}
        </div>
        
        <h3>🔧 環境変数</h3>
        {% for key, value in env_vars.items() %}
        <div class="status {{ 'success' if value != 'Not set' else 'error' }}">
            <strong>{{ key }}:</strong> {{ value }}
        </div>
        {% endfor %}
        
        <h3>🚀 次のステップ</h3>
        {% if not db_status %}
        <div class="status error">
            <strong>データベース初期化が必要です:</strong><br>
            1. ローカルで <code>python database/init_supabase.py</code> を実行<br>
            2. 環境変数が正しく設定されているか確認
        </div>
        {% else %}
        <div class="status success">
            <strong>準備完了!</strong><br>
            <a href="/">メインサイトにアクセス</a>
        </div>
        {% endif %}
        
        <hr>
        <p><small>🌐 Vercel デプロイ | 📅 {{ timestamp }}</small></p>
    </body>
    </html>
    '''
    
    import datetime
    return render_template_string(html, 
                                db_status=db_status, 
                                db_message=db_message,
                                env_vars=env_vars,
                                timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@bp.route('/status')
def simple_status():
    """シンプルなステータス確認"""
    return {
        'status': 'ok',
        'message': 'Vulnerable Shopping Mall is running',
        'database': get_database_status()[0]
    }