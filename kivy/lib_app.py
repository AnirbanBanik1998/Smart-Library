from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock

import requests

token = None
url = 'http://192.168.43.164:5000'

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleGridLayout):
    # Adds selection and focus behaviour to the view.
    pass

class SelectableBook(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableBook, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBook, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

class LoginScreen(Screen):
	#Implement authorization functionality
    def authenticate(self):
        global token
        reg_no = self.ids['regno'].text
        password = self.ids['password'].text
        resp = requests.get('{}/login'.format(url), auth=(reg_no, password))
        if resp.status_code == 200:
            token = resp.json()['token']
            print(token)
            self.manager.transition.direction = 'left'
            self.manager.current = 'dashboard_screen'
            #book = BookDb()
            #book.update_data()
        else:
            self.manager.current = 'login_screen'

class DashboardScreen(Screen):
    pass
    '''
	def __init__(self, **kwargs):
	    super(DashboardScreen, self).__init__(**kwargs)
	    Clock.schedule_once(self.finish_init,0)
	
	def finish_init(self, dt):
	    global token
	    while True:
	        if token is not None:
	            break
	    return
	'''

class BookDb(BoxLayout):
    book_list = ObjectProperty(None)
    column_headings = ObjectProperty(None)
    rv_data = ListProperty([])

    def __init__(self, **kwargs):
        super(BookDb, self).__init__(**kwargs)
        print('Book db called')
        self.init_dataframe()
        
    def init_dataframe(self):
        self.rv_data = [{'text': 'Text', 'Index': '0', 'selectable': True}, 
                {'text': 'Text', 'Index': '0', 'selectable': True}, 
                {'text': 'Text', 'Index': '0', 'selectable': True}]
        

    def get_dataframe(self):
        global token
        headers = {'x-access-token': token}
        res = requests.get('{}/get_books'.format(url), headers=headers)
        if res.status_code != 200:
            return

        # Extract and create column headings
        #for heading in df.columns:
        #    self.column_headings.add_widget(Label(text=heading))
        
        book_list = res.json()['books']
        '''
        for key in book_list[0]:
            self.column_headings.add_widget(Label(text=key))
            print(key)
        '''
        # Extract and create rows
        data = []
        index = 0
        for book in book_list:
            for val in book.values():
                data.append({'text':val, 'Index':str(index), 'selectable':True})
            index += 1
        self.rv_data = data
        #print(self.rv_data)
        
    def update_data(self):
        self.get_dataframe()
        #print('\n'+str(self.ids.rvlist.data))
        self.ids.rvlist.data = self.rv_data
        #print('\n'+str(self.ids.rvlist.data))
        self.ids.rvlist.refresh_from_data()


class LoginApp(App):

	def build(self):
		return Builder.load_file("lib_app.kv")

if __name__ == '__main__':
	LoginApp().run()
