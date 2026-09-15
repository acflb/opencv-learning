import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import pygetwindow as gw
import ctypes
import os
import time
from pywinauto.application import Application
import pyperclip

folder_dialog = None  # 全局变量，用于存储【选择文件夹】对话框的窗口对象

BASE_SAVE_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
app = Application(backend="win32").connect(title_re="选择文件夹", class_name="#32770", timeout=1)
folder_dialog = app.window(title_re="选择文件夹", class_name="#32770")
folder_dialog.set_focus()
# pyautogui.hotkey('alt', 'd')
# time.sleep(0.2)
# pyperclip.copy(BASE_SAVE_PATH)
# pyautogui.hotkey('ctrl', 'v')
# pyautogui.press('enter')
# time.sleep(0.5)

# # 2. 快捷键 Ctrl+Shift+N 新建文件夹
# pyautogui.hotkey('ctrl', 'shift', 'n')
# time.sleep(0.5)

# # 3. 输入联系人名字作为新文件夹名并确认
# pyautogui.write("1")
# time.sleep(0.2)
# pyautogui.press('enter')  #  新建文件夹
# time.sleep(0.4)


# import time
# from pywinauto import Desktop

# dlg = Desktop(backend="win32").window(title="选择文件夹")
# dlg.wait('ready', timeout=10)

# # 找到路径输入框（如果有多个Edit，用print_control_identifiers里的
# # auto_id / control_id 精确定位，比如加 found_index=0）
# edit = dlg.child_window(class_name="Edit")
# edit.set_edit_text(r"C:\Users\你的用户名\Desktop\目标文件夹路径")
# time.sleep(0.3)

# 点"选择文件夹"确认按钮（注意这里必须限定 class_name="Button"，
# 不然pywinauto可能会误抓到对话框标题本身，因为标题文字也叫"选择文件夹"喵）
folder_dialog.child_window(title="选择文件夹", class_name="Button").click_input()
# 4. 快捷键 Alt+S 触发右下角的“选择文件夹”按钮
# save_btn = folder_dialog.child_window(title_re="选择文件夹", control_type="Button")
# save_btn = folder_dialog.child_window(id=1)
# save_btn.click()
print(f"🎉 文件保存成功！保存路径为: 【桌面 / 1】",{folder_dialog.child_window})