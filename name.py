import os
import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab
from cnocr import CnOcr

# 1. 初始化 CnOcr 引擎
print("正在初始化 CnOcr...")
ocr = CnOcr()

# 2. 读取锚点图标 (加号图标 plus_icon.png)
TEMPLATE_PATH = "./images/plus_icon.png"


def get_wechat_contact_adaptive():
    """
    通过 OpenCV 寻找 `⊕` 图标位置，自适应动态定位并识别联系人名字
    """
    # 获取微信窗口
    wins = gw.getWindowsWithTitle("微信")
    if not wins:
        print("❌ 未找到微信窗口！")
        return "未识别联系人"

    win = wins[0]
    if win.isMinimized:
        win.restore()
    win.activate()

    # 1. 截取微信顶部整个栏目（宽一些，包含搜索栏和聊天窗口顶部）
    # 顶部高度设为 100 像素，足以覆盖 ⊕ 图标和聊天标题
    crop_left = win.left
    crop_top = win.top
    crop_right = win.left + win.width
    crop_bottom = win.top + 120

    full_header_img = ImageGrab.grab((crop_left, crop_top, crop_right, crop_bottom))

    # 将 PIL Image 转为 OpenCV 格式 (BGR)
    img_np = np.array(full_header_img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 2. 读取模板图 `⊕` 图标
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ 找不到模板图片: {TEMPLATE_PATH}，请确保该文件在脚本目录下！")
        return "未识别联系人"

    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
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

        # 【调试用】保存截取的联系人小图，确认是否准确定位
        name_crop.save("debug_name_crop.png")

        # 5. 送给 CnOcr 进行识别
        ocr_results = ocr.ocr(name_crop)

        if ocr_results:
            # 调试输出完整的数组内容
            # print("识别结果原始文本:", ocr_results)

            # 【核心修改】：遍历拼接列表中的所有识别结果
            raw_text = "".join([item["text"].strip() for item in ocr_results])
            print(f"🔍 CnOcr 识别文本: {raw_text}")

            # 清理非法文件名字符 (Windows 文件夹名字禁止包含这些字符)
            cleaned_name = raw_text
            for char in r'/\:<>?*|":':
                cleaned_name = cleaned_name.replace(char, "_")

            return cleaned_name
        else:
            print("⚠️ 找到了 ⊕ 图标，但在对应右侧区域未识别出文字")
    else:
        print(f"⚠️ 未能找到 ⊕ 图标 (最大匹配度仅为: {max_val:.2f})")

    return "未识别联系人"


if __name__ == "__main__":
    contact = get_wechat_contact_adaptive()
    print("✅ 最终识别的联系人名称:", contact)
