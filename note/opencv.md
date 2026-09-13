## 环境准备
安装python management(一路选yes)

开启Windows本地脚本执行许可
win+x打开管理员权限powershell,输入'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser'

以下都为当前目录

创建虚拟环境
python -m venv <环境名称>

删除虚拟环境
rm -rf <环境名称>

激活虚拟环境
<powershell>
.\venv\Scripts\activate.ps1
<cmd>
.\venv\Scripts\activate.bat
<mac>
source venv/bin/activate

退出虚拟环境
deactivate

查看当前环境已安装的包
pip list

导出当前环境所有依赖
pip freeze > requirements.txt

一键安装依赖
pip install -r requirements.txt

查看当前python解释器
<Windows>
where python
<Mac>
which python

安装包
pip install opencv-python cnocr pillow numpy requests onnxruntime pygetwindow
