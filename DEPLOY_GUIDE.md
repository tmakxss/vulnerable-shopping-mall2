# 🚀 Phase 2 デプロイガイド

## 📋 デプロイ準備完了チェックリスト

✅ **コード修正完了**
- Vercel + Supabase対応
- 環境変数の外部化
- セキュリティ警告バナー追加
- GitHubリポジトリ初期化

## 🔧 必要な次のステップ

### 1. GitHubリポジトリ作成
```bash
# GitHub上で新しいリポジトリを作成後
git remote add origin https://github.com/[YOUR_USERNAME]/vulnerable-shopping-mall.git
git branch -M main
git push -u origin main
```

### 2. Supabaseプロジェクト設定

#### 2.1 新プロジェクト作成
1. [Supabase](https://supabase.com) にログイン
2. "New project" をクリック
3. プロジェクト名: `vulnerable-shopping-mall`
4. データベースパスワードを設定
5. リージョン選択（推奨: Asia Pacific (Tokyo)）

#### 2.2 データベース接続情報取得
1. Settings > Database
2. 以下の情報をコピー:
   - `Host`
   - `Database name`
   - `Port`
   - `User`
   - `Password`

#### 2.3 データベース初期化
```bash
# 環境変数を設定後
python database/init_supabase.py
```

### 3. Vercelデプロイ設定

#### 3.1 Vercelプロジェクト作成
1. [Vercel](https://vercel.com) にログイン
2. "New Project" をクリック
3. GitHubリポジトリを選択

#### 3.2 環境変数設定
Vercelの設定画面で以下の環境変数を設定:

```env
# データベース設定
DB_TYPE=postgresql
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@[PROJECT_REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_KEY=[ANON_KEY]

# セキュリティ設定
SECRET_KEY=[ランダムな文字列]
```

#### 3.3 ビルド設定
- **Framework Preset**: Other
- **Root Directory**: `./`
- **Build Command**: (空のまま)
- **Output Directory**: (空のまま)

## 🔐 環境変数詳細

### SUPABASE_DB_URL
形式: `postgresql://postgres:[PASSWORD]@[PROJECT_REF].supabase.co:5432/postgres`
- `[PASSWORD]`: データベース作成時に設定したパスワード
- `[PROJECT_REF]`: プロジェクトの参照ID

### SUPABASE_URL & SUPABASE_KEY
1. Supabase Dashboard > Settings > API
2. `Project URL` → `SUPABASE_URL`
3. `anon public` キー → `SUPABASE_KEY`

### SECRET_KEY
セッション暗号化用のランダムな文字列:
```python
import secrets
print(secrets.token_hex(32))
```

## 🎯 デプロイ後の確認項目

1. **サイトアクセス**: Vercel URLでサイトが表示される
2. **セキュリティ警告**: 赤い警告バナーが表示される
3. **ログイン機能**: テストアカウントでログイン可能
4. **データベース**: 商品一覧が表示される

## 🚨 セキュリティ注意事項

- **教育目的のみ**: サイト上に明確な警告を表示済み
- **アクセス制限**: 必要に応じてBasic認証等を追加
- **個人情報**: 実際の個人情報は使用しない
- **クレジットカード**: 決済機能は無効化されている

## 📞 トラブルシューティング

### よくある問題
1. **データベース接続エラー**: 環境変数の確認
2. **デプロイエラー**: requirements.txtの依存関係確認
3. **静的ファイル404**: Vercelの静的ファイル設定確認

### ログ確認
- Vercel: Functions タブでログ確認
- Supabase: Database > Logs でクエリログ確認

## 🎉 次のフェーズ

Phase 2完了後、Phase 3でXSS脆弱性の段階的追加を開始します。