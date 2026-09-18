## 环境准备
安装python management(一路选yes)

开启Windows本地脚本执行许可
win+x打开管理员权限powershell,输入'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser'

以下都为当前目录

创建虚拟环境
python -m venv <环境名称>
python3.14 -m venv <环境名称>

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
<!-- 识别所需 -->
pip install opencv-python cnocr pillow numpy requests onnxruntime
<!-- 点击所需 -->
pip install pyautogui pygetwindow pywin32
<!-- 控制win原生窗口所需 -->
pip install pywinauto Pillow
<!-- 快捷键所需 -->
keyboard

#### 打包
'--noconsole'关闭控制台输出
pyinstaller --onefile --collect-all torch --collect-all torchvision --collect-all cnocr --collect-all cnstd --add-data "venv\Lib\site-packages\rapidocr;rapidocr" --add-data "images;images" opencv1.py
