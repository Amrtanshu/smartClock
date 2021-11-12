from time import strftime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.size = (800, 480)
Window.borderless = True

class clockApp(App):

    def update_time(self, nap):
        self.root.ids.time.text = strftime('%I:%M')
        self.root.ids.ampm.text = strftime('%p')

        self.root.ids.date.text = strftime('%m/%d/%Y - %A')

    def on_start(self):
        Clock.schedule_interval(self.update_time, 0)

if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('#101216')


    LabelBase.register(
        name='Roboto',
        fn_regular= 'Resources/Roboto-Thin.ttf',
        fn_bold= 'Resources/Roboto-Medium.ttf'
    )
    clockApp().run()
