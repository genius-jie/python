# -*- coding: utf-8 -*-

import pytest, os, logging
from appium import webdriver
from base.action import ElementActions
from base.environment import EnvironmentAndroid
from base.utils import log
from appium.options.android import UiAutomator2Options



# pytest的setup和down工作


# 初始化driver对象，在package的领域只会执行一次
@pytest.fixture(scope="package")
def driverenv():
    env = EnvironmentAndroid()
    current_device = env.current_device

    capabilities = {
        'platformName': current_device.get("platformName"),
        'platformVersion': current_device.get("platformVersion"),
        'deviceName': current_device.get("deviceName"),
        'udid': current_device.get("deviceName"),
        'systemPort': current_device.get('systemPort'),
        # 'app': env.appium.get("app"),
        'clearSystemFiles': True,
        # 'appActivity': env.appium.get("appActivity"),
        # 'appPackage': env.appium.get("appPackage"),
        'automationName': 'UIAutomator2',
        'noSign': True,
        # 'recreateChromeDriverSessions': True,
        "unicodeKeyboard": True,
        "noReset": True,
        "fullReset": False,
        "newCommandTimeout": 300
    }
    log.info(capabilities)
    # systemPort=current_device.get('systemPort')
    # if systemPort!=None:
    #     capabilities['systemPort']=systemPort
    #
    log.info('当前执行的appium相关配置为：' + str(capabilities))

    host = current_device.get('appiumserver')


    # 创建Appium选项对象
    # options = AppiumOptions()
    # for key, value in capabilities.items():
    #     options.set_capability(key, value)
    options = UiAutomator2Options().load_capabilities(capabilities)
    # 初始化WebDriver
    #
    # try:
    #     driver = WebDriver(command_executor='http://127.0.0.1:4723/wd/hub', options=options)
    #     # 进行其他操作...
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    driver = webdriver.Remote(f'http://127.0.0.1:4723', options=options)
    # driver = webdriver.Remote(host,  options=options)
    driver.update_settings({"fixImageTemplatescale": True})
    driver.implicitly_wait(10)
    return driver


# 初始化ElementActions类的对象，在package的领域只会执行一次，并且通过yield实现package执行结束前的数据清理工作
@pytest.fixture(scope="package")
def action(driverenv):
    element_action = ElementActions(driverenv)
    yield element_action  # 返回并且挂载ElementActions的实例，在对应作用域结束前，执行driver.quit()

    element_action.driver.quit()


# 用例执行前后：加入日志说明、结束前的截图输出到报告上
@pytest.fixture(autouse=True)
def caserun(action):
    log.info("————————————————————————执行用例 ----------——————————————")
    yield
    action.sleep(1).get_img("用例结束前的截图")
    log.info("————————————————————————该用例执行结束 ----------——————————————")
