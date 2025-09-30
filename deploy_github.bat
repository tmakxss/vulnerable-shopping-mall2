# GitHubデプロイスクリプト
# 実際のGitHubユーザー名を YOUR_USERNAME に置き換えて実行してください

echo "GitHubリポジトリの設定とプッシュ"

# リモートリポジトリ設定
git remote remove origin 2>/dev/null
git remote add origin https://github.com/YOUR_USERNAME/vulnerable-shopping-mall.git

# メインブランチに変更
git branch -M main

# プッシュ
git push -u origin main

echo "GitHubプッシュ完了！"
echo "次にVercelでデプロイを設定してください。"