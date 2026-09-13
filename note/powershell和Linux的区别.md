1. 在powershell中不能直接使用Linux的命令
例:删除 .venv 文件夹命令
<Linux>
rm -rf .venv
<powershell>
Remove-Item -Recurse -Force .\.venv
rm -Recurse -Force .\.venv