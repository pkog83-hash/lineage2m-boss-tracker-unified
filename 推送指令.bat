@echo off
echo 正在推送代碼到GitHub...

cd /d "C:\Users\Admin\統一版本"

echo 請將下面的網址替換為您的GitHub倉庫網址：
echo https://github.com/您的用戶名/lineage2m-boss-tracker-unified.git

echo.
echo 請手動執行以下命令（替換您的用戶名）：
echo git remote add origin https://github.com/您的用戶名/lineage2m-boss-tracker-unified.git
echo git branch -M main  
echo git push -u origin main

pause