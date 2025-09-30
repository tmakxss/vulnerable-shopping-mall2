from flask import Blueprint, render_template, request, session, redirect, flash
from app.utils import safe_database_query

bp = Blueprint('review', __name__)

@bp.route('/reviews')
def all_reviews():
    """全レビュー一覧"""
    try:
        # XSS脆弱性のあるレビュー表示
        reviews_data = safe_database_query("""
            SELECT r.id, r.rating, r.comment, r.created_at, 
                   u.username, p.name as product_name, p.image_url 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            JOIN products p ON r.product_id = p.id 
            ORDER BY r.created_at DESC
        """, fetch_all=True, default_value=[])
        
        # レビューを配列形式に変換
        reviews = []
        for review in reviews_data:
            if isinstance(review, dict):
                review_array = [
                    review.get('id', 0),
                    0,  # product_id (後で設定)
                    0,  # user_id (後で設定)
                    review.get('rating', 0),
                    review.get('comment', ''),
                    review.get('created_at', ''),
                    review.get('username', ''),
                    review.get('product_name', ''),
                    review.get('image_url') or '/static/test.jpeg'
                ]
                reviews.append(review_array)
        
        return render_template('review/list.html', reviews=reviews)
        
    except Exception as e:
        flash(f'レビューの取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('review/list.html', reviews=[])

@bp.route('/review/<int:review_id>')
def review_detail(review_id):
    """レビュー詳細"""
    try:
        # レビュー詳細取得
        review_data = safe_database_query("""
            SELECT r.id, r.rating, r.comment, r.created_at, 
                   u.username, p.name as product_name, p.image_url 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            JOIN products p ON r.product_id = p.id 
            WHERE r.id = ?
        """, (review_id,), fetch_one=True)
        
        if not review_data:
            flash('レビューが見つかりません', 'error')
            return redirect('/reviews')
        
        # レビューを配列形式に変換
        review = [
            review_data.get('id', 0),
            0,  # product_id
            0,  # user_id
            review_data.get('rating', 0),
            review_data.get('comment', ''),
            review_data.get('created_at', ''),
            review_data.get('username', ''),
            review_data.get('product_name', ''),
            review_data.get('image_url') or '/static/test.jpeg'
        ]
        
        return render_template('review/detail.html', review=review)
        
    except Exception as e:
        flash(f'レビューの取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect('/reviews') 