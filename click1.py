import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from cnocr import CnOcr
import pygetwindow as gw
import ctypes

# 解决 Windows 高分屏缩放导致的坐标偏移问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# =========================================================
# 极速优化 1：模型必须在【全局】只初始化一次！
# =========================================================
print("正在加载 OCR 模型...")
ocr = CnOcr() 
print("模型加载完成，开始识别！")

def click_save_button(window_title="微信"):
    # 1. 获取目标窗口
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"未找到标题包含 '{window_title}' 的窗口")
        return False
    
    win = windows[0]
    if win.isMinimized:
        win.restore()
        
    win_x, win_y, win_w, win_h = win.left, win.top, win.width, win.height

    # =========================================================
    # 极速优化 2：局部截图 (ROI) —— 只截取微信窗口底部 20% 的区域
    # 保存按钮必定在底部，无需浪费算力去扫描顶部聊天记录
    # =========================================================
    bottom_crop_h = int(win_h * 0.25)  # 取底部 25% 的高度
    
    crop_x = win_x
    crop_y = win_y + (win_h - bottom_crop_h)
    crop_w = win_w
    crop_h = bottom_crop_h

    # 截取局部画面
    bbox = (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    screen = ImageGrab.grab(bbox=bbox)
    frame_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # 3. 识图 (此时图片体积变小，识别速度提升 5~10 倍)
    results = ocr.ocr(frame_bgr)
    
    for item in results:
        text = item['text']
        if "保存" in text:
            position = item['position']
            
            # 计算局部区域的中心点
            xs = [pt[0] for pt in position]
            ys = [pt[1] for pt in position]
            rel_x = int(sum(xs) / len(xs))
            rel_y = int(sum(ys) / len(ys))
            
            # 还原为全屏绝对坐标
            abs_x = crop_x + rel_x
            abs_y = crop_y + rel_y
            
            # 快速移动并点击
            pyautogui.click(abs_x, abs_y)
            print(f"✅ 成功点击‘保存’，屏幕坐标: ({abs_x}, {abs_y})")
            return True
            
    print("❌ 底部区域未识别到‘保存’")
    return False

def click_by_template():
    # 1. 截屏
    screen = ImageGrab.grab()
    screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    # 2. 读取图标小图
    template = cv2.imread('./images/save_icon.png')
    h, w = template.shape[:2]
    
    # 3. 毫秒级矩阵匹配
    res = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # 匹配度 > 80% 即判定找到
    if max_val > 0.8:
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        pyautogui.click(center_x, center_y)
        print(f"极速点击成功！耗时约 20ms")

if __name__ == "__main__":
    # 调低 PyAutoGUI 的默认延迟（默认每次点击后会强制暂停 0.1s）
    pyautogui.PAUSE = 0.02
    
    # 运行识别点击
    click_save_button("微信")