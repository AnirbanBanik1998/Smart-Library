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
import pandas

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
	pass

class DashboardScreen(Screen):
	pass

class BookDb(BoxLayout):
    book_list = ObjectProperty(None)
    column_headings = ObjectProperty(None)
    rv_data = ListProperty([])

    def __init__(self, **kwargs):
        super(BookDb, self).__init__(**kwargs)
        self.get_dataframe()

    def get_dataframe(self):
        df = pandas.read_excel("booklist.xlsx")

        # Extract and create column headings
        # for heading in df.columns:
        #     self.column_headings.add_widget(Label(text=heading))

        # Extract and create rows
        data = []
        for row in df.itertuples():
            for i in range(1, len(row)):
                data.append([row[i], row[0]])
        self.rv_data = [{'text': str(x[0]), 'Index': str(x[1]), 'selectable': True} for x in data]

    def delete_row(self, instance):
        # TODO
        print("delete_row:")
        print("Button: text={0}, index={1}".format(instance.text, instance.index))
        print(self.rv_data[instance.index])
        print("Pandas: Index={}".format(self.rv_data[instance.index]['Index']))




class LoginApp(App):

	def build(self):
		return Builder.load_file("login.kv")

if __name__ == '__main__':
	LoginApp().run()