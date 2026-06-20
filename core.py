import requests
import json
import config
from datetime import datetime, timedelta, date, time
import pytz

url = config.url

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/tasks','https://www.googleapis.com/auth/calendar.readonly']

def initialize():
		"""Shows basic usage of the Tasks API.
		Prints the title and ID of the first 10 task lists.
		"""
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		creds = None

		if os.path.exists('/home/pi/dev/smartClock/token.json'):
			creds = Credentials.from_authorized_user_file('/home/pi/dev/smartClock/token.json', SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
							'/home/pi/dev/smartClock/credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('/home/pi/dev/smartClock/token.json', 'w') as token:
				token.write(creds.to_json())

def convertTime(time):
	# date = datetime.fromisoformat(time[:-1])
	offset = timedelta(seconds=19800)
	date = time - offset
	return date

def inBetween(startTime, endTime, nowTime): 
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime

class event():
	def __init__(self,title,start,end):
		self.title = title
		self.start = datetime.fromisoformat(start.get('dateTime'))
		self.end = datetime.fromisoformat(end.get('dateTime'))

class calendar:

	def __init__(self):
		creds = Credentials.from_authorized_user_file('/home/pi/dev/smartClock/token.json', SCOPES)
		service = build('calendar', 'v3', credentials=creds)
		self.service = service
		self.timeZone = service.calendars().get(calendarId = '2i5fq9518u7aqaourpqs2anor4@group.calendar.google.com').execute().get("timeZone")

	def getEvents(self,queryDate):

		try:
	        # Call the Calendar API
			startTime = convertTime(datetime.combine(queryDate,time())).isoformat() + 'Z';
			endTime = convertTime(datetime.combine(queryDate,time())+timedelta(days = 1)).isoformat() + 'Z';


			events_result = self.service.events().list(calendarId='2i5fq9518u7aqaourpqs2anor4@group.calendar.google.com', timeMin=startTime,
                                              timeMax=endTime, singleEvents=True,
                                              orderBy='startTime').execute()
			eventList = events_result.get('items', [])

			events = []

			for entry in eventList:
				eve = event(entry["summary"],(entry["start"]),(entry["end"]))
				events.append(eve)

			self.events = events

			return events

		except HttpError as error:
			print('An error occurred: %s' % error)


	def updateCurrAndNextEvents(self):
		now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
		events_result = self.service.events().list(calendarId='2i5fq9518u7aqaourpqs2anor4@group.calendar.google.com', timeMin=now,
		                          maxResults=2, singleEvents=True,
		                          orderBy='startTime').execute()
		eventList = events_result.get('items', [])

		events = [];

		for entry in eventList:
			print(entry["summary"])
			eve = event(entry["summary"],(entry["start"]),(entry["end"]))
			events.append(eve)

		time = datetime.now(pytz.timezone(self.timeZone))
		self.lastUpdateTime = time

		if(inBetween(events[0].start,events[0].end,time)):
			self.currentEvent = events[0];
			self.nextEvent = events[1];
		else:
			self.currentEvent = None
			self.nextEvent = events[0]

	def getCurrentEvent(self,time):
		currEvents = [];
		for event in self.events:
			if(inBetween(event.start,event.end,time)):
				currEvents.append(event)
		return currEvents
	
	def getNextEvent(self,currEvent):
		nextEvent = self.getCurrentEvent(currEvent.end+timedelta(seconds=5))
		return nextEvent


class task():
	def __init__(self,title,taskid,status,due,tasklist):
		self.title = title
		self.taskid = taskid
		self.status = status
		self.tasklist = tasklist
		if due!= "":
			self.due = datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ')
		else:
			self.due = ""

		# self.due = datetime.fromisoformat(due.get('dateTime'))


	def takeAction(self,doAction):
		params = dict(
			action = doAction,
			taskid = self.taskid)
		resp = requests.post(url,params = param)

class tasklist():
	def __init__(self,title,taskListId,tasks):
		self.title = title
		self.id = taskListId
		self.tasks = tasks

class tasks:

	def __init__(self):
		creds = Credentials.from_authorized_user_file('/home/pi/dev/smartClock/token.json', SCOPES)
		service = build('tasks', 'v1', credentials=creds)
		self.service = service

	def getTasks(self):
		try:

			taskResults = self.service.tasks().list(tasklist="N0wyWXExRlY2NVFydV9rcQ").execute()
			taskItems = taskResults.get('items',[])
			tasks = []

			for taskEntry in taskItems:
				if "due" in taskEntry:
					duedate = taskEntry["due"]
				else:
					duedate = ""

				tsk = task((taskEntry["title"]),(taskEntry["id"]),(taskEntry["status"]),duedate,"N0wyWXExRlY2NVFydV9rcQ")
				tasks.append(tsk)

			self.tasks = tasks
			return tasks

		except HttpError as err:
			print(err)

	def markComplete(self,task):

		try:
			taskID = task.taskid
			taskListID = task.tasklist

			taskBody = {
			'status' : 'completed',
			'id' : task.taskid,
			# 'title' : task.title,
			# 'due' : task.due
			}

			result = self.service.tasks().patch(tasklist = taskListID, task = taskID, body = taskBody).execute()


		except HttpError as err:
			print(err)




# initialize()

# c1 = calendar()
# print(c1.timeZone)
# time = datetime.now(pytz.timezone(c1.timeZone))
# print(time)
# c1.updateCurrAndNextEvents();
# print(c1.currentEvent.title)
# print(c1.nextEvent.title)









# queryDate = date.today()



# events = c1.getEvents(queryDate)



# for ent in events:
# 	print(ent.title,ent.start.tzinfo,ent.end,ent.color)

# time = datetime.now(events[0].start.tzinfo)
# curr_event = c1.getCurrentEvent(time)
# NextEvent = c1.getNextEvent(curr_event[0])

# print(curr_event[0].title)
# print(NextEvent[0].title)

# t1 = tasks()
# tks = t1.getTasks()
# tkl = tks[1]
# tk = tkl.tasks[1]
# print(tk.title,tk.taskid,tk.tasklist)
# t1.markComplete(tk)
# for item in tks:
# 	print(item.title, item.taskid, item.status, item.due)
# 	for task in item.tasks:
# 		print(task.title,task.taskid,task.tasklist)

