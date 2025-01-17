# -*- coding: utf-8 -*-
import base64
import os
from selenium.webdriver.support import expected_conditions as EC
import imagehash
import requests
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from pytesseract import pytesseract
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from base.utils import log, singleton, Waittime_count
import allure, time
from base.verify import NotFoundElementError, NotFoundTextError
from base.environment import EnvironmentAndroid
from PIL import Image
from pathlib import Path


# 封装元素操作的类


@singleton
class ElementActions:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.env = EnvironmentAndroid()
        # 通过driver.get_window_size()获取的分辨率会不准确，所以读取配置的Resolution
        self.Resolution = self.env.current_device.get('Resolution')

        if self.Resolution == None:
            self.Resolution = [1080, 1920]  # 2880 1800

        self.width = self.Resolution[0]
        self.height = self.Resolution[1]
        log.info(self.width)

    def reset(self, driver: webdriver.Remote):
        """因为是单例,所以当driver变动的时候,需要重置一下driver

        Args:
            driver: driver

        """
        self.driver = driver

    def get_img(self, name="app截图"):
        # 获取当前app的截图并加载到报告的对应附件中
        png_data = self.driver.get_screenshot_as_png()
        current_time = time.strftime('_%H:%M:%S_', time.localtime(time.time()))
        current_name = name + current_time + '.png'
        allure.attach(png_data, name=current_name, attachment_type=allure.attachment_type.PNG)

    def save_image(self, name="app截图"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        screenshot_dir = os.path.join(current_dir, "../data/screenShot")
        screenshot_path = os.path.join(screenshot_dir, f"{name}.png")
        # 检查历史截图是否存在，如果存在则删除
        # if os.path.exists(screenshot_path):
        #     os.remove(screenshot_path)
        #     print(f"已删除旧截图: {screenshot_path}")
        try:
            png_data = self.driver.get_screenshot_as_png()
            with open(screenshot_path, 'wb') as f:
                f.write(png_data)
            f.close()
            print(f"截图已保存到: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error taking screenshot: {e}")
        return None

    def start_activity(self, appPackage, app_activity, **opts):
        message = 'start_activity:    ' + app_activity
        params = {
            # zlj:com.jm.android.jumei/.home.activity.NewHomeActivity
            # 'intent': self.env.appium.get("appPackage") + app_activity,
            'intent': appPackage + app_activity,
            **opts
        }
        # log.info(f"Params: {params}")
        try:
            # 使用 execute_script 方法调用 mobile: startActivity
            self.driver.execute_script('mobile: startActivity', params)
            log.info("Activity started successfully")
        except Exception as e:
            log.error(f"Failed to start activity: {e}")
            raise

        # 等待指定的活动启动
        self.driver.wait_activity(app_activity, 2, interval=1)
        # self.driver.start_activity(self.env.appium.get("appPackage"), app_activity, **opts)
        # self.driver.execute_script('mobile: startActivity', params)
        # self.driver.wait_activity(app_activity, 10, interval=0.3)
        return self

    def wait_for_activity(self, activity, timeout=1):
        self.driver.wait_activity(activity, timeout, interval=1)
        return self

    def sleep(self, s, islog=True):
        if islog == True:
            message = "sleep等待 {} s ".format(str(s))
            log.info(message)
        time.sleep(s)
        return self

    def back_press(self):
        self._send_key_event('KEYCODE_BACK')


    def home_press(self):
        self.driver.background_app(1)

    def tap(self, locator):
        # 获取当前屏幕的分辨率，元素通过相对位置点击
        """

        :param locator: value格式为 "x,y"
        :return:
        """
        if locator.get('type') != "tap":
            log.error('定位方式错误，不能通过坐标位置定位点击 \nlocator: {}'.format(str(locator)))
        else:
            position = locator.get('value').split(',')
            x = int(position[0]) * self.width / 1080
            y = int(position[1]) * self.height / 1920
            positions = [(x, y)]
            log.info(
                "通过坐标({},{}), 成功点击 页面【{}】的元素【{}】".format(x, y, locator.get('page'), locator.get('name')))

            self.driver.tap(positions, duration=400)

    def long_press(self, locator, time=2000):
        # 长按操作，locator的type为tap时支持坐标位置长按
        """
        :param locator:
        :param time: 单位毫秒
        :return:
        """
        if locator.get('type') == "tap":
            position = locator.get('value').split(',')
            x = int(position[0]) * self.width / 1080
            y = int(position[1]) * self.height / 1920
            # 使用W3C Actions API进行长按
            actions = ActionBuilder(self.driver)
            finger = actions.add_pointer_input(PointerInput(interaction.POINTER_TOUCH, "finger"))
            finger.create_pointer_move(x=x, y=y)
            finger.create_pointer_down(interaction.BUTTON_MAIN)
            finger.create_pause(time)  # 长按时长
            finger.create_pointer_up(interaction.BUTTON_MAIN)
            actions.perform()

        else:
            ele = self._find_element(locator)
            # 对元素进行长按
            actions = ActionBuilder(self.driver)
            finger = actions.add_pointer_input(PointerInput(interaction.POINTER_TOUCH, "finger"))
            finger.create_pointer_move(to_element=ele)
            finger.create_pointer_down(interaction.BUTTON_MAIN)
            finger.create_pause(time)  # 长按时长
            finger.create_pointer_up(interaction.BUTTON_MAIN)
            actions.perform()

        log.info("[长按] 页面【{}】的元素【{}】".format(locator.get('page'), locator.get('name')))

    def swip_left(self, parent_locator, count=1):
        """向左滑动,一般用于ViewPager

        Args:
            count: 滑动次数

        """
        ele = self.find_ele(parent_locator)
        ele_location = ele.location
        ele_size = ele.size
        for x in range(count):
            self.driver.swipe(ele_location['x'] + ele_size['width'] - 10, ele_location['y'] + ele_size['height'] / 2,
                              ele_location['x'], ele_location['y'] + ele_size['height'] / 2, 1000)
        log.info("----------向左滑动----------")
        return self

    def swipe_and_find_element(self, direction, parent_locator, childs_locator, target_element_locator):
        directions = []
        if direction == "x":
            directions = ["right", "left"]
        elif direction == "y":
            directions = ["down", "up"]
        else:
            log.error("参数direction错误，请输入x或y")
            return None
        for dirn in directions:
            try:
                target_element = self._swipe_and_find_element_(dirn, parent_locator, childs_locator,target_element_locator)
                if target_element:
                    return target_element
            except Exception as e:
                # 记录异常信息，但继续尝试其他方向
                print(f"Error swiping {dirn}: {e}")
        return None

    def _swipe_and_find_element_(self, direction, parent_locator, childs_locator, target_element_locator):
        all_elements = []
        new_elements = self.find_ele(childs_locator, is_Multiple=True)
        while new_elements and not self.is_element_exist(target_element_locator):
            all_elements.extend(new_elements)
            if direction == 'right':
                self.swip_right(parent_locator)
            elif direction == 'left':
                self.swip_left(parent_locator)
            elif direction == 'down':
                self.swip_left(parent_locator)
            elif direction == 'up':
                self.swip_left(parent_locator)
            else:
                break
            elements = self.find_ele(childs_locator, is_Multiple=True)
            new_elements = [elem for elem in elements if elem not in all_elements]
            log.info("滑动后剩余元素数量：{}".format(len(new_elements)))
        if self.is_element_exist(target_element_locator):
            return self.find_ele(target_element_locator)
        return None

    def swip_right(self, parent_locator, count=1):
        """
            向右滑
        """
        ele = self.find_ele(parent_locator)
        ele_location = ele.location
        ele_size = ele.size
        for x in range(count):
            self.driver.swipe(ele_location['x'], ele_location['y'] + ele_size['height'] / 2,
                              ele_location['x'] + ele_size['width'] - 10, ele_location['y'] + ele_size['height'] / 2,
                              100)
        log.info("----------向右滑动----------")
        return self

    def swip_down(self, parent_locator, count=1):
        """向下滑动,常用于下拉刷新

        Args:
            count: 滑动次数
            half:是否为滑动一半
        """
        ele = self.find_ele(parent_locator)
        ele_location = ele.location
        ele_size = ele.size
        for x in range(count):
            self.driver.swipe(ele_location['x'] / 2, ele_location['y'], ele_location['x'] / 2,
                              ele_location['y'] + ele_size['height'] - 10, 100)
        log.info("---------向下滑动----------")
        return self

    def swip_up(self, parent_locator, count=1):
        """向上滑动,常用于下拉刷新

        Args:
            count: 滑动次数
        """

        ele = self.find_ele(parent_locator)
        ele_location = ele.location
        ele_size = ele.size
        for x in range(count):
            self.driver.swipe(ele_location['x'] / 2, ele_location['y'] + ele_size['height'] - 10, ele_location['x'] / 2,
                              ele_location['y'], 100)

        log.info("----------向上滑动---------")
        return self

    def find_ele_child(self, locator_parent, locator_child, is_Multiple=False, wait=1):
        # 通过父结点定位方式查找子结点元素
        # 定位方式限制：如果子节点定位方式为name时，父节点定位方式只能为id、name、class name

        """
        :param locator_parent: 父节点定位器对象
        :param locator_child:  子节点定位器对象
        :param is_Multiple: 是否查找多个
        :param wait:
        :return: 查找不到时返回None或者[]
        """

        if locator_child['type'] != 'name':
            element_parent = self.find_ele(locator_parent)
            return self.find_ele_child_byelement(element_parent, locator_child, is_Multiple, wait)
        else:
            return self._find_ele_child_byname(locator_parent, locator_child, is_Multiple, wait)

    def find_ele_child_byelement(self, element_parent, locator_child, is_Multiple=False, wait=1):
        # 通过父结点元素查找子结点元素,不支持name定位方式，支持查找到很多个子节点

        if locator_child['type'] == 'name':
            log.error('find_ele_child_byelement的定位方式错误')
            raise NotFoundElementError

        value_child, type_child = locator_child['value'], locator_child['type']
        try:
            WebDriverWait(self.driver, wait).until(
                lambda driver: element_parent.find_element(type_child, value_child))

            log.info(
                "页面【{}】的元素【{}】成功查询到查找子节点 元素【{}】"
                .format(locator_child.get("page"), element_parent,
                        locator_child.get('name')))

            if is_Multiple == False:
                return element_parent.find_element(type_child, value_child)
            else:
                return element_parent.find_elements(type_child, value_child)
        except:
            log.info(
                "页面【{}】的元素【{}】未能查询到查找子节点 元素【{}】\n locator_child{}"
                .format(locator_child.get("page"), element_parent,
                        locator_child.get('name'), locator_child))

            if is_Multiple == False:
                return None
            else:
                return []

    def find_ele_parent(self, locator_parent, locator_child, wait=1):
        # 通过子节点来定位父节点元素,locator_parent有多个元素（通过遍历父节点，找出包含符合条件子节点的父节点）
        # 注意，子节点必须唯一，不然找到的父节点可能只是第一个匹配上的
        # 定位方式限制 子节点 定位方式不能是name

        if locator_child['type'] == 'name':
            log.error('find_ele_parent的定位方式错误')
            raise NotFoundElementError

        elelist_parent = self.find_ele(locator_parent, is_Multiple=True)

        for element_parent in elelist_parent:
            child_eles = self.find_ele_child_byelement(element_parent, locator_child, is_Multiple=True, wait=wait)
            log.info(child_eles)

            if child_eles != []:
                log.info("成功遍历查找到元素 {}".format(child_eles))
                return element_parent
        log.info('未找到元素, elelist_parent:{}'.format(str(elelist_parent)))

        return None

    def find_ele_fromparent(self, locator_tmp, locator_target, is_Multiple=False, wait=1):
        # 通过uiautomator查找定位元素的兄弟节点元素,不支持xpath，且兄弟节点必须同级
        """
        支持的定位方式有：text(name),description(特有的),id,class name
        """

        log.info("页面【{}】通过元素【{}】查找兄弟元素【{}】".format(locator_tmp.get("page"), locator_tmp.get('name'),
                                                               locator_target.get("name")))

        map = {
            "name": "textContains",
            "description": "descriptionContains",
            "id": "resourceId",
            "class name": "className"
        }
        type_tmp = map.get(locator_tmp["type"])
        type_target = map.get(locator_target["type"])

        if type_tmp == None or type_target == None:
            log.error('当前定位方式不支持')
            raise NotFoundElementError

        value_tmp = locator_tmp["value"]
        value_target = locator_target["value"]

        ui_value = 'new UiSelector().{}(\"{}\").fromParent(new UiSelector().{}(\"{}\"))'.format(type_tmp, value_tmp,
                                                                                                type_target,
                                                                                                value_target)

        try:
            WebDriverWait(self.driver, wait).until(
                lambda driver: driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_value))

            if is_Multiple == False:
                return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_value)
            else:
                return self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, ui_value)
        except:
            log.info('页面【{}】未找到 元素【{}】\n locator: {}'.format(locator_tmp.get("page"), locator_target.get('name'),
                                                                    str(locator_target)))
            if is_Multiple == False:
                return None
            else:
                return []

    def find_ele(self, locator, is_Multiple=False, wait=1):
        # 通过定位器查找元素,不用于断言（断言元素存在用 is_element_exist ，断言页面是否含有对应文本关键字的请用is_text_displayed）
        # 需要查找多个时，返回list
        # 没有查找到时，返回None 或 []

        """
               Args:
                   locator:  定位器对象
                   is_Multiple: 是否查找多个
        """

        log.info("查找 页面【{}】的元素【{}】".format(locator.get("page"), locator.get("name")))
        if is_Multiple == False:
            return self._find_element(locator, is_raise=False, wait=wait)
        else:
            return self._find_elements(locator, is_raise=False, wait=wait)

    def find_element_ByImage(self, imageName):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "../tests/test_zlj/" + imageName + ".png")
        with open(image_path, 'rb') as png_file:
            b64_data = base64.b64encode(png_file.read()).decode('UTF-8')
        workelement = self._find_element(locator=dict(name="elename", type=AppiumBy.IMAGE, value=b64_data),
                                         is_need_displayed=True)
        return workelement

    def is_element_exist(self, locator, wait=1):
        """检查元素是否存在"""

        if self._find_element(locator, is_raise=False, wait=wait) == None:
            log.error("没有查找到  页面【{}】的元素【{}】".format(locator.get("page"), locator.get("name")))
            return False
        else:
            log.info("已查找到  页面【{}】的元素【{}】".format(locator.get("page"), locator.get("name")))
            return True

    def click(self, locator, count=1, wait=2):
        """基础的点击事件

        Args:
            locator:定位器
            count: 点击次数
        """
        msg = "[点击]  页面【{}】的元素【{}】".format(locator.get("page"), locator.get("name"))
        log.info(msg)

        element = self._find_element(locator, wait=wait)

        self.click_ele(element, count, is_log=False)

        return self

    def click_ele(self, element, count=1, is_log=True):
        # 对元素对象进行点击
        if is_log:
            log.info(f"[点击]{count}次元素 {element}")

        try:
            for _ in range(count):
                element.click()
                self.sleep(0.1)  # 点击之间的小延迟
        except Exception as e:
            log.error(f"点击元素时发生错误: {e}")
            # 根据需要决定是否抛出异常或继续执行
            # raise

        self.sleep(0.1)  # 最后一次点击后的延迟

        return self

    def get_text(self, locator):
        """获取元素中的text文本
        查找到单个元素，返回文本字符串

        Args:
            locator:定位器
            count: 点击次数

        Returns:
            如果没有该控件返回None

        Examples:
            TextView 是否显示某内容
        """
        element = self._find_element(locator, wait=1)
        log.info("获取元素中的text文本\n locator: \n{}".format(locator))
        return self.get_text_ele(element)

    def get_text_ele(self, element):
        if element != None:
            return element.get_attribute("text")
        else:
            return None

    def text(self, locator, value, clear_first=False, click_first=True):
        """输入文本

        Args:
            locator: 定位器
            value: 文本内容
            clear_first: 是否先清空原来文本
            click_first: 是否先点击选中
        Raises:
            NotFoundElementError

        """
        element = self._find_element(locator)
        log.info("在【{}】页面 对元素【{}】输入文本【{}】".format(locator.get("page"), locator.get("name"), value))

        self.text_ele(element, value, clear_first, click_first)

        return self

    def text_ele(self, element, value, clear_first=False, click_first=True):

        if click_first:
            element.click()
        if clear_first:
            element.clear()
        element.send_keys(value)

    def is_toast_show(self, message, wait=1):
        """Android检查是否有对应Toast显示,常用于断言
        Args:
            message: Toast信息
            wait:  等待时间
        Returns:
            True 显示Toast
        """

        toast_loc = ("xpath", ".//*[contains(@text,'%s')]" % message)
        try:
            WebDriverWait(self.driver, wait, 0.2).until(expected_conditions.presence_of_element_located(toast_loc))

            log.info("当前页面成功找到toast: %s" % message)
            return True

        except:
            log.error("当前页面中未能找到toast为: %s" % message)

            return False

    def is_text_displayed(self, text, retry_time=0, is_raise=False):
        """检查页面中是否有文本关键字

        如果希望检查失败的话,不再继续执行case,使用 is_raise = True

        Args:
            text: 关键字(请确保想要的检查的关键字唯一)
            is_retry: 是否重试,默认为true
            retry_time: 重试次数,默认为5
            is_raise: 是否抛异常
        Returns:
            True: 存在关键字
        Raises:
            如果is_raise = true,可能会抛NotFoundElementError

        """

        try:
            if retry_time != 0:
                result = WebDriverWait(self.driver, retry_time).until(
                    lambda driver: self._find_text_in_page(text))
            else:
                result = self._find_text_in_page(text)
            if result == True:
                log.info("[Text]页面中找到了 %s 文本" % text)
            return result
        except TimeoutException:
            log.error("[Text]页面中未找到 %s 文本" % text)
            if is_raise:
                raise NotFoundTextError
            else:
                return False
    def is_clickable(self, locator):
        EC.element_to_be_clickable(locator)

    def dialog_ok(self, wait=1):
        locator = {'name': '对话框确认键', 'type': 'id', 'value': 'android:id/button1'}
        self.click(locator)

    def set_number_by_soft_keyboard(self, nums):
        """模仿键盘输入数字,主要用在输入取餐码类似场景

        Args:
            nums: 数字
        """
        list_nums = list(nums)
        for num in list_nums:
            self._send_key_event('KEYCODE_NUM', num)

    # ======================= private ====================

    def _find_ele_child_byname(self, locator_parent, locator_child, is_Multiple=False, wait=1):
        # 使用uiautomator通过父节点，定位子节点。

        value_parent, type_parent = locator_parent['value'], locator_parent['type']
        value_child, type_child = locator_child['value'], locator_child['type']

        try:
            map = {
                "name": "textContains",
                "id": "resourceId",
                "class name": "className"
            }
            type_parent = map.get(type_parent)

            if type_parent == None:
                log.error('当前定位方式不支持')
                raise NotFoundElementError

            ui_value = 'new UiSelector().{}(\"{}\").childSelector(new UiSelector().textContains(\"{}\"))'.format(
                type_parent, value_parent, value_child)

            WebDriverWait(self.driver, wait).until(
                lambda driver: driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_value))

            log.info("页面【{}】的元素【{}】成功查找子节点 元素【{}】".format(locator_parent.get("page"),
                                                                        locator_parent.get("name"),
                                                                        locator_child.get('name')))
            if is_Multiple == False:
                return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_value)
            else:
                return self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, ui_value)
        except:
            log.info(
                "页面【{}】的元素【{}】未能查询到查找子节点 元素【{}】\n locator_parent:{} \n locator_child{}"
                .format(locator_parent.get("page"), locator_parent.get("name"),
                        locator_child.get('name'), locator_parent, locator_child))

            if is_Multiple == False:
                return None
            else:
                return []

    def _find_text_in_page(self, text):
        """检查页面中是否有文本关键字
        拿到页面全部source,暴力检查text是否在source中
        Args:
            text: 检查的文本

        Returns:
            True : 存在

        """
        log.info("[查找] 文本 %s " % text)

        return text in self.driver.page_source

    def _find_element(self, locator, is_need_displayed=True, wait=1, is_raise=True):
        """查找单个元素,如果有多个返回第一个

        Args:
            locator: 定位器
            is_need_displayed: 是否需要定位的元素必须展示
            is_raise: 是否抛出异常

        Returns: 元素 ,没找到返回 None

        Raises: NotFoundElementError
                未找到元素会抛 NotFoundElementError 异常

        """

        waittime_count = Waittime_count(
            msg='[查找] 页面【{}】该元素【{}】等待时间:'.format(locator.get("page"), locator.get("name")))
        waittime_count.start()
        try:
            if is_need_displayed:
                WebDriverWait(self.driver, wait).until(
                    lambda driver: self._get_element_by_type(driver, locator).is_displayed())
            else:
                WebDriverWait(self.driver, wait).until(
                    lambda driver: self._get_element_by_type(driver, locator) is not None)

            waittime_count.end()
            return self._get_element_by_type(self.driver, locator)
        except Exception as e:

            if is_raise == True:
                log.error(
                    "【{}】页面中未能找到元素【{}】\n locator: \n {}".format(locator.get("page"), locator.get("name"),
                                                                         locator))
                raise NotFoundElementError
            else:
                return None

    def _find_elements(self, locator, wait=1, is_raise=False):
        """查找元素,可查找出多个

        Args:
            locator: 定位器
            is_raise: 是否抛出异常

        Returns:元素列表 或 []

        """
        try:
            WebDriverWait(self.driver, wait).until(
                lambda driver: self._get_element_by_type(driver, locator, False).__len__() > 0)
            return self._get_element_by_type(self.driver, locator, False)
        except:

            if is_raise == True:
                log.error(
                    "【{}】页面中未能找到元素【{}】\n locator: \n {}".format(locator.get("page"), locator.get("name"),
                                                                         locator))
                raise NotFoundElementError
            else:
                return []

    @staticmethod
    def _get_element_by_type(driver, locator, element=True):
        """通过locator定位元素(默认定位单个元素)

        Args:
            driver:driver
            locator:定位器
            element:
                true:查找单个元素
                false:查找多个元素

        Returns:单个元素 或 元素list

        """
        value = locator['value']
        ltype = locator['type']

        # find_element在安卓中appium定位不支持通过name查找,但uiautomator可以且速度快
        if ltype == 'name':
            ui_value = 'new UiSelector().textContains(\"{}\")'.format(value)
            return driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_value) if element else driver.find_elements(
                "-android uiautomator", ui_value)
        else:
            return driver.find_element(ltype, value) if element else driver.find_elements(ltype, value)

    def _send_key_event(self, arg, num=0):
        """
        操作实体按键
        Code码：https://developer.android.com/reference/android/view/KeyEvent.html
        Args:
            arg: event_list key
            num: KEYCODE_NUM 时用到对应数字


        """
        event_list = {'KEYCODE_HOME': 3, 'KEYCODE_BACK': 4, 'KEYCODE_MENU': 82, 'KEYCODE_NUM': 8}
        if arg == 'KEYCODE_NUM':
            self.driver.press_keycode(8 + int(num))
        elif arg in event_list:
            self.driver.press_keycode(int(event_list[arg]))

    def get_image_path(self, image_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        reference_image_path = os.path.join(current_dir, "../data/screenShot/" + image_name)
        return reference_image_path

    def get_dify_imagetask(self, image_name, task):
        # 本地文件路径
        image_path = self.get_image_path(image_name)
        # 文件MIME类型（根据文件实际类型选择）
        file_mime_type = 'image/png'  # 如果文件是PNG；如果是其他类型，则替换为相应的MIME类型
        # 设置API URL和API密钥
        api_key = 'app-xHRHJY3pStf6X88GPCscNqyC'
        url = 'https://dify-test.91jzx.cn/v1/files/upload'
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        # 构建表单数据
        data = {
            'user': "admin"
        }
        # 准备表单数据
        files = {
            'file': (image_path, open(image_path, 'rb'), file_mime_type)
        }
        # 发送POST请求
        response = requests.post(url, headers=headers, data=data, files=files, verify=False)
        upload_file_id = response.json().get('id')
        api_url = 'https://dify-test.91jzx.cn/v1/completion-messages'
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        # 准备表单数据
        data = {
            "inputs": {"input": task},
            "response_mode": "blocking",
            "user": "admin",
            "files": [
                {
                    "type": "image",
                    "url": "",
                    "upload_file_id": f"{upload_file_id}",
                    "transfer_method": "local_file"
                }
            ]
        }
        log.info(data)
        # 发送POST请求
        response_json = requests.post(api_url, headers=headers, json=data, verify=False).json()
        return response_json.get('answer')

    def assert_by_image(self, current_image_name, reference_image_name):
        data_dir = Path(__file__).resolve().parent.parent / 'data'
        current_image_path = data_dir / 'screenShot' / current_image_name
        reference_image_path = data_dir / "referenceShot" / reference_image_name
        b64_data = self._read_image_to_base64(reference_image_path)
        reference_text = self._extract_text_from_image(reference_image_path)
        current_text = self._extract_text_from_image(current_image_path)

        reference_hash = self._compute_image_hash(reference_image_path)
        current_hash = self._compute_image_hash(current_image_path)
        result1 = True
        result2 = True
        if current_text is not None and reference_text is not None:
            if (current_text != reference_text):
                print("Image has changed.")
                result1 = False
        if current_hash is not None and reference_hash is not None:
            if (current_hash != reference_hash):
                print("Image has changed.")
                result2 = False
        try:
            self._find_element(locator=dict(name="elename", type=AppiumBy.IMAGE, value=b64_data),
                               is_need_displayed=True).is_displayed()
        except Exception as e:
            return False
        if (result1 & result2):
            log.info("Image has not changed.")
        return result1 & result2

    def _read_image_to_base64(self, file_path):
        try:
            with open(file_path, 'rb') as png_file:
                return base64.b64encode(png_file.read()).decode('UTF-8')
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def _extract_text_from_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img, lang='chi_sim')
                return text.strip().replace("\n", " ").replace(" ", "")
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _compute_image_hash(self, file_path):
        try:
            with Image.open(file_path) as img:
                return imagehash.average_hash(img)
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
