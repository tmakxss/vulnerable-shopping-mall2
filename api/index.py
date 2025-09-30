import sys
import os

# パスを追加してアプリケーションをインポート可能にする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    
    # Flaskアプリケーションを作成
    app = create_app()
    
except Exception as e:
    # フォールバック: 最小限のアプリケーション
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'fallback_key')
    
    @app.route('/')
    def fallback_home():
        return jsonify({
            'message': '🔒 脆弱なショッピングモール - 初期化中',
            'status': 'initializing',
            'error': f'アプリケーション読み込みエラー: {str(e)}',
            'note': 'データベース初期化後に完全機能が利用可能になります'
        })
    
    @app.route('/health')
    def fallback_health():
        return jsonify({'status': 'partial', 'error': str(e)})

# Vercel用エクスポート
application = app

if __name__ == "__main__":
    # ローカル開発用
    app.run(debug=True)