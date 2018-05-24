import requests
import json
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, jsonify

greetNewUsersInterval = 5  #in seconds
requestUrl = "https://api.telegram.org/bot"
token      = "579760998:AAEEDEE_EXNvPXnSVAfXsAs44uH0JH-p-WU"
welcomeMessage = 'Welcome to the group: '


app = Flask(__name__)
newUsers = []
firstRun = True
def doAPIRequest(url):
  result = None  
  try:
    r = requests.get(url)
    if r.status_code == 200:
      data = json.loads(r.text)
      if data['ok'] == True:
        result = data
  except Exception:
	  print("Error in API Request")

  return result

def sendMessage(chatID, message):  
  method = "sendMessage?chat_id={0}&text={1}".format(chatID, message)
  url = "{0}{1}/{2}".format(requestUrl, token, method)
  print url
  doAPIRequest(url)

def greetNewUsers():
  global firstRun
  try:
    print 'Greeting new users'    
    data = doAPIRequest("{0}{1}/{2}".format(requestUrl, token, "getUpdates"))
    if data is not None:
      for result in data['result']:
        if 'message' in result:
          message = result['message']
          if "new_chat_member" in message:            
            chatID = message['chat']['id']            
            new_chat_member = message['new_chat_member']
            if 'first_name' in new_chat_member:
              userID = new_chat_member['id']
              if userID not in newUsers:
                newUsers.append(userID)
                if firstRun:
                  continue
                  
                messageToSend = welcomeMessage + new_chat_member['first_name']
                sendMessage(chatID, messageToSend)                  
                print welcomeMessage + new_chat_member['first_name']

      if firstRun:
        firstRun = False

  except Exception:
	  print("Unknown Error")


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(func=greetNewUsers, trigger=IntervalTrigger(seconds=greetNewUsersInterval), id='greetNewUsers', name='greetNewUsers', replace_existing=True)
atexit.register(lambda: scheduler.shutdown())


@app.route('/', methods=['GET', 'POST'])
def home():   
  resp_dict = { 'msg': 'new user bot'}
  return jsonify(resp_dict)


if __name__ == '__main__':
	app.run(debug=False)