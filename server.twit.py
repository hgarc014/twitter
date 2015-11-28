import socket
import sys
import time
import signal
import json
from thread import *
#from check import ip_checksum

class Message(object):
	
	def __init__(self, message,hashtags,username):
		self.message=message
		self.hashtags=hashtags
		self.username=username
		self.isRead=False
		self.postTime=time.time()

class User(object):
	

	def __init__(self, userName, passwd,isAdmin):
		self.userName=userName
		self.passwd=passwd
		self.messages=[]
		self.subscriptions=[]
		self.isAdmin=isAdmin
		self.isLogin=False



def handler(signum, frame):
	print 'Timeout'
	raise Exception("Resend")

signal.signal(signal.SIGALRM, handler)

HOST = '' #means all available
PORT = 6481

pkt='packet'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print 'Socket created'

try:
	s.bind((HOST, PORT))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

except socket.error, msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

print 'Socket bind complete'

userlist=[]
allPosts=[]
test=User('user','pass',False)
test.subscriptions.append('u')
userlist.append(test);
userlist.append(User('u','p',False));
userlist.append(User('admin','m',True));

loginPre='login='
logoutPre='logout='
subscriptionsPre='subscriptions='
subscribePre='subscribe='
subscribeDropPre='subscribeDrop='
offlinePre='offline='
offlineUserPre='offlineUser='
postPre='post='
searchPre='search='
userMsgPre='msgcnt='
adminPre='admin='

def return_json(obj):
	return json.dumps(obj, default=lambda o: o.__dict__)

def check_input(functionT,field,text):
	print functionT + '.'+field +':'+text

def admin_options(data):
	global adminPre
	data=data[len(adminPre):]
	myj=json.loads(data)
	user = get_user(myj["user"])
	if user and user.isAdmin:
		res='Invalid command!'
		command = myj["command"]
		if  command == "messagecount":
			res=str(len(allPosts)) + ' messages received since server was activated'
		elif command == "usercount":
			i=0
			for user in userlist:
				if user.isLogin:
					i+=1
			res=str(i) + ' users are currently logged in'
		s.sendto('1'+adminPre+res,addr)
	else:
		s.sendto('0'+adminPre,addr)

def get_user_message_count(data):
	global userMsgPre
	username=data[len(userMsgPre):]
	#print 'received:'+username
	user = get_user(username)
	msgcnt=0
	if user:
		for msg in user.messages:
			if not msg.isRead:
				msgcnt += 1
		s.sendto('1'+userMsgPre+str(msgcnt),addr)
	else:
		s.sendto('0'+userMsgPre,addr)

def get_user(username):
	for user in userlist:
		if user.userName == username:
			return user
	return

def login_user(data):
	
	global loginPre
	wasValid=False
	username=data[len(loginPre):data.find(':')]
	passwd=data[data.find(':')+1:]
	mesgs=''
	user = get_user(username)
	if user and user.passwd == passwd:
		print 'Logged in user: ' + user.userName
		mesgs=len(user.messages)
		user.isLogin=True
		wasValid=True;
		
	if wasValid:
		print return_json(user)
		s.sendto('1'+loginPre+return_json(user),addr);
	else:
		s.sendto('0'+loginPre,addr);
	return


#allow changing of subscriptions, but only subscribe to valid users
def user_subscriptions(data):
	global subscriptionsPre
	username=data[len(subscriptionsPre):]
	user = get_user(username)
	if user:
		subs=[]
		for sub in user.subscriptions:
			subs.append(sub)
		#print 'Returned subscriptions for \'' + user.userName + '\''
		#print return_json(subs)
		s.sendto('1'+subscriptionsPre+return_json(subs),addr);
	else:
		s.sendto('0'+subscriptionsPre,addr);
	
def user_drop_subscription(data):
	global subscribeDropPre
	text=data[len(subscribeDropPre):]
	username=text[:text.find(':')]
	subrm=text[text.find(':')+1:]
	user = get_user(username)
	if user:
		user.subscriptions.remove(subrm)
		print 'Removed \''+subrm+'\' from \''+user.userName + '\' subscriptions'
		s.sendto('1'+subscribeDropPre,addr)
	else:
		s.sendto('0'+subscribeDropPre,addr)
	
	
def user_add_subscription(data):
	global subscribePre
	data=data[len(subscribePre):]
	myj = json.loads(data)
	username=myj["username"]
	subadd=myj["sub"]
	user = get_user(username)
	adduser=get_user(subadd)
	if adduser:
		if subadd not in user.subscriptions and subadd != user.userName:
			user.subscriptions.append(subadd);
			print 'Added \''+subadd+'\' to \''+user.userName+'\' subscriptions'
		s.sendto('1'+subscribePre,addr);
	else:
		s.sendto('0'+subscribePre,addr);
	
#list = Class(stuff) + list
	
def post_message(data):
	global postPre
	data = data[len(postPre):]
	#print data
	myj = json.loads(data)
	username=myj["username"]
	message=myj["message"]
	hashtags=myj["hashtags"]
	allPosts.append(Message(message,hashtags,username))
	
	for user in userlist:
		if username in user.subscriptions:
			user.messages.append(Message(message,hashtags,username))
			#if not user.isLogin:
			#	print '\nadding message offline message for ' + user.userName
				
	s.sendto('1'+postPre,addr)
		
	
	
#receive messages and redistribute to appropiate subscribers in real time

#store list of messages sent, but not delivered because user was offline

#allow admin to type messagecount in order to display number of received messages since server was activated

def logout_user(data):
        global logoutPre
	username=data[len(logoutPre) : data.find(':')]
	passwd=data[data.find(':')+1:]
	#print 'user:\"' + username + '\" pass:\"'+passwd+'\"'
	wasValid=False
	user = get_user(username)
	if user and user.passwd == passwd:
#	for user in userlist:
#		if user.userName == username and user.passwd == passwd:
		print 'logged out user: ' + user.userName;
		user.isLogin=False
		user.messages=[]
		wasValid=True
		
	if wasValid:
		s.sendto('1'+logoutPre,addr);
	else:
		s.sendto('0'+logoutPre,addr);
	return

def offline_all(data):
	global offlinePre
	username=data[len(offlinePre):]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		msg.isRead=True
		res.append(msg)
	#test = '|'.join(res)
	s.sendto('1'+offlinePre+return_json(res),addr)
	return
	


def offline_user(data):
	global offlineUserPre
	username=data[len(offlineUserPre):data.find(':')]
	sub_user=data[data.find(':')+1:]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		if msg.username == sub_user:
			msg.isRead=True
			res.append(msg)
	s.sendto('1'+offlineUserPre+return_json(res),addr)

def search_hashtag(data):
	global searchPre
	tags=data[len(searchPre):]
	tags = json.loads(tags)
	#print tags
	res=[]
	for searchtag in tags:
		for message in allPosts:
			if len(res) == 10:
				break
			for tag in message.hashtags:
				#print tag.lower() + '=='+searchtag.lower()
				if tag.lower() == searchtag.lower():
					res.append(message)
					break
	#print return_json(res)
	s.sendto('1'+searchPre+return_json(res),addr)

while 1:
	d = s.recvfrom(1024)
	data = d[0]
	addr = d[1]
	
	if loginPre in data:
		login_user(data)
	elif logoutPre in data:
		logout_user(data)
	elif subscriptionsPre in data:
		user_subscriptions(data)
	elif subscribeDropPre in data:
		user_drop_subscription(data)
	elif subscribePre in data:
		user_add_subscription(data)
	elif offlinePre in data:
		offline_all(data)
	elif offlineUserPre in data:
		offline_user(data)
	elif postPre in data:
		post_message(data)
	elif searchPre in data:
		search_hashtag(data)
	elif userMsgPre in data:
		get_user_message_count(data)
	elif adminPre in data:
		admin_options(data)

s.close()

