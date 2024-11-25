import os

import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image

# 列出支持的语言
print(pytesseract.get_languages(config=''))

# print(pytesseract.image_to_string(Image.open('test.png'), lang='chi_sim+eng'))
def read_image(name):
    # config = r'--oem 3 --psm 6 outputbase digits' #只识别数字
    config = r'-c tessedit_char_whitelist=0123456789 --psm 6' #只识别数字
    # config = r'-c tessedit_char_blacklist=0123456789 --psm 6'#不识别数字
    print(pytesseract.image_to_string(Image.open(name), config=config, lang='chi_sim'))
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "../data/screenShot/img.png")
    read_image(image_path)

if __name__ == '__main__':
    main()