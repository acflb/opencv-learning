## 创建一个新的存储库并推送
echo "# opencv-learning" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M master
git remote add origin https://github.com/acflb/opencv-learning.git
git push -u origin master

## 推送已存在的仓库到远端
git remote add origin https://github.com/acflb/opencv-learning.git
git branch -M master
git push -u origin master