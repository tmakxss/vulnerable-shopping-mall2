import os
import psycopg2
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

def fix_gtr_names():
    """GT-Rの名前を修正"""
    
    # .envからSupabaseの接続情報を取得
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
    
    if not SUPABASE_DB_URL:
        print("❌ SUPABASE_DB_URLが見つかりません")
        return
    
    try:
        # PostgreSQL接続
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cursor = conn.cursor()
        
        print("🔗 Supabaseに接続しました")
        
        # 修正データ
        name_fixes = [
            {
                'id': 8,
                'old_name': 'Nissan GT-R R33',
                'new_name': 'Nissan GT-R R35',
                'new_description': 'スカイラインGT-Rの最新進化形。VR38DETTエンジンと先進的な4WDシステムATTESA E-TSを搭載。「技術の日産」の現代的な到達点。'
            },
            {
                'id': 16,
                'old_name': 'Nissan Fairlady Z',
                'new_name': 'Nissan Skyline GT-R R33',
                'new_description': 'スカイラインGT-Rの第3世代。RB26DETTエンジンと4WDシステムATTESAを搭載。「技術の日産」を象徴する伝説的スポーツカー。'
            }
        ]
        
        print("🚗 GT-Rの名前を修正中...")
        
        # 各商品名を修正
        for fix in name_fixes:
            cursor.execute('''
                UPDATE products 
                SET name = %s, description = %s
                WHERE id = %s
            ''', (fix['new_name'], fix['new_description'], fix['id']))
            
            print(f"✅ ID {fix['id']}: {fix['old_name']} → {fix['new_name']}")
        
        # 変更をコミット
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 GT-Rの名前修正が完了しました！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_gtr_names()