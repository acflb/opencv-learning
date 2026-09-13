import cv2
import numpy as np
from PIL import ImageGrab
from cnocr import CnOcr
import requests
import json

# 1. 初始化 CnOCR 引擎 (可配置使用 CPU 或 ONNX 加速)
ocr = CnOcr()

def capture_roi(rect):
    """
    使用 OpenCV 截取屏幕指定区域 (ROI)
    rect: (x, y, width, height) 区域坐标
    """
    x, y, w, h = rect
    # 截取屏幕全图
    screen = ImageGrab.grab()
    screen_np = np.array(screen)
    # PIL(RGB) 转换成 OpenCV(BGR) 格式
    frame = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    
    # 裁剪答题区域
    roi = frame[y:y+h, x:x+w]
    return roi

def preprocess_image(img):
    """
    OpenCV 预处理：增强文本清晰度，提高 CnOCR 识别率
    """
    # 转灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 放大图片 (针对小字体/低分辨率截图，放大能显著提升识别率)
    resized = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    
    # 自适应二值化 (去除背景杂色，突出文字)
    # 注意：如果背景是暗色文字是亮色，需进行反色处理
    binary = cv2.adaptiveThreshold(
        resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    return binary

def recognize_text(img):
    """
    调用 CnOCR 进行文本识别
    """
    # CnOCR 可以直接接收 ndarray 图像矩阵
    results = ocr.ocr(img)
    
    # 拼接识别出的各行文本
    lines = [item['text'] for item in results]
    full_text = "\n".join(lines)
    return full_text

def query_ai_answer(question_text, api_key):
    """
    将识别到的题目和选项传给大模型（如 DeepSeek / ChatGPT）匹配答案
    """
    url = "https://api.deepseek.com/chat/completions" # 替换为您使用的 API 地址
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"你是一个答题助手，请阅读以下题目和选项，直接给出最准确的选项及原因：\n\n{question_text}"
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"请求 API 失败: {e}"

# ==================== 主流程运行 ====================
if __name__ == "__main__":
    # 1. 设定答题窗口所在屏幕的位置 (x, y, 宽度, 高度)
    # 提示：可以使用 Photoshop、QQ/微信截图工具测量准确坐标
    ANSWER_BOX = (0, 0, 100, 600) 
    
    print("正在截取答题区域...")
    roi_img = capture_roi(ANSWER_BOX)
    
    # 保存原始截图以供检查坐标是否正确
    cv2.imwrite("debug_crop.png", roi_img)
    
    # 2. 图像预处理
    processed_img = preprocess_image(roi_img)
    cv2.imwrite("debug_processed.png", processed_img)
    
    # 3. CnOCR 识别
    print("正在识别文本...")
    ocr_result = recognize_text(processed_img)
    print("\n--- 识别结果 ---")
    print(ocr_result)
    print("----------------\n")
    
    # 4. 获取答案 (替换为您自己的 API Key)
    # API_KEY = "your_api_key_here"
    # if ocr_result.strip() and API_KEY != "your_api_key_here":
    #     print("正在获取 AI 答案...")
    #     answer = query_ai_answer(ocr_result, API_KEY)
    #     print("\n=== AI 推荐答案 ===")
    #     print(answer)
    # else:
    #     print("提示：识别为空或未配置 API Key，请检查坐标与配置。")