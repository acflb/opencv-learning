import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw


def capture_window_roi(window_title, relative_box=None):
    """
    根据窗口标题获取窗口坐标，并截取区域 (ROI)

    :param window_title: 窗口标题（支持部分匹配，如 '雷电模拟器'）
    :param relative_box: 窗口内部答题区的相对坐标 (rel_x, rel_y, rel_w, rel_h)。
        如果为 None，则截取整个窗口。
    :return: (roi_img, absolute_box) -> OpenCV图像矩阵, 绝对屏幕坐标
    """
    # 1. 查找匹配标题的窗口
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        raise ValueError(
            f"未找到标题包含 '{window_title}' 的窗口！请检查窗口是否已打开。"
        )

    # 拿到第一个匹配的窗口
    win = windows[0]

    # 如果窗口被最小化了，尝试还原
    if win.isMinimized:
        win.restore()

    # 2. 获取窗口在屏幕上的绝对位置与尺寸
    win_x, win_y = win.left, win.top
    win_w, win_h = win.width, win.height

    print(
        f"找到窗口 '{win.title}' -> 屏幕位置: X={win_x}, Y={win_y}, 宽度={win_w}, 高度={win_h}"
    )

    # 3. 计算最终要截取的区域 (ROI)
    if relative_box is None:
        # 默认截取整个窗口
        abs_x, abs_y, abs_w, abs_h = win_x, win_y, win_w, win_h
    else:
        # 根据相对偏移计算在全屏上的绝对坐标
        rel_x, rel_y, rel_w, rel_h = relative_box
        abs_x = win_x + rel_x
        abs_y = win_y + rel_y
        abs_w = rel_w
        abs_h = rel_h

    # 4. 截取屏幕指定区域 (PIL ImageGrab 用的 bbox 参数是: left, top, right, bottom)
    bbox = (abs_x, abs_y, abs_x + abs_w, abs_y + abs_h)
    screen = ImageGrab.grab(bbox=bbox)

    # 5. PIL 图像转 OpenCV 格式 (BGR)
    screen_np = np.array(screen)
    frame = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    return frame, (abs_x, abs_y, abs_w, abs_h)


# ==================== 测试与使用示例 ====================
if __name__ == "__main__":
    # 替换为你的目标窗口标题（支持模糊匹配，比如“雷电”、“夜神”、“微信”等）
    TARGET_WINDOW_TITLE = "firefox"

    # 假设答题框在模拟器内部：
    # 距离模拟器左边框 50 像素，顶边框 100 像素，宽 400，高 500
    # 如果想截取整个窗口，可以将 RELATIVE_BOX 设为 None
    RELATIVE_BOX = (50, 100, 400, 500)  # (rel_x, rel_y, width, height)

    try:
        print("正在获取窗口截图...")
        roi_img, abs_box = capture_window_roi(
            TARGET_WINDOW_TITLE, relative_box=RELATIVE_BOX
        )

        print(f"实际截取屏幕绝对坐标: {abs_box}")

        # 保存截图供检查
        cv2.imwrite("debug_window_crop.png", roi_img)
        print("截图保存成功，请查看 debug_window_crop.png 确认截取区域是否准确！")

    except Exception as e:
        print(f"出错: {e}")
