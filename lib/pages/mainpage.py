from base.page import BasePage
from base.action import ElementActions
from base.utils import log




class mainPage(BasePage):

    name="桌面"

    def pageinto(self,action:ElementActions):
        action.start_activity(self.activity)

    def load_android(self):
        self.姓名=self.get_locator("姓名",'name','姓名')
        self.年级=self.get_locator("年级",'name','年级')
        self.错题本=self.get_locator("错题本",'id','com.jzx.client.launcher:id/tv_error_note')
        self.家庭作业辅导=self.get_locator("家庭作业辅导",'id','com.jzx.client.launcher:id/tv_question_ocr')
        self.系统更新取消=self.get_locator("取消系统更新",'id','com.jzx.client.launcher:id/cancel')
        self.系统更新确定=self.get_locator("系统更新确定",'id','com.jzx.client.launcher:id/confirm')
        self.系统更新取消_知道了=self.get_locator("系统更新取消_知道了",'id','com.jzx.client.launcher:id/btns')
        self.用户信息=self.get_locator("用户信息",'id','com.jzx.client.launcher:id/idcard')
        self.聊天=self.get_locator("聊天",'id','com.jzx.client.launcher:id/tv_hx')
        self.数学思维=self.get_locator("数学思维",'id','com.jzx.client.launcher:id/tv_mind')
        self.数学精准学=self.get_locator("数学精准学",'id','com.jzx.client.launcher:id/tv_math')
        self.其他资料=self.get_locator("其他资料",'id','com.jzx.client.launcher:id/tv_tools')
        self.新手引导=self.get_locator("新手引导",'id','com.jzx.client.launcher:id/guide')
        self.进入学习=self.get_locator("进入学习",'id','com.jzx.client.launcher:id/submit')




