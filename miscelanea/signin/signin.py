from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from pymongo import MongoClient

Builder.load_file('signin/signin.kv')

class SigninWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test=0
        self.signed_user_callback=None

    def pass_callback(self, _callback):
        self.signed_user_callback=_callback

    def verify_user(self, username, password):
        client = MongoClient()
        db = client.miscelanea

        user = db.users.find_one({'username':username})
        if username=='' or password=='':
            self.ids.signin_notification.text='Falta nombre de usuario y/o contraseña'
        else:
            if user:
                if user['password']==password:
                    self.ids.signin_notification.text=''
                    if user['type']=='admin':
                        self.parent.parent.current = 'scrn_admin'
                    else:
                        self.parent.parent.current = 'scrn_home'
                    if callable(self.signed_user_callback):
                        self.signed_user_callback(user)
                    self.ids.username.text=''
                    self.ids.password.text=''
                else:
                    self.ids.signin_notification.text='Usuario o Contraseña incorrecta'
            else:
                self.ids.signin_notification.text='Usuario o Contraseña incorrecta'


class SigninApp(App):
    def build(self):
        return SigninWindow()

if __name__=="__main__":
    sa = SigninApp()
    sa.run()