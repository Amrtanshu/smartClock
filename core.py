import requests
import json
import utilities
from datetime import datetime, timedelta
import config


url = config.url

def convertTime(time):
	date = datetime.fromisoformat(time[:-1])
	offset = timedelta(seconds=19800)
	date = date + offset
	return date

def inBetween(startTime, endTime, nowTime): 
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime

class event():
	def __init__(self,title,start,end,color):
		self.title = title
		self.start = start
		self.end = end
		self.color = color

class task():
	def __init__(self,title,taskid,status,tasklist):
		self.title = title
		self.taskid = taskid
		self.status = status
		self.tasklist = tasklist


	def takeAction(self,doAction):
		params = dict(
			action = doAction,
			taskid = self.taskid)
		resp = requests.post(url,params = param)



class calendar:

	def getEvents(self,date):
		params = dict(
			action="schedule",
			day=date
		)
		resp = requests.get(url,params = params);
		schedule = resp.json()
		schedule = schedule["events"]
		events = [];

		for entry in schedule:
			eve = event(entry["title"],convertTime(entry["start"]),convertTime(entry["end"]),entry["color"])
			events.append(eve)
		self.events = events
		return events

	def getCurrentEvent(self,time):
		currEvents = [];
		for event in self.events:
			if(inBetween(event.start,event.end,time)):
				currEvents.append(event)
		return currEvents



class tasks:

	def getTasks(self):

		params = dict(
			action="tasks",
		)
		resp = requests.get(url,params = params);
		tasklists = resp.json()
		tasklists = tasklists["tasks"]
		tasks = [];

		for entry in tasklists:
			tsk = task(entry["title"],entry["id"],entry["status"],entry["list"])
			tasks.append(tsk)
		self.tasks = tasks
		return tasks



c1 = calendar()
sch = c1.getEvents("2021-11-18")
time = datetime.now()
curr_event = c1.getCurrentEvent(time)

t1 = tasks()
tks = t1.getTasks()
