from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import datetime
from pymongo import MongoClient
import os, sys
from kivy.resources import resource_add_path, resource_find

from admin.admin import AdminWindow
from signin.signin import SigninWindow
from _home._home import HomeWindow


class MainWindow(BoxLayout):

    admin_widget = AdminWindow()
    signin_widget = SigninWindow()
    home_widget = HomeWindow()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        client = MongoClient()
        db = client.miscelanea
        self.signins = db.signins
        self.signed_id=''

        self.signed_in_user=''
        self.shop_status=False
        self.signin_widget.pass_callback(self.signed_user)
        self.product_update=self.admin_widget.pass_update_function()
        self.sale_update=self.admin_widget.pass_update_sale_function()
        self.home_widget.pass_shop_status_callback(self.global_shop_status, self.product_update, self.sale_update)
        self.ids.scrn_si.add_widget(self.signin_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_home.add_widget(self.home_widget)

    def global_shop_status(self, status):
        self.shop_status=status
        self.admin_widget.update_status(self.shop_status)


    def signed_user(self, user):
        self.signed_in_user=user
        date=datetime.datetime.now()
 
        self.signed_in_user.pop('_id', None)
        self.signed_in_user.pop('password', None)
        self.signed_in_user['sign_in']=date
        self.signed_in_user['sign_out']='n/a'
        self.signed_id=self.signins.insert(self.signed_in_user)

        self.admin_widget.show_user(self.signed_in_user, self.signout_user)
        self.home_widget.show_user(self.signed_in_user, self.signout_user)

    def signout_user(self):
        date=datetime.datetime.now()
        self.signed_in_user['sign_out']=date
        query = {"_id":self.signed_id}
        update = {'$set':self.signed_in_user}
        self.signins.update_one(query,update)

        self.signed_id=''
        self.signed_in_user=''

class MainApp(App):
    def build(self):
        return MainWindow()

if __name__=='__main__':
    if hasattr(sys, 'MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
    