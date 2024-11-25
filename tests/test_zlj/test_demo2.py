# -*- coding: utf-8 -*-
from base import action
from base.action import ElementActions
from lib.pages.set import MainPages as p
from base.verify import NotFoundTextError
from base.utils import log
import uiautomator2 as u2
import os
import base64
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import imagehash
from PIL import Image
from pathlib import Path
import base64


# 测试用例demo，pytest框架自动加载执行


class Test_demo():

    def test_home(self, action: ElementActions):
        # 张立杰注释
        action.click(p.桌面.错题本)
        # 截图识别元素
        # action.save_image("首页")
        # action.sleep(1)

    def test_home2(self, action: ElementActions):
        answer=action.get_image_front("Screenshot_homepage.png")
        print("Answer:", answer)

    def test_home3(self, action: ElementActions):
        action.save_image("首页")
        result1 = action.assert_by_image("首页.png", "Screenshot_homepage.png")
        print(result1)
