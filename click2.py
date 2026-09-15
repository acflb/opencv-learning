import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import pygetwindow as gw
import ctypes

# 解决 Windows 高分屏缩放导致的坐标偏移问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# 设置 PyAutoGUI 动作间极短暂停
pyautogui.PAUSE = 0.01

def click_save_button(window_title="微信", template_path=["./images/save_icon_dark.png", "./images/save_icon_light.png"], threshold=0.8):
    """
    通过模板匹配毫秒级查找并点击微信中的“保存”按钮
    
    :param window_title: 目标窗口标题
    :param template_path: 保存图标的切图路径
    :param threshold: 匹配相似度阈值（0.8 表示 80% 以上相似即认定匹配）
    """
    # 1. 获取微信窗口
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"❌ 未找到标题包含 '{window_title}' 的窗口")
        return False
    
    win = windows[0]
    if win.isMinimized:
        win.restore()
        
    win_x, win_y, win_w, win_h = win.left, win.top, win.width, win.height

    # 2. 局部截图 ROI：微信操作栏固定在窗口底部，只截取底部 25% 的区域
    bottom_crop_h = int(win_h * 0.25)
    crop_x = win_x
    crop_y = win_y + (win_h - bottom_crop_h)
    crop_w = win_w
    crop_h = bottom_crop_h

    # 执行截屏并转为 OpenCV BGR 格式
    bbox = (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    screen = ImageGrab.grab(bbox=bbox)
    frame_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # 3. 读取模板图
    for path in template_path:
        template = cv2.imread(path)
        if template is None:
            continue
    if template is None:
        print(f"❌ 找不到模板图片: {template_path}，请确认图片文件存在！")
        return False

    temp_h, temp_w = template.shape[:2]

    # 4. 执行毫秒级模板匹配
    res = cv2.matchTemplate(frame_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print(f"当前最高匹配度: {max_val:.2f}")

    # 5. 判断最高匹配度是否达到预设阈值
    if max_val >= threshold:
        # max_loc 返回的是图标在【局部截图】中的左上角坐标 (rel_x, rel_y)
        rel_x, rel_y = max_loc
        
        # 计算图标中心在局部图中的相对坐标
        center_rel_x = rel_x + temp_w // 2
        center_rel_y = rel_y + temp_h // 2

        # 换算为屏幕【绝对坐标】
        abs_x = crop_x + center_rel_x
        abs_y = crop_y + center_rel_y

        # 执行点击
        pyautogui.click(abs_x, abs_y)
        print(f"⚡ 极速匹配成功！已点击‘保存’，屏幕坐标: ({abs_x}, {abs_y})")
        return True
    else:
        print(f"❌ 未能找到‘保存’图标（最高相似度仅 {max_val:.2f}，低于设定的 {threshold}）")
        return False

if __name__ == "__main__":
    # 调用函数，直接进行极速匹配点击
    click_save_button("微信")