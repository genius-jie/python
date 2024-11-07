# -*- coding: utf-8 -*-
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


# 测试用例demo，pytest框架自动加载执行


class Test_demo():

    def test_home(self, action: ElementActions):
        # 张立杰注释
        # action.click(p.桌面.八年级)
        # 截图识别元素
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "家庭作业.png")
        with open(image_path, 'rb') as png_file:
            b64_data = base64.b64encode(png_file.read()).decode('UTF-8')
        action._find_element(locator=dict(name="elename", type=AppiumBy.IMAGE, value=b64_data),
                             is_need_displayed=False).click()
        action.sleep(1)
