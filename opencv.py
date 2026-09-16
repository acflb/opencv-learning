import ctypes
import os
import time
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import pyperclip
from cnocr import CnOcr
from PIL import ImageGrab
from pywinauto.application import Application

import keyboard


BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"
TEMPLATE_PATH = IMAGE_DIR / "plus_icon.png"
SAVE_TEMPLATE_PATHS = (
    IMAGE_DIR / "save_icon_dark.png",
    IMAGE_DIR / "save_icon_light.png",
)
BASE_SAVE_PATH = Path.home() / "Desktop"
INVALID_FILENAME_CHARS = '/\\:<>?*|"'
global OCR
OCR = None
OCR = CnOcr()


def get_wechat_contact_adaptive():
    """
    通过 OpenCV 寻找 `⊕` 图标位置，自适应动态定位并识别联系人名字
    """
    # 获取微信窗口
    win = get_window("微信")
    if win is None:
        print("❌ 未找到微信窗口！")
        return "未识别联系人"

    win.activate()

    # 1. 截取微信顶部整个栏目（宽一些，包含搜索栏和聊天窗口顶部）
    # 顶部高度设为 100 像素，足以覆盖 ⊕ 图标和聊天标题
    crop_left = win.left
    crop_top = win.top
    crop_right = win.left + win.width
    crop_bottom = win.top + 120

    full_header_img = ImageGrab.grab((crop_left, crop_top, crop_right, crop_bottom))

    # 模板匹配只需要灰度图，避免不必要的 RGB -> BGR 转换。
    img_gray = cv2.cvtColor(np.asarray(full_header_img), cv2.COLOR_RGB2GRAY)

    template = load_template(TEMPLATE_PATH)
    if template is None:
        print(f"❌ 找不到模板图片: {TEMPLATE_PATH}，请确保该文件在脚本目录下！")
        return "未识别联系人"

    th, tw = template.shape[:2]

    # 3. 使用 OpenCV 模板匹配，寻找 ⊕ 图标的坐标
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 设置匹配阈值，大于 0.7 说明找到了 ⊕ 图标
    if max_val > 0.7:
        icon_x, icon_y = max_loc
        print(f"🎯 成功定位 ⊕ 图标坐标: x={icon_x}, y={icon_y} (匹配度: {max_val:.2f})")

        # 4. 根据 ⊕ 图标的位置计算联系人名字所在的 ROI 区域 (Region of Interest)
        # 从 ⊕ 图标右侧偏移一定距离（根据你的界面，大约右移 40~60 像素）
        name_left = icon_x + tw + 5  # ⊕ 图标右边缘往右 20 像素
        name_top = icon_y - 5  # 稍微向上对齐
        name_right = name_left + 300  # 联系人名字的宽度（给 300 像素足够显示长名字）
        name_bottom = name_top + th + 15  # 高度与图标类似

        # 截取联系人名字的小图
        name_crop = full_header_img.crop((name_left, name_top, name_right, name_bottom))

        # 5. 送给 CnOcr 进行识别
        ocr_results = OCR.ocr(name_crop)

        if ocr_results:
            # 调试输出完整的数组内容
            # print("识别结果原始文本:", ocr_results)

            # 【核心修改】：遍历拼接列表中的所有识别结果
            raw_text = "".join([item["text"].strip() for item in ocr_results])
            print(f"🔍 CnOcr 识别文本: {raw_text}")

            # 清理非法文件名字符 (Windows 文件夹名字禁止包含这些字符)
            cleaned_name = raw_text.translate(
                str.maketrans({char: "_" for char in INVALID_FILENAME_CHARS})
            )

            return cleaned_name
        else:
            print("⚠️ 找到了 ⊕ 图标，但在对应右侧区域未识别出文字")
    else:
        print(f"⚠️ 未能找到 ⊕ 图标 (最大匹配度仅为: {max_val:.2f})")

    return "未识别联系人"


""" 点击保存 """
# 解决 Windows 高分屏缩放导致的坐标偏移问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# 设置 PyAutoGUI 动作间极短暂停
pyautogui.PAUSE = 0.01

def click_save_button(window_title="微信", template_paths=SAVE_TEMPLATE_PATHS, threshold=0.8):
    """
    通过模板匹配毫秒级查找并点击微信中的“保存”按钮
    
    :param window_title: 目标窗口标题
    :param template_path: 保存图标的切图路径
    :param threshold: 匹配相似度阈值（0.8 表示 80% 以上相似即认定匹配）
    """
    # 1. 获取微信窗口
    win = get_window(window_title)
    if win is None:
        print(f"❌ 未找到标题包含 '{window_title}' 的窗口")
        return False

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
    frame_gray = cv2.cvtColor(np.asarray(screen), cv2.COLOR_RGB2GRAY)

    # 3. 使用第一个可用模板，模板会在进程内缓存。
    templates = [load_template(path) for path in template_paths]
    templates = [template for template in templates if template is not None]
    if not templates:
        print(f"❌ 找不到模板图片: {template_paths}，请确认图片文件存在！")
        return False

    # 4. 匹配两个主题模板，取最高分，避免主题变化导致误判。
    matches = [
        (cv2.minMaxLoc(cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)), template)
        for template in templates
    ]
    best_match = max(matches, key=lambda item: item[0][1])
    _, max_val, _, max_loc = best_match[0]
    template = best_match[1]
    temp_h, temp_w = template.shape[:2]

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



""" 存储到对应联系人文件夹 """
def handle_select_folder_dialog(contact_name):
    """
    Step 2 (特制版): 处理弹出的【选择文件夹】对话框。
    在此对话框内新建文件夹并选中。
    """
    try:
        app = Application(backend="win32").connect(title_re="选择文件夹", class_name="#32770", timeout=1)
        folder_dialog = app.window(title_re="选择文件夹", class_name="#32770")
        folder_dialog.set_focus()
        pyautogui.hotkey('alt', 'd')
        time.sleep(0.2)
        pyperclip.copy(str(BASE_SAVE_PATH))
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(0.5)

        # 2. 快捷键 Ctrl+Shift+N 新建文件夹
        pyautogui.hotkey('ctrl', 'shift', 'n')
        time.sleep(0.5)

        # 3. 输入联系人名字作为新文件夹名并确认
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        
        time.sleep(0.2)
        pyautogui.press('enter')  #  新建文件夹
        time.sleep(0.4)
        pyautogui.hotkey('y')

        # 4. 触发右下角的“选择文件夹”按钮
        folder_dialog.child_window(title="选择文件夹", class_name="Button").click_input()
        print(f"🎉 文件保存成功！保存路径为: 【桌面 / {contact_name}】")
        return True

    except Exception as e:
        print(f"❌ 操控【选择文件夹】窗口失败: {e}")
        return False


def get_window(title):
    """返回第一个匹配窗口，并在需要时恢复窗口。"""
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        return None
    window = windows[0]
    if window.isMinimized:
        window.restore()
    return window


@lru_cache(maxsize=8)
def load_template(path):
    """缓存灰度模板，避免每次操作重复读取和转换图片。"""
    return cv2.imread(os.fspath(path), cv2.IMREAD_GRAYSCALE)


# def get_ocr():
#     """只在确实需要识别联系人时初始化 OCR 引擎。"""
#     global OCR
#     if OCR is None:
#         print("正在初始化 CnOcr...")
#         OCR = CnOcr()
#     return OCR

def do_click_task():
    print("触发啦喵！")
    contact = get_wechat_contact_adaptive()
    if click_save_button("微信"):
        handle_select_folder_dialog(contact)


if __name__ == "__main__":
    keyboard.add_hotkey('ctrl+alt+p', do_click_task)
    print("后台监听中，按 Ctrl+Alt+P 触发~")
    keyboard.wait()  # 让程序一直挂着，不退出
    # contact = get_wechat_contact_adaptive()
    # if click_save_button("微信"):
    #     handle_select_folder_dialog(contact)
    # print("✅ 最终识别的联系人名称:", contact)
