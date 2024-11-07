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
        self.八年级=self.get_locator("八年级",'name','八年级')



