from time import strftime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup


from datetime import datetime, timedelta
from core import calendar
import pickle


Window.size = (720, 480)
Window.borderless = True
Window.fullscreen = True
Window.show_cursor = False

c1 = calendar()
sch = c1.getEvents(strftime('%Y-%m-%d'))

class mainScreen(Screen):
    def update_time(self, nap):
        time = datetime.now()

        curr_event = c1.getCurrentEvent(time)
        next_event = c1.getNextEvent(curr_event[0])

        self.ids.time.text = strftime('%I:%M')
        self.ids.ampm.text = strftime('%p')

        self.ids.date.text = strftime('%d/%m/%Y - %A')

        if (len(curr_event)>0):
            self.ids.ongoingEvent.text = curr_event[0].title
            self.ids.ongoingTime.text = curr_event[0].start.strftime('%I:%M') + " - " + curr_event[0].end.strftime('%I:%M')
        
        if (len(next_event)>0):
            self.ids.nextEvent.text = next_event[0].title
            self.ids.nextTime.text = next_event[0].start.strftime('%I:%M') + " - " + next_event[0].end.strftime('%I:%M')


    def on_pre_enter(self):
        Clock.schedule_once(self.update_time)
        Clock.schedule_interval(self.update_time, 1)




class menuScreen(Screen):
    pass



class pomodoroScreen(Screen):

    start_time = datetime.now()
    end_time = datetime.now()
    remaining_time = timedelta(minutes = 1)
    pomo_count = 0

    status = 1 
    status_name = ['Ready','Pomo','Paused','Break']

    # status 1 = idle, 2 = pomo, 3 = pomopause, 4 = break

    def update_pomo(self,nap):

        self.ids.pomoCount.text = self.status_name[self.status-1] + ' || Count - '+ str(self.pomo_count)


        if self.status == 4:
            timeleft = self.end_time - datetime.now()
            if timeleft.seconds <=0:
                self.pomo_count = self.pomo_count + 1
                self.button2_press()

            else:
                self.ids.pomoTime.text = (str(timeleft).split('.')[0])

        if self.status == 2:
            timeleft = self.end_time - datetime.now()

            if timeleft.seconds <=0:
                self.pomo_count = self.pomo_count + 1
                self.button3_press()
            else:
                self.ids.pomoTime.text = (str(timeleft).split('.')[0])


    def button1_press(self):
        if self.status == 1: #start
            self.end_time = datetime.now()+timedelta(minutes = self.pomo_time)
            self.status = 2
            self.ids.pomobutton1.text = 'Pause'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Break'


        elif self.status == 2: #pause
            self.remaining_time = self.end_time - datetime.now()
            self.status = 3
            self.ids.pomobutton1.text = 'Resume'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Break'

        elif self.status == 3: #resume
            self.end_time = datetime.now()+self.remaining_time
            self.status = 2
            self.ids.pomobutton1.text = 'Pause'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Break'

        elif self.status == 4: #stop
            self.remaining_time = timedelta(minutes = self.pomo_time)
            self.status = 1
            self.ids.pomobutton1.text = 'Start'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Settings'
            self.ids.pomoTime.text = (str(timedelta(minutes = self.pomo_time)).split('.')[0])


    def button2_press(self):

        if self.status == 1: #reset
            self.pomo_count = 0


        elif self.status == 2 or self.status == 3: #reset
            self.end_time = datetime.now()+timedelta(minutes = self.pomo_time)
            self.status = 2
            self.ids.pomobutton1.text = 'Pause'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Break'


        elif self.status == 4: #skip break
            self.end_time = datetime.now()+timedelta(minutes = self.pomo_time)
            self.status = 2
            self.ids.pomobutton1.text = 'Pause'
            self.ids.pomobutton2.text = 'Reset'
            self.ids.pomobutton3.text = 'Break'


    def button3_press(self):

        if self.status == 1: #configure
            self.parent.current = 'config'

        elif self.status == 2 or self.status == 3: #break
            self.end_time = datetime.now()+timedelta(minutes = self.break_time)
            self.start_time = datetime.now()
            self.status = 4
            self.ids.pomobutton1.text = 'Stop'
            self.ids.pomobutton2.text = 'Skip'
            self.ids.pomobutton3.text = 'Extend'


        elif self.status == 4: #extend break
            self.end_time = self.end_time+timedelta(minutes = self.long_break)
            self.ids.pomobutton1.text = 'Stop'
            self.ids.pomobutton2.text = 'Skip'
            self.ids.pomobutton3.text = 'Extend'


    def on_pre_enter(self):

        with open('settings.txt', 'rb') as f:
            settings = pickle.load(f)
            self.pomo_time = settings['pomo_time']
            self.break_time = settings['break_time']
            self.long_break = settings['long_break']

        self.status = 4
        self.button1_press()
        Clock.schedule_interval(self.update_pomo, .5)



class calendarScreen(Screen):
    pass


class taskScreen(Screen):
    pass

class configScreen(Screen):
    def configure_pomo(self):

        settings = {'pomo_time':int(self.ids.confdur.text),'break_time':int(self.ids.confbreak.text),'long_break':int(self.ids.conflbreak.text)}

        file = open('settings.txt', 'wb')
        pickle.dump(settings, file)
        file.close()
        self.parent.current = 'pomo'


    def on_pre_enter(self):
        with open('settings.txt', 'rb') as f:
            settings = pickle.load(f)
            self.ids.sliderdur.value = settings['pomo_time']
            self.ids.sliderbreak.value = settings['break_time']
            self.ids.sliderlbreak.value = settings['long_break']





class clockApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(mainScreen(name='home'))
        sm.add_widget(menuScreen(name='menu'))

        sm.add_widget(pomodoroScreen(name='pomo'))
        sm.add_widget(calendarScreen(name='calendar'))
        sm.add_widget(taskScreen(name='tasks'))   
        sm.add_widget(configScreen(name='config'))
        return sm



if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('#101216')


    LabelBase.register(
        name='Roboto',
        fn_regular= 'Resources/Roboto-Thin.ttf',
        fn_bold= 'Resources/Roboto-Medium.ttf'
    )
    clockApp().run()
