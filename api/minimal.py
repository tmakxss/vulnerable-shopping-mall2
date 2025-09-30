"""
最小限のFlaskアプリケーション（Vercelテスト用）
"""
from flask import Flask, jsonify
import os

def create_minimal_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'test_key')
    
    @app.route('/')
    def home():
        return jsonify({
            'message': '🔒 脆弱なショッピングモール',
            'status': 'running',
            'warning': 'このサイトは教育目的でのみ使用してください',
            'environment': {
                'DB_TYPE': os.getenv('DB_TYPE', 'not_set'),
                'SUPABASE_URL': 'configured' if os.getenv('SUPABASE_URL') else 'not_set'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'service': 'vulnerable-shopping-mall'
        })
    
    return app

# アプリケーション作成
app = create_minimal_app()

# Vercel用エクスポート
application = app