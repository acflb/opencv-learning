import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from cnocr import CnOcr
import pygetwindow as gw
import time

# 1. 初始化 CnOCR
ocr = CnOcr()

def find_and_click_text(target_text="保存", window_title="微信"):
    """
    在指定窗口中识别包含 target_text 的文字块，并自动点击该文字
    """
    # 1. 查找微信窗口
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"未找到标题包含 '{window_title}' 的窗口！")
        return False
    
    win = windows[0]
    if win.isMinimized:
        win.restore()
        
    win_x, win_y, win_w, win_h = win.left, win.top, win.width, win.height
    print(f"找到窗口 '{win.title}' -> 屏幕位置: X={win_x}, Y={win_y}, 宽={win_w}, 高={win_h}")

    # 2. 截取整个微信窗口画面
    bbox = (win_x, win_y, win_x + win_w, win_y + win_h)
    screen = ImageGrab.grab(bbox=bbox)
    frame_rgb = np.array(screen)
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    
    # 调亮/高对比度处理（可选，辅助底色识别）
    # 底部栏背景较暗，CnOCR 对深底白字识别率通常很不错
    
    # 3. 使用 CnOCR 进行识别
    results = ocr.ocr(frame_bgr)
    
    target_found = False
    for item in results:
        text = item['text']
        position = item['position']  # 返回 4 个顶点的相对坐标 np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])
        
        # 判断识别到的文本中是否包含目标词（如“保存”）
        if target_text in text:
            target_found = True
            
            # 计算文字框在局部截图中的中心坐标 (rel_center_x, rel_center_y)
            xs = [pt[0] for pt in position]
            ys = [pt[1] for pt in position]
            rel_center_x = int(sum(xs) / len(xs))
            rel_center_y = int(sum(ys) / len(ys))
            
            # 换算为屏幕上的【绝对坐标】
            abs_x = win_x + rel_center_x
            abs_y = win_y + rel_center_y
            
            print(f"✅ 找到文本 '{text}'！在窗口内部坐标: ({rel_center_x}, {rel_center_y})")
            print(f"准备点击屏幕绝对坐标: ({abs_x}, {abs_y})")
            
            # 4. 执行自动移动与点击
            pyautogui.moveTo(abs_x, abs_y, duration=0.2)  # 带平滑移动，防止被防作弊机制屏蔽
            pyautogui.click()
            print("点击完成！")
            return True
            
    if not target_found:
        print(f"❌ 未在当前画面中识别到 '{target_text}' 文字，请确认底部栏是否已弹出。")
        # 调试保存当前截图
        cv2.imwrite("debug_wechat.png", frame_bgr)
        print("当前截图已保存至 debug_wechat.png 以供检查。")
        return False

# ==================== 测试运行 ====================
if __name__ == "__main__":
    # print("请在 3 秒内将微信界面打开并调出带有‘保存’图标的操作栏...")
    # time.sleep(3)
    
    # 识别并点击微信窗口中的“保存”按钮
    find_and_click_text(target_text="保存", window_title="微信")