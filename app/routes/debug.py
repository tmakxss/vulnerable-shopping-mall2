from flask import Blueprint, jsonify
from app.utils import safe_database_query
import traceback

bp = Blueprint('debug', __name__)

@bp.route('/debug')
def debug():
    """デバッグ情報を表示"""
    debug_info = {
        "status": "running",
        "tests": []
    }
    
    try:
        # テスト 1: 基本的なクエリ
        result1 = safe_database_query("SELECT COUNT(*) as count FROM users", fetch_one=True)
        debug_info["tests"].append({
            "test": "user_count",
            "result": result1,
            "success": True
        })
        
        # テスト 2: 商品データの詳細
        result2 = safe_database_query("SELECT * FROM products LIMIT 1", fetch_one=True)
        debug_info["tests"].append({
            "test": "product_detail",
            "result": result2,
            "result_type": str(type(result2)),
            "success": True
        })
        
        # テスト 3: 商品リスト
        result3 = safe_database_query("SELECT id, name, price FROM products LIMIT 2", fetch_all=True)
        debug_info["tests"].append({
            "test": "product_list",
            "result": result3,
            "result_type": str(type(result3)),
            "count": len(result3) if result3 else 0,
            "success": True
        })
        
    except Exception as e:
        debug_info["tests"].append({
            "test": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        })
    
    return jsonify(debug_info)

@bp.route('/debug/products')
def debug_products():
    """商品データの詳細デバッグ"""
    try:
        # 直接データベース操作でテスト
        from app.database import DatabaseManager
        
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 最初の商品を取得
        cursor.execute("SELECT * FROM products LIMIT 1")
        raw_result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        
        # 手動で辞書変換
        manual_dict = {}
        if raw_result:
            for i, col in enumerate(columns):
                try:
                    value = raw_result[i]
                    if hasattr(value, '__class__'):
                        manual_dict[col] = {
                            "value": str(value),
                            "type": str(type(value)),
                            "raw": repr(value)
                        }
                    else:
                        manual_dict[col] = value
                except Exception as e:
                    manual_dict[col] = f"Error: {e}"
        
        conn.close()
        
        return jsonify({
            "raw_result": str(raw_result),
            "raw_type": str(type(raw_result)),
            "columns": columns,
            "manual_dict": manual_dict,
            "db_manager_result": db.execute_query("SELECT * FROM products LIMIT 1", fetch_one=True)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        })