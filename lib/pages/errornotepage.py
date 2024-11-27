from base.page import BasePage
from base.action import ElementActions
from base.utils import log




class ErrorNotePage(BasePage):

    name="错题本"

    def pageinto(self,action:ElementActions):
        print("进入错题本")
        action.start_activity(self.appPackage,self.activity)

    def load_android(self):
        self.appPackage="com.jzx.client.note"
        self.activity="/.ui.MainActivity"
        self.错题本=self.get_locator("错题本",'id','com.jzx.client.launcher:id/tv_error_note')




