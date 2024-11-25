import os
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
from PIL import Image

# 获取当前脚本文件所在的目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "../data/screenShot/首页2.png")

# 使用 PIL 读取图像
pil_image = Image.open(image_path)

# 将 PIL 图像转换为 OpenCV 格式
img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# 使用 Tesseract 提取文字信息
tess_text = pytesseract.image_to_data(img, output_type=Output.DICT, lang='chi_sim')
print(tess_text['text'])
def find_word_coordinates(word, tess_text):
    word_coords = []
    word_length = len(word)

    for i in range(len(tess_text['text']) - word_length + 1):
        current_text = ''.join(tess_text['text'][i:i + word_length])
        if current_text == word:
            x = tess_text['left'][i]
            y = tess_text['top'][i]
            w = sum(tess_text['width'][i:i + word_length])
            h = max(tess_text['height'][i:i + word_length])
            word_coords.append((x, y, w, h))

    return word_coords

# 输入要查找的词语
search_word = "第一讲"

# 查找词语的坐标
coordinates = find_word_coordinates(search_word, tess_text)

# 打印词语的坐标
if coordinates:
    for coord in coordinates:
        print(f"词语: {search_word}, 坐标: ({coord[0]}, {coord[1]}), 宽度: {coord[2]}, 高度: {coord[3]}")
else:
    print(f"未找到词语: {search_word}")
