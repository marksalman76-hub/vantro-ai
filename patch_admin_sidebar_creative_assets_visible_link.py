cd /d "C:\Users\User\Desktop\ecommerce-ai-agent-platform"

python -X utf8 patch_admin_sidebar_creative_assets_visible_link.py

findstr /n /i "admin/creative-assets Creative Media Assets" frontend\src\app\admin\page.tsx

cd frontend

npm run build

cd /d "C:\Users\User\Desktop\ecommerce-ai-agent-platform"

git add frontend/src/app/admin/page.tsx patch_admin_sidebar_creative_assets_visible_link.py

git commit -m "Add visible creative assets sidebar link"

git push origin main

deploy-all.cmd