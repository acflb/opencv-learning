import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from cnocr import CnOcr
import ctypes
import psutil
import win32gui
import win32process
import time
import keyboard
import os
import sys

# 解决 Windows 高分屏缩放导致的坐标偏移问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

print("正在加载 OCR 模型...")
ocr = CnOcr() 
print("模型加载完成，开始识别！")

# 设置匹配阈值
threshold = 0.8


""" 加载模板图 """
def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和 PyInstaller 打包后的环境"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# 读取模板图
BASEURL = resource_path("./images/")
template_paths = [BASEURL + "more.png", BASEURL + "download_icon.png", BASEURL + "start_downloading.png", BASEURL + "start_downloading_affirm.png"]

""" 根据可执行文件名获取窗口句柄 """
def get_windows_by_exe(exe_name):
    result = []
    
    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        if not win32gui.GetWindowText(hwnd):  # 跳过没有标题的窗口（通常是不可见的辅助窗口）
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            if proc.name().lower() == exe_name.lower():
                result.append(hwnd)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(callback, None)
    return result
    
    
""" 模板匹配 """
def match_template(screen_bgr, template_path, win_x, win_y):
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ 模板图片未找到: {template_path}")
        return None, None, None

    h, w = template.shape[:2]
    res = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        # 计算图标中心位置
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # 将局部坐标转换为全屏坐标
        abs_x = center_x + win_x
        abs_y = center_y + win_y
        
        # 执行点击
        pyautogui.click(abs_x, abs_y)
        print(f"✅ 成功点击图标，屏幕坐标: ({abs_x}, {abs_y})，匹配度: {max_val:.2f}")
        # return max_loc, (w, h), max_val
    else:
        print(f"❌ 未找到匹配的图标，最大值: {max_val:.2f}")
        return None, None, None
    
    
""" 截图 """
def capture_window(hwnd):
    if not win32gui.IsWindow(hwnd):
        print(f"❌ 无效的窗口句柄: {hwnd}")
        return None

    # 如果窗口最小化，先恢复窗口,并等待窗口恢复
    if hwnd and win32gui.IsIconic(hwnd):  # 如果窗口最小化
        win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.5)  # 等待窗口恢复

    # 获取窗口位置和大小
    win_x, win_y, win_w, win_h = win32gui.GetWindowRect(hwnd)
    bbox = (win_x, win_y, win_w, win_h)
    
    # 截取窗口区域
    screen = ImageGrab.grab(bbox=bbox)
    # 保存截图供调试
    # screen.save("debug_window_crop.png")
    
    # 将 PIL 图像转换为 OpenCV 格式 (BGR)
    frame_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    return frame_bgr
    

""" 主函数 """
def main(window_exe_name):

    # 1. 获取窗口句柄  
    hwnds = get_windows_by_exe(window_exe_name)
    
    # 2.循环点击每个模板图
    for template_path in template_paths:
        if not hwnds:
            print(f"❌ 未找到可执行文件 '{window_exe_name}' 的窗口")
            return
        
        # 截图窗口，返回 OpenCV 图像
        frame_bgr = capture_window(hwnds[0])
        # 获取窗口位置和大小
        win_x, win_y, win_w, win_h = win32gui.GetWindowRect(hwnds[0])

        # 执行模板匹配并点击
        match_template(frame_bgr, template_path, win_x, win_y)
        time.sleep(0.5)  # 等待点击动作完成
    
if __name__ == "__main__":
    
    keyboard.add_hotkey("ctrl+alt+1", lambda: main("CamScanner.exe"))
    keyboard.wait()
    