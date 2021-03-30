from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView

from datetime import timedelta,datetime
from kivy.clock import Clock
import time

from pymongo import MongoClient
Builder.load_file('_home/home.kv')


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True) 


class SelectableLabel(RecycleDataViewBehavior, BoxLayout):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		self.ids['_hashtag'].text = str(1+index)
		self.ids['_articulo'].text = data['name'].capitalize()
		self.ids['_cantidad'].text = str(data['qty'])
		if data['type']=='/kg':
			self.ids['_precio_por_articulo'].text = str("{:.2f}".format(data['prices_per_item']))+data['type']
		else:
			self.ids['_precio_por_articulo'].text = str("{:.2f}".format(data['prices_per_item']))
		self.ids['_precio'].text = str("{:.2f}".format(data['price']))
		return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

	def on_touch_down(self, touch):
		if super(SelectableLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		if is_selected:
			rv.data[index]['selected']=True
		else:
			rv.data[index]['selected']=False


class SelectableByNameLabel(RecycleDataViewBehavior, BoxLayout):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		if data['code']:
			self.ids['_codigo'].text = data['code']
		else:
			self.ids['_codigo'].text = 'Sin Código'
		self.ids['_articulo'].text = data['name'].capitalize()
		if data['qty'] or data['qty']==0:
			self.ids['_cantidad'].text = str(data['qty'])
		else:
			self.ids['_cantidad'].text = 'Sin Cantidad'
		self.ids['_precio'].text = str("{:.2f}".format(data['price']))
		return super(SelectableByNameLabel, self).refresh_view_attrs(
            rv, index, data)

	def on_touch_down(self, touch):
		if super(SelectableByNameLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		if is_selected:
			rv.data[index]['selected']=True
		else:
			rv.data[index]['selected']=False


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []

    def add_item(self,item):
    	print("RV function")
    	print(item['name'])
    	item['selected']=False
    	target = -1
    	if self.data:
    		for i in range(len(self.data)):
    			if item['name']==self.data[i]['name']:
    				target=i
    		if target>=0:
    			if item['qty']:
    				self.data[target]['qty']+=item['qty']
    			else:
	    			self.data[target]['qty']+=1
    			self.data[target]['price']=self.data[target]['prices_per_item']*self.data[target]['qty']
    			self.refresh_from_data()
    		else:
    			self.data.append(item)
    	else:
    		self.data.append(item)

    def remove_item(self):
    	target=self.item_selected()
    	price=0
    	if target>=0:
    		self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
    		price = self.data[target]['price']
    		self.data.pop(target)
    		self.refresh_from_data()
    	
    	return price

    def modify_item_popup(self,_callback):
    	target=self.item_selected()
    	if target>=0:
    		popup = ChangeQuantityPopup(_callback)
    		popup.pass_item(self.data[target])
    		popup.extra_callback(self.update_item)
    		popup.open()

    def update_item(self,value):
    	target=self.item_selected()
    	if target>=0:
    		self.data[target]['qty']=value
    		self.data[target]['price']=self.data[target]['prices_per_item']*value
    		if value==0:
    			self.data.pop(target)
    		self.refresh_from_data()

    def total(self):
    	total=0
    	for i in range(len(self.data)):
    		total+=self.data[i]['price']
    	return total

    def clear(self):
    	self.data=[]
    	self.refresh_from_data()

    def item_selected(self):
    	target=-1
    	price = 0
    	for i in range(len(self.data)):
    		if self.data[i]['selected']:
    			target=i
    	return target


class ChangeQuantityPopup(Popup):
	def __init__(self, success_callback, **kwargs):
		self.changed_qty = -1
		self.item = None
		self._succ_cb = success_callback
		self._succ_cb2 = None
		self._fail_cb = kwargs.pop('fail_callback', None)
		super(ChangeQuantityPopup, self).__init__(**kwargs)

	def validate_text_input(self, input_value):
		if self.item['type']=='/item':
			try:
				self.changed_qty=int(input_value)
				self.ids.not_valid_notification.text = ''
			except:
				self.ids.not_valid_notification.text = 'Numero No Valido'
		else:
			try:
				self.changed_qty=float(input_value)
				self.ids.not_valid_notification.text = ''
			except:
				self.ids.not_valid_notification.text = 'Numero No Valido'
		if self.ids.not_valid_notification.text=='':
			self.dismiss()
			if callable(self._succ_cb2):
				self._succ_cb2(self.changed_qty)
			if callable(self._succ_cb):
				self._succ_cb()

	def extra_callback(self,extra_cb):
		self._succ_cb2=extra_cb

	def pass_item(self, data):
		self.item = data
		self.ids.new_qty_info_1.text = "Producto: "+data['name'].capitalize()
		self.ids.new_qty_info_2.text = "Cantidad: "+str(data['qty'])


class ProductInfoPopup(Popup):
	def __init__(self, _check, **kwargs):
		super(ProductInfoPopup, self).__init__(**kwargs)
		client = MongoClient()
		self.db = client.miscelanea
		self.products = self.db.products
		self.check=_check

	def item_lookup_code(self):
		input_code = self.ids.by_code.text
		self.ids.by_code.text=''

		target_code = self.products.find_one({'code': input_code})
		if not target_code == None:
			self.ids.notify.text=''
			self.ids.name.text=target_code['name'].capitalize()
			self.ids.code.text=target_code['code']
			self.ids.price.text="{:.2f}".format(target_code['price'])
			self.ids.qty.text=str(target_code['qty'])
		else:
			self.ids.notify.text = 'No se encontró producto'
			self.ids.name.text=''
			self.ids.code.text=''
			self.ids.price.text=''
			self.ids.qty.text=''

	def add_info(self,info):
		self.ids.notify.text=''
		self.ids.name.text=info['name'].capitalize()
		if info['code']:
			self.ids.code.text=info['code']
		else:
			self.ids.code.text='N/A'
		self.ids.price.text="{:.2f}".format(info['price'])
		if info['quantity']:
			self.ids.qty.text=str(info['quantity'])
		else:
			self.ids.qty.text='N/A'

	def item_lookup_name(self):
		input_name = self.ids.by_name.text
		self.ids.by_name.text=''
		popup=ProductByNamePopup(input_name, self.add_info, self.check)
		popup.show_items()


class ProductByNamePopup(Popup):
	def __init__(self, input_name, _callback, _check, **kwargs):
		super(ProductByNamePopup, self).__init__(**kwargs)
		self.input_name=input_name
		self._callback=_callback
		client = MongoClient()
		self.db = client.miscelanea
		self.products = self.db.products
		self.check=_check

	def show_items(self):
		self.input_name=self.input_name.lower()
		if self.check:
			self.ids.qty_input.disabled=True
			self.ids.qty_input.opacity=0
		self.open()
		for name in self.products.find():
			if name['name'].lower().find(self.input_name)>=0:
				name['prices_per_item']=name['price']
				self.ids.rvs.add_item(name)

	def select_item(self):
		target=self.ids.rvs.item_selected()
		if target>=0:
			self.ids.notification.text=''
			_item = self.products.find_one({'_id': self.ids.rvs.data[target]['_id']})
			item={}
			item['name']=_item['name']
			item['code']=_item['code']
			item['prices_per_item']=_item['price']
			item['price']=_item['price']
			item['qty']=1
			item['quantity']=_item['qty']
			item['type']=_item['type']
			if self.ids.qty_input.text or self.ids.qty_input.text=='0':
				if item['type']=='/kg':
					try:
						qty=float(self.ids.qty_input.text)
						item['price']=item['prices_per_item']*qty
						item['qty']=qty
					except:
						self.ids.notification.text='Cantidad no valida'
				else:
					try:
						qty=int(self.ids.qty_input.text)
						item['price']=item['prices_per_item']*qty
						item['qty']=qty
					except:
						self.ids.notification.text='Cantidad no valida'
			if not self.ids.notification.text=='Cantidad no valida':
				if callable(self._callback):
					self._callback(item)
				self.ids.notification.text=''
				self.dismiss()
		else:
			self.ids.notification.text='No hay producto seleccionado'


class CancelPurchasePopup(Popup):
	def __init__(self, _callback, **kwargs):
		self._succ_cb = _callback
		super(CancelPurchasePopup, self).__init__(**kwargs)

	def accept(self):
		if callable(self._succ_cb):
			self._succ_cb(True)
			self.dismiss()


class SignoutPopup(Popup):
	def __init__(self, _callback, **kwargs):
		self._succ_cb = _callback
		super(SignoutPopup, self).__init__(**kwargs)

	def accept(self):
		if callable(self._succ_cb):
			self._succ_cb(True)
		self.dismiss()

class PayPopup(Popup):
	def __init__(self, total, _callback=None, **kwargs):
		self._succ_cb = _callback
		self.total = total.replace('$', '').strip()
		super(PayPopup, self).__init__(**kwargs)
		self.ids.total.text=self.total

	def show_change(self):
		received = self.ids.received.text
		try:
			change = float(received)-float(self.total)
			if change>=0:
				self.ids.change.text = "{:.2f}".format(change)
				self.ids.pay_button.disabled = False
			else:
				self.ids.change.text = "Pago menor a cantidad a pagar"
		except:
			self.ids.change.text = "Pago no valido"

	def accept_pay(self):
		self.dismiss()
		if callable(self._succ_cb):
			self._succ_cb()


class HomeWindow(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		client = MongoClient()
		self.db = client.miscelanea
		self.products = self.db.products
		self.signed_in_user=''

		self.total = 0.00
		self.rows_products = 0
		self.just_purchased = False
		self.in_sale=False
		self.global_sale_callback=None
		self.update_products=None
		self.update_sales=None
		self.sale_start =''

		self.signout_callback=None

		self.now = datetime.now()
		date = str(self.now.day)+"/"+str(self.now.month)+"/"+str(self.now.year)
		self.ids.date.text = date
		Clock.schedule_interval(self.update_clock,1)
		self.ids.time.text = self.now.strftime('%H:%M:%S')

	def add_product_by_code(self):
		input_code = self.ids.by_code.text

		target_code = self.products.find_one({'code': input_code})
		if not target_code == None:
			self.ids.by_code.text=''
			item={}
			item['name']=target_code['name']
			item['code']=target_code['code']
			item['prices_per_item']=target_code['price']
			item['price']=target_code['price']
			item['qty']=1
			item['type']=target_code['type']

			self.add_product(item)


	def add_product_by_name(self):
		input_name=self.ids.by_name.text
		self.ids.by_name.text=''
		popup=ProductByNamePopup(input_name, self.add_product, False)
		popup.show_items()

	def add_product(self, item):
		self.total+=item['price']
		self.ids.mod_subtotal.text = '$ '+"{:.2f}".format(self.total)
		self.ids.rvs.add_item(item)

	def remove_product(self):
		minus_price = self.ids.rvs.remove_item()

		self.total-=minus_price
		self.ids.mod_subtotal.text = '$ '+"{:.2f}".format(self.total)

	def update_qty(self):
		self.total=self.ids.rvs.total()
		self.ids.mod_subtotal.text = '$ '+"{:.2f}".format(self.total)

	def change_item_quantity(self, _callback=None):
		self.ids.rvs.modify_item_popup(_callback)  

	def finalize_purchase(self):
		date = datetime.now()
		self.ids.purchase_failure.text=''
		self.ids.purchase_success.text='Compra Finalizada Exitosamente'
		self.in_sale=False
		self.global_sale_callback(False)
		self.ids.finalize_purchase.disabled=True
		self.ids.new_purchase.disabled=False
		self.ids.by_code.disabled=True
		self.ids.by_name.disabled=True
		product_list = []
		for item in self.ids.rvs.data:
			product_list.append(item)
			target_item = self.products.find_one({'code': item['code']})
			if target_item:
				if target_item['qty']:
					if int(item['qty'])>target_item['qty']:
						target_item['qty']=0
					else:
						target_item['qty']-=int(item['qty'])
					query = {"code":target_item['code']}
					update = {'$set':target_item}
					self.products.update_one(query,update)
		self.update_products()
		self.ids.rvs.clear()
		sale = {'product_list': product_list, 'n_products': len(product_list), 'total': self.total, 'user': self.signed_in_user, 'sale_start': self.sale_start, 'sale_end': date}
		self.db.sales.insert(sale)
		self.update_sales()

	def new_purchase(self):
		date = datetime.now()
		self.sale_start=date
		self.ids.purchase_failure.text=''
		self.ids.purchase_success.text=''
		self.in_sale=True
		self.global_sale_callback(True)
		self.ids.pay.disabled=False
		self.ids.cancel_purchase.disabled=False
		self.ids.new_purchase.disabled=True
		self.ids.by_code.disabled=False
		self.ids.by_name.disabled=False
		self.total=0.00
		self.ids.mod_subtotal.text = '0.00'

	def cancel_purchase(self, from_popup):
		self.sale_start=''
		if from_popup:
			self.reset_after_cancel()
			self.ids.rvs.clear()
		else:
			if len(self.ids.rvs.data):
				popup = CancelPurchasePopup(self.cancel_purchase, pos_hint={'right':1, 'bottom':0})
				popup.open()
			else:
				self.reset_after_cancel()
				
	def reset_after_cancel(self):
		self.in_sale=False
		self.global_sale_callback(False)
		self.total=0.00
		self.ids.mod_subtotal.text = '0.00'
		self.ids.mod_total.text = '0.00'
		self.ids.purchase_success.text=''
		self.ids.purchase_failure.text=''
		self.ids.pay.disabled=True
		self.ids.finalize_purchase.disabled=True
		self.ids.cancel_purchase.disabled=True
		self.ids.new_purchase.disabled=False
		self.ids.by_code.disabled=True
		self.ids.by_name.disabled=True
		
	def product_info(self):
		popup=ProductInfoPopup(True)
		popup.open()

	def pay(self):
		if len(self.ids.rvs.data):
			popup=PayPopup(self.ids.mod_subtotal.text, self.payed)
			popup.open()
			self.ids.purchase_failure.text=''
		else:
			self.ids.purchase_failure.text='No hay nada que pagar'

	def payed(self):
		self.ids.finalize_purchase.disabled=False
		self.ids.pay.disabled=True
		self.ids.cancel_purchase.disabled=True

	def update_clock(self,*args):
		self.now=self.now+timedelta(seconds=1)
		self.ids.time.text =self.now.strftime('%H:%M:%S')

	def signout(self, choice=False):
		if not choice:
			if self.in_sale:
				self.ids.purchase_failure.text='Compra abierta'
			else:
				self.ids.purchase_failure.text=''
				popup=SignoutPopup(self.signout, pos_hint={'right': 1, 'top': 1})
				popup.open()
		else:
			self.parent.parent.current = 'scrn_si'
			self.signout_callback()

	def to_admin(self):
		self.parent.parent.current = 'scrn_admin'

	def show_user(self,user, _callback):
		self.signout_callback=_callback
		self.signed_in_user=user
		self.ids.show_user.text="Bienvenido, "+self.signed_in_user['name'].title()
		if self.signed_in_user['type']=='admin':
			self.ids.to_admin.disabled=False
			self.ids.to_admin.text='Admin'
			self.ids.to_admin.opacity=1
		else:
			self.ids.to_admin.disabled=True
			self.ids.to_admin.text=''
			self.ids.to_admin.opacity=0

	def pass_shop_status_callback(self, _callback1, _callback2, _callback3):
		self.global_sale_callback=_callback1
		self.update_products=_callback2
		self.update_sales=_callback3


class TestApp(App):
	def build(self):
		return HomeWindow()


if __name__=="__main__":
    TestApp().run() 