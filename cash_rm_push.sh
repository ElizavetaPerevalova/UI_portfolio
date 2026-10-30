#!/bin/bash

echo "========================================"
echo "📝 Enter your commit message:"
echo "========================================"
read commit_message

if [ -z "$commit_message" ]
then
      echo "❌ Error: Commit message cannot be empty!"
      exit 1
fi

echo "🧹 Clearing Git cache..."
git rm -r --cached .

echo "➕ Adding files to Git index..."
git add .

echo "💾 Committing changes..."
git commit -m "$commit_message"

echo "🚀 Pushing to GitHub (origin master)..."
git push

echo "========================================"
echo "🎉 Done! Everything is up to date on GitHub!"
echo "========================================"
