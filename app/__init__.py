from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# 環境変数をロード
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 環境変数から秘密鍵を取得（本番環境では適切な値を設定）
    app.secret_key = os.getenv('SECRET_KEY', 'vulnerable_shop_secret_key_12345')
    
    # セキュリティ警告の設定
    app.config['SECURITY_WARNING'] = True
    app.config['EDUCATIONAL_USE_ONLY'] = True
    
    # 基本的なヘルスチェックルート（ブループリント読み込み前）
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'Vulnerable Shopping Mall is running',
            'environment': {
                'db_type': os.getenv('DB_TYPE', 'not_set'),
                'supabase_configured': bool(os.getenv('SUPABASE_URL')),
                'secret_key_configured': bool(os.getenv('SECRET_KEY'))
            }
        })
    
    @app.route('/status')
    def status():
        return jsonify({'status': 'ok', 'service': 'vulnerable-shopping-mall'})
    
    # ブループリント登録（エラーハンドリング付き）
    try:
        from app.routes import main, auth, product, cart, order, review, admin, user, api, mail, health
        
        app.register_blueprint(health.bp)  # 詳細ヘルスチェック
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(product.bp)
        app.register_blueprint(cart.bp)
        app.register_blueprint(order.bp)
        app.register_blueprint(review.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(user.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(mail.bp)
        
    except ImportError as e:
        print(f"Warning: Could not import some blueprints: {e}")
        # 基本的な機能のみ提供
        @app.route('/')
        def index():
            return jsonify({
                'message': '🔒 脆弱なショッピングモール - セットアップ中',
                'status': 'initializing',
                'error': str(e)
            })
    
    return app 