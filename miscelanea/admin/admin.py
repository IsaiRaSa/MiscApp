from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import datetime
import time
import csv
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from pymongo import MongoClient

Builder.load_file('admin/admin.kv')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True) 


class SelectableItemLabel(RecycleDataViewBehavior, BoxLayout):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		if not data['code']==None:
			self.ids['_codigo'].text = data['code']
		else:
			self.ids['_codigo'].text = 'Sin Código'
		self.ids['_articulo'].text = data['name'].capitalize()
		if not data['qty']==None:
			self.ids['_cantidad'].text = str(data['qty'])
		else:
			self.ids['_cantidad'].text = 'Sin cantidad'
		if data['type']:
			if data['type']=='/item':
				type_of='/artículo'
			else:
				type_of = data['type']
		else:
			type_of = ''
		self.ids['_precio'].text = str("{:.2f}".format(data['price']))+" "+type_of
		return super(SelectableItemLabel, self).refresh_view_attrs(
            rv, index, data)

	def on_touch_down(self, touch):
		if super(SelectableItemLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		if is_selected:
			rv.data[index]['selected']=True
		else:
			rv.data[index]['selected']=False

class SelectableUserLabel(RecycleDataViewBehavior, BoxLayout):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		self.ids['_name'].text = data['name'].title()
		self.ids['_username'].text = data['username']
		self.ids['_type'].text = str(data['type'])
		return super(SelectableUserLabel, self).refresh_view_attrs(
            rv, index, data)

	def on_touch_down(self, touch):
		if super(SelectableUserLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		if is_selected:
			rv.data[index]['selected']=True
		else:
			rv.data[index]['selected']=False

class SelectableSaleLabel(RecycleDataViewBehavior, BoxLayout):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		self.ids['_name'].text = data['user']['name'].title()
		self.ids['_username'].text = data['user']['username']
		self.ids['_cantidad'].text = str(data['n_products'])
		self.ids['_total'].text = '$ '+str("{:.2f}".format(data['total']))
		self.ids['_time'].text = str(data['sale_start'].strftime("%H:%M:%S"))+"-"+str(data['sale_end'].strftime("%H:%M:%S"))
		self.ids['_date'].text = str(data['sale_start'].strftime("%d/%m/%Y"))
		return super(SelectableSaleLabel, self).refresh_view_attrs(
            rv, index, data)

	def on_touch_down(self, touch):
		if super(SelectableSaleLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		if is_selected:
			rv.data[index]['selected']=True
		else:
			rv.data[index]['selected']=False

class SaleItemsLabel(RecycleDataViewBehavior, BoxLayout):
	index = None

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		if not data['code']==None:
			self.ids['_codigo'].text = data['code']
		else:
			self.ids['_codigo'].text = 'Sin Código'
		self.ids['_articulo'].text = data['name'].capitalize()
		if not data['qty']==None:
			self.ids['_cantidad'].text = str(data['qty'])
		else:
			self.ids['_cantidad'].text = 'Sin cantidad'
		if data['type']:
			if data['type']=='/item':
				type_of='/artículo'
			else:
				type_of = data['type']
		else:
			type_of = ''
		self.ids['_precio_por_articulo'].text = str("{:.2f}".format(data['prices_per_item']))+" "+type_of
		self.ids['_total'].text= str("{:.2f}".format(data['price']))
		return super(SaleItemsLabel, self).refresh_view_attrs(
            rv, index, data)

class SigninsLabel(RecycleDataViewBehavior, BoxLayout):
	index = None

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		self.ids['_name'].text=data['name']
		self.ids['_username'].text=data['username']
		try:
			self.ids['_sign_in'].text=data['sign_in'].strftime("%H:%M:%S")
		except:
			self.ids['_sign_in'].text='N/A'
		try:
			self.ids['_sign_out'].text=data['sign_out'].strftime("%H:%M:%S")
		except:
			self.ids['_sign_out'].text='N/A'
		try:
			self.ids['_date'].text=data['sign_in'].strftime("%d/%m/%y")
		except:
			self.ids['_date'].text='N/A'
		return super(SigninsLabel, self).refresh_view_attrs(
            rv, index, data)

class AdminRV(RecycleView):
    def __init__(self, **kwargs):
        super(AdminRV, self).__init__(**kwargs)
        self.data = []
        self.ascending_descending=True

    def item_selected(self):
    	target=-1
    	price=0
    	for i in range(len(self.data)):
    		if self.data[i]['selected']:
    			target=i

    	return target

    def order_by(self, order):
    	newlist=[]
    	nonelist=[]
    	if self.data:
    		print("HERE", self.data[0][order])
    		if self.ascending_descending:
    			for dato in self.data:
    				if dato[order]:
    					newlist.append(dato)
    				else:
    					nonelist.append(dato)
    			if nonelist:
    				newlist = sorted(newlist, key=lambda k: k[order])
    				newlist.extend(nonelist)
    			else:
    				newlist=[]
	    			newlist = sorted(self.data, key=lambda k: k[order]) 
    			self.data=[]
    			self.data=newlist
    			self.ascending_descending=False
    		else:
    			for dato in self.data:
    				print("DATA:", dato)
    				if dato[order]:
    					newlist.append(dato)
    				else:
    					nonelist.append(dato)
    			if nonelist:
    				newlist = sorted(newlist, key=lambda k: k[order], reverse=True)
    				nonelist.extend(newlist)
    				newlist=[]
    				newlist=nonelist
    			else:
    				newlist=[]
	    			newlist = sorted(self.data, key=lambda k: k[order], reverse=True)
    			self.data=[]
    			self.data=newlist
    			self.ascending_descending=True

    def add_data(self,items):
    	if not self.data:
	    	for item in items:
		    	item['selected']=False
	    		self.data.append(item)
		    	self.refresh_from_data()


class CustomDropDown(DropDown):
	def __init__(self, **kwargs):
		self._succ_cb = None
		super(CustomDropDown, self).__init__(**kwargs)

	def screen_chosen(self, screen):
		if callable(self._succ_cb):
			self._succ_cb(screen)

	def receive_callback(self,_callback):
		self._succ_cb = _callback


class ItemPopup(Popup):
	def __init__(self, _callback, **kwargs):
		self._succ_cb = _callback
		self._fail_cb = kwargs.pop('fail_callback', None)
		super(ItemPopup, self).__init__(**kwargs)
		self.my_observer = Observer()

	def popup_scan(self):
		source_path = Path(__file__).resolve()
		source_dir = str(source_path.parent)+"\\scans\\"
		patterns = "*"
		ignore_patterns = ""
		ignore_directories = False
		case_sensitive = True
		my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
		my_event_handler.on_created = self.on_created
		my_event_handler.on_deleted = self.on_deleted
		my_event_handler.on_modified = self.on_modified
		my_event_handler.on_moved = self.on_moved
		go_recursively = True
		self.my_observer = Observer()
		self.my_observer.schedule(my_event_handler, source_dir, recursive=go_recursively)
		self.my_observer.start()
		try:
			self.open()
		except KeyboardInterrupt:
			self.my_observer.stop()
			self.my_observer.join()


	def popup_setup(self, option,item_data):
		self.ids.code_toggle.disabled=True
		if option=='add':
			self.ids.item_info_1.text='Agregar Producto Nuevo'
		else:
			self.ids.item_info_1.text='Modificar Producto'
			self.ids.item_info_2.text=item_data['name'].title()
			if item_data['code']:
				self.ids.item_code.text=item_data['code']
			else:
				self.ids.item_code.text='Sin código'
				self.ids.code_toggle.state='normal'
				self.ids.code_toggle.text='Código no necesario'
			self.ids.item_name.text=item_data['name'].title()
			self.ids.item_price.text=str(item_data['price'])
			if item_data['type']=='/kg':
				self.ids.weight_toggle.state='down'
				self.ids.choice_label.text='Cantidad en kilos'
			else:
				self.ids.item_toggle.state='down'
				self.ids.choice_label.text='Cantidad de artículos'
			if item_data['qty'] or item_data['qty']==0:
				self.ids.item_qty.text=str(item_data['qty'])
			else:
				self.ids.item_qty.text='Sin cantidad'

	def verify_item(self, code,code_state, name, price, qty, qty_status1, qty_status2):
		print("Code: ",code,"\nName:",name,"\nPrice:",price,"\nqty:",qty,"\nQty type:",qty_status1, "\nQty type:",qty_status2)
		alert1 = 'Falta: '
		alert2 = ''
		validated = {}
		if code_state=='down':
			if not code:
				alert1+='Código. '
				validated['code']=False
			else:
				try:
					numeric = int(code)
					validated['code']=code
				except:
					alert2+='Código no válido. '
					validated['code']=False
		else:
			validated['code']=None

		if not name:
			alert1+='Nombre. '
			validated['name']=False
		else:
			validated['name']=name.lower()

		if not price:
			alert1+='Precio. '
			validated['price']=False
		else:
			try:
				validated['price']=float(price)
			except:
				alert2+='Precio no válido. '
				validated['price']=False

		if qty_status1=='normal' and qty_status2=='normal':
			alert1+='Tipo de cantidad. '
			validated['type']=False
		else:
			if qty_status1=='down':
				validated['type']='/kg'
				if qty or qty in ['0', '0.0']:
					try:
						validated['qty']=float(qty)
					except:
						alert2+='Cantidad no válida. '
						validated['qty']=False
				else:
					validated['qty']=None
			else:
				validated['type']='/item'
				if qty or qty=='0':
					try:
						validated['qty']=int(qty)
					except:
						alert2+='Cantidad no válida. '
						validated['qty']=False
				else:
					alert1+='Cantidad. '
					validated['qty']=False

		values = list(validated.values())
		for i in range(len(values)):
			if validated['type']=='/item' and values[i] is 0:
				values[i]=True
			if validated['type']=='/kg' and values[i]==0.0:
				values[i]=True

		if False in values:
			self.ids.not_valid_notification.text=alert1+alert2
		else:
			self.ids.not_valid_notification.text=''
			self._succ_cb(validated)
			self.dismiss()

	def add_code(self,code):
		self.ids.item_code.text=''
		self.ids.item_code.text=code

	def on_created(self,event):
	    print(f"{event.src_path} has been created")

	def on_deleted(self,event):
	    print(f"{event.src_path} deleted")

	def on_modified(self,event):
	    print(f"{event.src_path} has been modified")
	    with open(str(event.src_path)) as csv_file:
		    csv_reader = csv.reader(csv_file)
		    for code in csv_reader:
	    		print("Code:", code[0],"\nType:",type(code[0]))
	    		self.add_code(code[0])

	def on_moved(self,event):
	    print(f"{event.src_path} moved to {event.dest_path}")


class DeleteItemPopup(Popup):
	def __init__(self, success_callback, **kwargs):
		self._succ_cb = success_callback
		self._fail_cb = kwargs.pop('fail_callback', None)
		super(DeleteItemPopup, self).__init__(**kwargs)

	def popup_setup(self, item_data):
		if item_data['code']:
			self.ids.code_delete_label.text=item_data['code']
		else:
			self.ids.code_delete_label.text='Sin código'
		self.ids.name_delete_label.text=item_data['name']
		self.ids.price_delete_label.text=str(item_data['price'])
		if item_data['qty']:
			self.ids.qty_delete_label.text=str(item_data['qty'])
		else:
			self.ids.qty_delete_label.text='Sin cantidad'

	def accept_delete(self):
		self._succ_cb()
		self.dismiss()

class DeleteUserPopup(Popup):
	def __init__(self, success_callback, **kwargs):
		self._succ_cb = success_callback
		self._fail_cb = kwargs.pop('fail_callback', None)
		super(DeleteUserPopup, self).__init__(**kwargs)

	def popup_setup(self, item_data):
		self.ids.name_delete_label.text=item_data['name']
		self.ids.username_delete_label.text=item_data['username']
		self.ids.type_delete_label.text=str(item_data['type'])

	def accept_delete(self):
		self._succ_cb()
		self.dismiss()

class UserPopup(Popup):
	def __init__(self, _callback, **kwargs):
		self._succ_cb = _callback
		self._fail_cb = kwargs.pop('fail_callback', None)
		super(UserPopup, self).__init__(**kwargs)
		self.saved_username=None

	def popup_setup(self, option,item_data):
		if option=='add':
			self.ids.user_info_1.text='Agregar Usuario Nuevo'
		else:
			self.ids.user_info_1.text='Usuario Producto'
			self.ids.user_info_2.text=item_data['name']
			self.ids.user_name.text=item_data['name']
			self.saved_username=item_data['username']
			self.ids.user_username.text=item_data['username']
			if item_data['type']=='admin':
				self.ids.admin_option.state='down'
			else:
				self.ids.worker_option.state='down'
			self.ids.user_password.text=str(item_data['password'])

	def verify_user(self, name, username, password, admin_type, worker_type):
		alert1 = 'Falta: '
		alert2 = ''
		validated = {}

		client = MongoClient()
		db = client.miscelanea
		existingUsernames=[]
		usernames=db.users.find({}, {'username':1, '_id':0})
		for i in usernames:
			existingUsernames.append(i['username'])


		if not name:
			alert1+='Nombre. '
			validated['name']=False
		else:
			if name.isalpha():
				validated['name']=name.lower()
			else:
				alert2+='Nombre no válido. '
				validated['name']=False

		if not username:
			alert1+='Nombre de usuario. '
			validated['username']=False
		elif username in existingUsernames:
			if username==self.saved_username:
				validated['username']=username.lower()
			else:
				alert2+='Nombre de usuario ya existe'
				validated['username']=False
		else:
			validated['username']=username.lower()

		if not password:
			alert1+='Contraseña. '
			validated['password']=False
		else:
			validated['password']=password

		if admin_type=='normal' and worker_type=='normal':
			alert1+='Tipo. '
			validated['type']=False
		else:
			if admin_type=='down':
				validated['type']='admin'
			else:
				validated['type']='trabajador'

		values = validated.values()

		if False in values:
			self.ids.not_valid_notification.text=alert1+alert2
		else:
			self.ids.not_valid_notification.text=''
			self._succ_cb(validated)
			self.dismiss()


class SignoutPopup(Popup):
	def __init__(self, _callback=None, **kwargs):
		self._succ_cb = _callback
		super(SignoutPopup, self).__init__(**kwargs)

	def accept(self):
		if callable(self._succ_cb):
			self._succ_cb(True)
		self.dismiss()

class SigninData(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		client = MongoClient()
		db = client.miscelanea
		self.signins = db.signins
		Clock.schedule_once(self.load_signins)

	def switch_screen(self, to_screen):
		if to_screen=='Datos de Ventas':
			to_screen='Sale Data'
		else:
			to_screen='Sign in Data'
		self.parent.current = to_screen

	def load_signins(self, blank=None, choice='Default'):
		today_date=datetime.datetime.today().date()
		valid_input=True
		iDate=datetime.datetime.strptime('01/01/00','%d/%m/%y')
		lDate=datetime.datetime.strptime('31/12/2099','%d/%m/%Y')
		_signins = []
		self.ids.sign_ins_rv.data=[]
		if choice=='Default':
			for signin in self.signins.find():
				if signin['sign_in'].date()>=today_date:
					_signins.append(signin)
			self.ids.sign_ins_rv.add_data(_signins)
			self.ids.date_id.text='Hoy'
		elif choice=='Date':
			date=self.ids.single_date.text
			try:
				nDate=datetime.datetime.strptime(date,'%d/%m/%y')
			except:
				valid_input=False
			if valid_input:
				for signin in self.signins.find():
					if signin['sign_in'].date()==nDate.date():
						_signins.append(signin)
				self.ids.sign_ins_rv.add_data(_signins)
				self.ids.date_id.text=nDate.strftime("%d/%m/%y")
		else:
			if self.ids.initial_date.text:
				initial_date=self.ids.initial_date.text
				try:
					iDate=datetime.datetime.strptime(initial_date,'%d/%m/%y')
				except:
					valid_input=False
			if self.ids.last_date.text:
				last_date=self.ids.last_date.text
				try:
					lDate=datetime.datetime.strptime(last_date,'%d/%m/%y')
				except:
					valid_input=False
			
			if valid_input:
				for signin in self.signins.find():
					if iDate.date()<=signin['sign_in'].date()<=lDate.date():
						_signins.append(signin)
				self.ids.sign_ins_rv.add_data(_signins)
				self.ids.date_id.text=iDate.strftime("%d/%m/%y")+" - "+lDate.strftime("%d/%m/%y")

		self.ids.initial_date.text=''
		self.ids.last_date.text=''
		self.ids.single_date.text=''

class SaleDataItemPopup(Popup):
	def __init__(self, **kwargs):
		super(SaleDataItemPopup, self).__init__(**kwargs)

	def display_item_info(self, sale):
		self.open()
		items=sale['product_list']
		total_items=0
		total_kg=0.0
		total_money=0.0
		for item in items:
			total_money+=item['price']
			if item['type']=='/item':
				total_items+=item['qty']
			else:
				total_kg+=item['qty']
				total_items+=1
		self.ids.total_items.text=str(total_items)
		self.ids.total_kg.text=str(total_kg)
		self.ids.total_money.text='$ '+str("{:.2f}".format(total_money))
		self.ids.sale_items_rv.add_data(items)

		
class SaleData(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		client = MongoClient()
		db = client.miscelanea
		self.sales = db.sales
		Clock.schedule_once(self.load_sales)

	def switch_screen(self, to_screen):
		if to_screen=='Datos de Ventas':
			to_screen='Sale Data'
		else:
			to_screen='Sign in Data'
		self.parent.current = to_screen

	def more_info(self):
		target=self.ids.sales_rv.item_selected()
		if target>=0:
			sale = self.ids.sales_rv.data[target]
			p=SaleDataItemPopup()
			p.display_item_info(sale)

	def load_sales(self, blank=None, choice='Default'):
		today_date=datetime.datetime.today().date()
		valid_input=True
		iDate=datetime.datetime.strptime('01/01/00','%d/%m/%y')
		lDate=datetime.datetime.strptime('31/12/2099','%d/%m/%Y')
		_sales = []
		self.ids.sales_rv.data=[]
		final_sum=0
		if choice=='Default':
			for sale in self.sales.find():
				if sale['sale_start'].date()>=today_date:
					_sales.append(sale)
					final_sum+=sale['total']
			self.ids.sales_rv.add_data(_sales)
			self.ids.date_id.text="Hoy"
		elif choice=='Date':
			date=self.ids.single_date.text
			try:
				nDate=datetime.datetime.strptime(date,'%d/%m/%y')
				print("INPUT: ",nDate)
			except:
				valid_input=False
			if valid_input:
				for sale in self.sales.find():
					if sale['sale_start'].date()==nDate.date():
						_sales.append(sale)
						final_sum+=sale['total']
				self.ids.sales_rv.add_data(_sales)
				self.ids.date_id.text=nDate.strftime("%d/%m/%y")
		else:
			if self.ids.initial_date.text:
				initial_date=self.ids.initial_date.text
				try:
					iDate=datetime.datetime.strptime(initial_date,'%d/%m/%y')
				except:
					valid_input=False
			if self.ids.last_date.text:
				last_date=self.ids.last_date.text
				try:
					lDate=datetime.datetime.strptime(last_date,'%d/%m/%y')
				except:
					valid_input=False
			
			print("INPUT: ", iDate,lDate)
			if valid_input:
				for sale in self.sales.find():
					if iDate.date()<=sale['sale_start'].date()<=lDate.date():
						_sales.append(sale)
						final_sum+=sale['total']
				self.ids.sales_rv.add_data(_sales)
				self.ids.date_id.text=iDate.strftime("%d/%m/%y")+" - "+lDate.strftime("%d/%m/%y")

		self.ids.final_sum.text='$ '+str("{:.2f}".format(final_sum))
		self.ids.initial_date.text=''
		self.ids.last_date.text=''
		self.ids.single_date.text=''
		
class MoreInfoScreen(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def switch_screen(self, to_screen):
		if to_screen=='Datos de Ventas':
			to_screen='Sale Data'
		else:
			to_screen='Sign in Data'
		self.parent.current = to_screen


class ProductScreen(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		client = MongoClient()
		db = client.miscelanea
		self.items=db.products
		Clock.schedule_once(self.load_item)

	def load_item(self, blank=None):
		_items = []
		self.ids.item_rv.data=[]
		for item in self.items.find():
			_items.append(item)
		self.ids.item_rv.add_data(_items)

	def item_information(self):
		print("Item information")

	def add_item(self,validated):
		print("Passed:",validated.items())
		self.ids.item_rv.data.append(validated)
		self.ids.item_rv.refresh_from_data()
		self.items.insert(validated)

	def modify_item(self,validated):
		print("validated:",validated)
		query = {"code":validated['code']}
		update = {'$set':validated}
		self.items.update_one(query,update)

		target = self.ids.item_rv.item_selected()
		price_formated = "{:.2f}".format(validated['price'])
		self.ids.item_rv.data[target]['code']=validated['code']
		self.ids.item_rv.data[target]['name']=validated['name']
		self.ids.item_rv.data[target]['qty']=validated['qty']
		self.ids.item_rv.data[target]['price']=float(price_formated)
		self.ids.item_rv.refresh_from_data()

	def delete_item(self):
		target = self.ids.item_rv.item_selected()
		query = {"code":self.ids.item_rv.data[target]['code']}
		self.ids.item_rv._layout_manager.deselect_node(self.ids.item_rv._layout_manager._last_selected_node)
		self.ids.item_rv.data.pop(target)
		self.ids.item_rv.refresh_from_data()

		self.items.delete_one(query)

	def add_item_button(self,_callback=None):
		p = ItemPopup(_callback)
		p.popup_setup('add','')
		p.popup_scan()

	def modify_item_button(self,_callback=None):
		target = self.ids.item_rv.item_selected()
		if target>=0:
			item_data = self.ids.item_rv.data[target]
			p = ItemPopup(_callback)
			p.popup_setup('modify',item_data)
			p.open()
		
	def delete_item_button(self,_callback=None):
		target = self.ids.item_rv.item_selected()
		if target>=0:
			item_data = self.ids.item_rv.data[target]
			p = DeleteItemPopup(_callback)
			p.popup_setup(item_data)
			p.open()

	def order_by(self, order):
		self.ids.item_rv.order_by(order)

	def search_by_code(self):
		target = self.ids.search_by_code.text
		self.ids.search_by_code.text = ''
		items = []
		self.ids.item_rv.data = []
		for name in self.items.find():
			if name['code']:
				if name['code'].find(target)>=0:
					items.append(name)
		self.ids.item_rv.add_data(items)

	def search_by_name(self):
		target = self.ids.search_by_name.text.lower()
		self.ids.search_by_name.text = ''
		items = []
		self.ids.item_rv.data = []
		for name in self.items.find():
			if name['name'].lower().find(target)>=0:
				items.append(name)
		self.ids.item_rv.add_data(items)
		
	

class UserScreen(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		client = MongoClient()
		db = client.miscelanea
		self.users = db.users
		Clock.schedule_once(self.load_user)
		self.signed_in_user=''

	def load_user(self, blank):
		_users = []
		for user in self.users.find():
			_users.append(user)
		self.ids.user_rv.add_data(_users)

	def user_information(self):
		print("User information")

	def add_user(self,validated):
		print("Passed:",validated)
		self.ids.user_rv.data.append(validated)
		self.ids.user_rv.refresh_from_data()
		self.users.insert(validated)

	def modify_user(self,validated):
		print("validated:",validated)
		target = self.ids.user_rv.item_selected()
		query = {"_id":self.ids.user_rv.data[target]['_id']}
		update = {'$set':validated}
		self.users.update_one(query,update)
		print("QUERY AND UPDTADE:",query,update)

		target = self.ids.user_rv.item_selected()
		self.ids.user_rv.data[target]['name']=validated['name']
		self.ids.user_rv.data[target]['username']=validated['username']
		self.ids.user_rv.data[target]['type']=validated['type']
		self.ids.user_rv.refresh_from_data()

	def delete_user(self):
		target = self.ids.user_rv.item_selected()
		query = {"_id":self.ids.user_rv.data[target]['_id']}
		self.ids.user_rv._layout_manager.deselect_node(self.ids.user_rv._layout_manager._last_selected_node)
		self.ids.user_rv.data.pop(target)
		self.ids.user_rv.refresh_from_data()

		self.users.delete_one(query)

	def add_user_button(self,_callback=None):
		p = UserPopup(_callback)
		p.popup_setup('add','')
		p.open()

	def modify_user_button(self,_callback=None):
		target = self.ids.user_rv.item_selected()
		if target>=0:
			item_data = self.ids.user_rv.data[target]
			p = UserPopup(_callback)
			p.popup_setup('modify',item_data)
			p.open()
		
	def delete_user_button(self,_callback=None):
		target = self.ids.user_rv.item_selected()
		if target>=0:
			item_data = self.ids.user_rv.data[target]
			p = DeleteUserPopup(_callback)
			p.popup_setup(item_data)
			p.open()

	def test(self):
		print("\n\nTest:\n")


class AdminWindow(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.dropdown = CustomDropDown()
		self.screenbutton = self.ids.drop_down_button
		self.screenbutton.bind(on_release=self.dropdown.open)
		self.shop_status=False

		self.signout_callback=None
		self.sm=self.ids.scrn_mngr
		self.sm.add_widget(ProductScreen())
		self.sm.add_widget(UserScreen())
		self.sm.add_widget(MoreInfoScreen())

		self.sm.add_widget(SigninData())
		self.sm.add_widget(SaleData())

	def switch_screen(self,screen):
		self.sm.current=screen

	def send_callback(self,_callback):
		self.dropdown.receive_callback(_callback)

	def signout(self, choice=False):
		if not choice:
			if self.shop_status:
				self.ids.notification.text='Hay una compra abierta'
			else:
				pu=SignoutPopup(self.signout, pos_hint={'right': 1, 'top': 1})
				pu.open()
				self.ids.notification.text=''
		else:
			self.parent.parent.current = 'scrn_si'
			self.signout_callback()

	def to_sale(self):
		self.parent.parent.current = 'scrn_home'

	def show_user(self,user, _callback):
		self.signout_callback=_callback
		self.signed_in_user=user
		self.ids.show_user.text="Bienvenido, "+self.signed_in_user['name'].title()

	def update_status(self, status):
		self.shop_status=status

	def pass_update_function(self):
		return self.ids.product_screen.load_item

	def pass_update_sale_function(self):
		return self.ids.sale_data.load_sales


class AdminPApp(App):
	def build(self):
		return AdminWindow()


if __name__=="__main__":
    ha = AdminPApp() 
    ha.run()