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
        self.用户列表数=self.get_locator("用户列表数",'class name','android.widget.RelativeLayout')
        self.用户列表框=self.get_locator("用户列表框",'id','com.jzx.client.launcher:id/studentContainer')
        self.张诺安=self.get_locator("张诺安",'name','张诺安')
        self.张森谷=self.get_locator("张诺安",'name','张森谷')
        self.张希苪=self.get_locator("张诺安",'name','张希苪')
        self.张库珀=self.get_locator("张诺安",'name','张库珀')
        self.张润吉=self.get_locator("张诺安",'name','张润吉')
        self.张永天=self.get_locator("张诺安",'name','张永天')
        self.张圈圆=self.get_locator("张诺安",'name','张圈圆')
        self.张近义=self.get_locator("张近义",'name','张近义')
        self.点击切换=self.get_locator("点击切换",'id','com.jzx.client.launcher:id/switch_btn')

        self.教材年级=self.get_locator("我的信息教材年级",'name','教材/年级')
        self.年级=self.get_locator("年级",'id','com.jzx.client.launcher:id/ll_grade')
        self.三年级=self.get_locator("三年级",'name','三年级')
        self.四年级=self.get_locator("四年级",'name','四年级')
        self.五年级=self.get_locator("五年级",'name','五年级')
        self.六年级=self.get_locator("六年级",'name','六年级')
        self.初中六年级=self.get_locator("年级",'name','年级')
        self.七年级=self.get_locator("七年级",'name','七年级')
        self.八年级=self.get_locator("八年级",'name','八年级')
        self.九年级=self.get_locator("九年级",'name','九年级')
        self.地区=self.get_locator("地区",'id','com.jzx.client.launcher:id/ll_city')
        self.地区安徽省=self.get_locator("安徽省",'name','安徽省')
        self.安徽安庆市=self.get_locator("安庆市",'name','安庆市')
        self.确定=self.get_locator("确定",'id','com.jzx.client.launcher:id/sure')
        # self.切换用户=self.get_locator("切换用户",'name','切换用户')
        # self.切换用户=self.get_locator("切换用户",'name','切换用户')







