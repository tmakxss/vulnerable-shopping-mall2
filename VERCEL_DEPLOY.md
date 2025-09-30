# 🚀 Vercelデプロイ設定ガイド

## 1. Vercelプロジェクト作成

1. **Vercel（https://vercel.com）にログイン**
2. **"New Project" をクリック**
3. **"Import Git Repository" セクションで GitHubリポジトリを選択**
   - `YOUR_USERNAME/vulnerable-shopping-mall` を選択
4. **"Import" をクリック**

## 2. プロジェクト設定

### Framework Preset
- **Framework Preset**: `Other` を選択

### Root Directory
- **Root Directory**: `./` （デフォルトのまま）

### Build and Output Settings
- **Build Command**: 空のまま
- **Output Directory**: 空のまま
- **Install Command**: `pip install -r requirements.txt`

## 3. 環境変数設定

**Environment Variables** セクションで以下を設定：

### 必須環境変数

```env
# データベース設定
DB_TYPE=postgresql
SUPABASE_DB_URL=postgresql://postgres:[DB_PASSWORD]@[PROJECT_REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_KEY=[ANON_KEY]

# セキュリティ設定
SECRET_KEY=[RANDOM_SECRET_KEY]
```

### 値の取得方法

#### Supabase関連
1. **Supabaseダッシュボード** → **Settings** → **Database**
2. **Connection string** から以下を取得：
   - `[PROJECT_REF]`: プロジェクト参照ID
   - `[DB_PASSWORD]`: 設定したデータベースパスワード

3. **Settings** → **API**から以下を取得：
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_KEY`: anon public key

#### SECRET_KEY生成
PowerShellで以下を実行：
```powershell
[System.Web.Security.Membership]::GeneratePassword(32, 0)
```

## 4. デプロイ実行

1. **"Deploy" をクリック**
2. **ビルドプロセスの監視**
3. **デプロイ完了後、URLをクリックしてサイトにアクセス**

## 5. デプロイ後の確認

### ✅ 確認項目
- [ ] サイトが正常に表示される
- [ ] 赤い警告バナーが表示される
- [ ] データベースエラーが発生する（初期化前のため正常）

### 🗄️ データベース初期化
デプロイ成功後、ローカルで以下を実行：

```bash
# .env.productionファイルに本番環境変数を設定後
python database/init_supabase.py
```

## 6. トラブルシューティング

### よくあるエラー
1. **Module not found**: requirements.txtの依存関係確認
2. **Database connection failed**: 環境変数の値確認
3. **500 Internal Server Error**: Vercel Function Logsで詳細確認

### ログ確認方法
1. **Vercel Dashboard** → **Functions**
2. **Real-time logs** でエラー詳細を確認

## 🎉 成功確認

デプロイが成功すると：
- Vercel URLでサイトにアクセス可能
- 「脆弱なショッピングモール」のタイトル表示
- セキュリティ警告バナー表示
- データベース初期化後、完全動作開始