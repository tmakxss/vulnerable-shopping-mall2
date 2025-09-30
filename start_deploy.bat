@echo off
echo ========================================
echo 🚀 脆弱ショッピングモールサイト デプロイ
echo ========================================
echo.

echo 📋 Phase 2: インフラ構築とデプロイ
echo.

echo ✅ 完了項目:
echo   - コード修正 (Vercel + Supabase対応)
echo   - セキュリティ警告バナー追加
echo   - GitHubリポジトリ初期化
echo   - データベース移行スクリプト作成
echo.

echo 🔧 必要な手動作業:
echo.
echo 1. GitHubリポジトリ作成:
echo    - https://github.com にアクセス
echo    - New repository をクリック
echo    - Name: vulnerable-shopping-mall
echo    - Public を選択
echo    - Create repository をクリック
echo.
echo 2. Supabaseプロジェクト作成:
echo    - https://supabase.com にアクセス
echo    - New project をクリック
echo    - Name: vulnerable-shopping-mall
echo    - Database password を設定
echo    - Region: Asia Pacific (Tokyo)
echo.
echo 3. Vercelプロジェクト作成:
echo    - https://vercel.com にアクセス
echo    - New Project をクリック
echo    - GitHubリポジトリを選択
echo    - 環境変数を設定
echo.

echo 📖 詳細ガイド:
echo   - DEPLOY_GUIDE.md     : 総合デプロイガイド
echo   - VERCEL_DEPLOY.md    : Vercel設定詳細
echo   - deploy_github.bat   : GitHubプッシュスクリプト
echo.

echo 🚨 重要: 
echo   このサイトは学習目的のみで使用してください
echo   実際の攻撃は違法です
echo.

pause