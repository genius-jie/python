# -*- coding: utf-8 -*-
from base import action
from base.action import ElementActions
from lib.pages.set import 精准学 as jzx

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

    def test_home(self, action):
        # 打开用户信息-张诺安
        jzx.用户信息.pageinto(action)
        action.click(jzx.用户信息.切换用户)
        action.swipe_and_find_element( "x",jzx.用户信息.用户列表框,jzx.用户信息.用户列表数, jzx.用户信息.张近义).click()
        action.click(jzx.用户信息.点击切换)
        # action.click(jzx.用户信息.教材年级)
        # action.click(jzx.用户信息.年级)
        # action.click(jzx.用户信息.三年级)
        # eles=action.find_ele(jzx.用户信息.确定,is_Multiple=True)
        # print(len(eles))
        # # 遍历并点击每个链接
        # for ele in eles:
        #     ele.click()
        # action.sleep(2)
        # action.click(jzx.用户信息.地区)
        # action.click(jzx.用户信息.地区安徽省)
        # action.click(jzx.用户信息.安徽安庆市)
        # action.click(jzx.用户信息.确定)
        # action.click(jzx.用户信息.确定)


        # action.click(jzx.用户信息.张诺安)
        # eles=action.find_ele(jzx.用户信息.用户列表,is_Multiple=True)
        # eles[1].click()
        # action.click(jzx.用户信息.点击切换)
        # # 保存用户信息截图
        # action.save_image("用户信息")
        # # 断言显示
        # assert action.assert_by_image("用户信息.png", "用户信息核对图.png")
        # # 返回桌面
        # action.back_press()

    # 测试家庭作业
    def test_home_homework(self, action):
        # 打开错题本
        action.click(jzx.家庭作业辅导.首页按钮)
        # 保存错题本截图
        action.save_image("家庭作业辅导老师起身动画图")
        task="帮我识别图片中的老师的坐姿，如果双手合十，正襟危坐，就返回1，如果准备起身，或者已经起身了，就返回0"
        result=action.get_dify_imagetask("家庭作业辅导老师起身动画图.png", task)
        if(result=="1"):
            assert False, "老师起身动画未生效"
        # 调用dify费时，不需要再等待了action.wait_for_activity(jzx.家庭作业辅导.activity)
        action.save_image("家庭作业辅导")
        # 断言显示
        assert action.assert_by_image("家庭作业辅导.png", "家庭作业辅导核对图.png")
        # 返回桌面
        action.back_press()

    # 测试错题本
    def test_home_error_note(self, action):
        # 打开错题本
        jzx.错题本.pageinto(action)
        # 保存错题本截图
        action.save_image("错题本")
        # 断言显示
        action.assert_by_image("错题本.png", "错题本核对图.png")
        # 返回桌面
        action.back_press()


    def test_home2(self, action: ElementActions):
        answer=action.get_image_front("Screenshot_homepage.png")
        print("Answer:", answer)

    def test_home3(self, action: ElementActions):
        action.save_image("首页")
        result1 = action.assert_by_image("首页.png", "Screenshot_homepage.png")
        print(result1)
