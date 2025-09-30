from flask import Flask
from app.routes import main, auth, product, cart, order, review, admin, user, api, mail, health
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
    
    # ブループリント登録
    app.register_blueprint(health.bp)  # ヘルスチェックを最初に登録
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
    
    return app 