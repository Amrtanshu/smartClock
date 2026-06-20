from time import strftime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label



from datetime import datetime, timedelta
import pytz
from core import *
from pathlib import Path
import pickle
from gpiozero import Buzzer
from time import sleep

from wakeonlan import send_magic_packet



Window.size = (800, 480)
Window.borderless = True
Window.fullscreen = True
Window.show_cursor = False

# c1 = calendar()
# sch = c1.getEvents(strftime('%Y-%m-%d'))
initialize()
calendarToday = calendar()
calendarToday.updateCurrAndNextEvents()

tasks = tasks()

buzzer = Buzzer(17)



class mainScreen(Screen):
    def update_time(self, nap):
        time = datetime.now(pytz.timezone(calendarToday.timeZone))

        # curr_event = c1.getCurrentEvent(time)

        self.ids.time.text = strftime('%I:%M')
        self.ids.ampm.text = strftime('%p')
        self.ids.date.text = strftime('%d/%m/%Y - %A')


        if calendarToday.currentEvent is not None:
            self.ids.ongoingEvent.text = calendarToday.currentEvent.title
            self.ids.ongoingTime.text = calendarToday.currentEvent.start.strftime('%I:%M') + " - " + calendarToday.currentEvent.end.strftime('%I:%M')
            if (time < calendarToday.currentEvent.start + timedelta(seconds=5)):
                buzzer.on()
                sleep(2)
                buzzer.off()
                sleep(1)
                buzzer.on()
                sleep(2)
                buzzer.off()

        else:   
            self.ids.ongoingEvent.text = ""
            self.ids.ongoingTime.text = ""


        self.ids.nextEvent.text = calendarToday.nextEvent.title
        self.ids.nextTime.text = calendarToday.nextEvent.start.strftime('%I:%M') + " - " + calendarToday.nextEvent.end.strftime('%I:%M')

        if calendarToday.currentEvent is not None:
            if calendarToday.currentEvent.end < time :
                calendarToday.updateCurrAndNextEvents()
        else:
            if calendarToday.lastUpdateTime + timedelta(minutes = 15) < time:
                calendarToday.updateCurrAndNextEvents()

    def on_pre_enter(self):
        Clock.schedule_once(self.update_time)
        Clock.schedule_interval(self.update_time, 1)




class menuScreen(Screen):
    
    def computerWakeup(self):
        send_magic_packet('70:8B:CD:0C:42:A5',ip_address = '192.168.1.255')
        print('woken')




class pomodoroScreen(Screen):

    start_time = datetime.now()
    end_time = datetime.now()
    remaining_time = timedelta(minutes = 1)
    pomo_count = 0

    status = 1 
    status_name = ['Ready','Pomo','Paused','Break']

    # status 1 = idle, 2 = pomo, 3 = pomopause, 4 = break

    def update_pomo(self,nap):

        self.ids.pomoTimeCurrent.text = strftime('%I:%M %p') + " - " + calendarToday.currentEvent.title
        self.ids.pomoCount.text = self.status_name[self.status-1] + ' || Count - '+ str(self.pomo_count)


        if self.status == 4:
            timeleft = self.end_time - datetime.now()
            if timeleft.seconds <=0:
                self.pomo_count = self.pomo_count
                buzzer.on()
                sleep(0.5)
                buzzer.off()
                self.button2_press()

            else:
                self.ids.pomoTime.text = (str(timeleft).split('.')[0])

        if self.status == 2:
            timeleft = self.end_time - datetime.now()

            if timeleft.seconds <=0:
                self.pomo_count = self.pomo_count + 1
                buzzer.on()
                sleep(0.5)
                buzzer.off()
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

        with open(str(Path.home())+'/dev/smartClock/settings.txt', 'rb') as f:
            settings = pickle.load(f)
            self.pomo_time = settings['pomo_time']
            self.break_time = settings['break_time']
            self.long_break = settings['long_break']

        self.status = 4
        self.button1_press()
        Clock.schedule_interval(self.update_pomo, .5)



class calendarScreen(Screen):
    displayDate = date.today()

    def createCalendar(self):
        self.ids.calendarscroll.clear_widgets()
        queryDate = self.displayDate
        events = calendarToday.getEvents(queryDate)
        layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for ent in events:
            timeStr= ent.start.strftime('%I:%M') + " - " + ent.end.strftime('%I:%M')
            lbl = Label(text=ent.title, size_hint_y=None, height=50,font_name = 'Roboto', font_size = 40,size_hint_x=.7)
            layout.add_widget(lbl)
            lbl = Label(text=timeStr, size_hint_y=None, height=50,font_name = 'Roboto', font_size = 40)
            layout.add_widget(lbl)
    
        
        self.ids.calendarscroll.add_widget(layout)
        self.ids.calendarDate.text = self.displayDate.strftime('%d/%m/%Y - %A')


    def on_pre_enter(self):
        self.createCalendar()

    def createNextCalendar(self):
        self.displayDate = self.displayDate + timedelta(days=1)
        self.createCalendar()

    def createPreviousCalendar(self):
        self.displayDate = self.displayDate - timedelta(days=1)
        self.createCalendar()

    def createTodayCalendar(self):
        self.displayDate = date.today()
        self.createCalendar()







class taskScreen(Screen):
    def createTasks(self):
        self.ids.tasksscroll.clear_widgets()
        taskList = tasks.getTasks()
        layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for tsk in taskList:

            if tsk.due == "":
                taskDue = "-" 
            else:
                taskDue = tsk.due.strftime('%d/%m(%a)')

            if tsk.status == 'completed':
                taskTitle = "[s]" + tsk.title + "[/s]"
                taskDue = "[s]" + taskDue + "[/s]"
            else:
                taskTitle = tsk.title

            lbl = Label(text=taskTitle, size_hint_y=None, height=50,font_name = 'Roboto', font_size = 40,size_hint_x=.9,markup = True)
            layout.add_widget(lbl)
            lbl = Label(text=taskDue, size_hint_y=None, height=50,font_name = 'Roboto', font_size = 40)
            layout.add_widget(lbl)
            
        self.ids.tasksscroll.add_widget(layout)

    def on_pre_enter(self):
        self.createTasks()




class configScreen(Screen):
    def configure_pomo(self):

        settings = {'pomo_time':int(self.ids.confdur.text),'break_time':int(self.ids.confbreak.text),'long_break':int(self.ids.conflbreak.text)}

        file = open(str(Path.home())+'/dev/smartClock/settings.txt', 'wb')
        pickle.dump(settings, file)
        file.close()
        self.parent.current = 'pomo'


    def on_pre_enter(self):
        with open(str(Path.home())+'/dev/smartClock/settings.txt', 'rb') as f:
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
