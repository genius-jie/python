from base.page import BasePage
from base.action import ElementActions
from base.utils import log




class UserInfoPage(BasePage):

    name="用户信息"

    def pageinto(self,action:ElementActions):
        print("进入用户信息")
        action.start_activity(self.appPackage,self.activity)

    def load_android(self):
        self.appPackage="com.jzx.client.launcher"
        self.activity="/.ui.SubUserInfoActivity"
        self.用户信息按钮=self.get_locator("用户信息按钮",'id','com.jzx.client.launcher:id/idcard')
        self.我的信息=self.get_locator("我的信息",'id','com.jzx.client.launcher:id/my_info')
        self.我的护眼=self.get_locator("我的护眼",'id','com.jzx.client.launcher:id/my_protect')
        self.关于我们=self.get_locator("关于我们",'id','com.jzx.client.launcher:id/my_device')
        self.护眼数据=self.get_locator("护眼数据",'id','com.jzx.client.launcher:id/rb_eyes_data')
        self.护眼设置=self.get_locator("护眼设置",'id','com.jzx.client.launcher:id/rb_eyes_setting')
        self.切换用户=self.get_locator("切换用户",'name','切换用户')
        self.用户列表=self.get_locator("用户列表",'class name','android.widget.RelativeLayout')
        self.点击切换=self.get_locator("点击切换",'id','com.jzx.client.launcher:id/switch_btn')
        # self.切换用户=self.get_locator("切换用户",'name','切换用户')
        # self.切换用户=self.get_locator("切换用户",'name','切换用户')







