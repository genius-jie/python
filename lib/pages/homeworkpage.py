from base.page import BasePage
from base.action import ElementActions
from base.utils import log




class HomeWorkPage(BasePage):

    name="家庭作业"

    def pageinto(self,action:ElementActions):
        print("进入家庭作业")
        action.start_activity(self.appPackage,self.activity)

    def load_android(self):
        self.appPackage="com.jzx.client.questionocr"
        self.activity="/.MainActivity"
        self.首页按钮=self.get_locator("家庭作业辅导",'id','com.jzx.client.launcher:id/tv_question_ocr')




