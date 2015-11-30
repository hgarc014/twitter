import socket
import sys
import time
import signal
import json
import os
import hashlib
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
		self.followers=[]
		self.isAdmin=isAdmin
		self.isLogin=False

	
def clear_screen():
	unused_var=os.system('clear')
	
clear_screen()


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

def md5(passwd):
	return hashlib.md5(passwd.encode('utf-8')).hexdigest()

userlist=[]
allPosts=[]
userlist.append(User('user',md5('p'),False));
userlist.append(User('u',md5('p'),False));
userlist.append(User('admin',md5('p'),True));

for i in range(1,51):
	userlist.append(User('u'+str(i),md5('p'),False));


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
followersPre='followers='
changePassPre='changePass='

def change_pass(data):
	global changePassPre
	data = data[len(changePassPre):]
	myj=json.loads(data)
	username=myj['username']
	oldpass=myj['currentpass']
	newpass=myj['newpass']
	user = get_user(username)
	if user and user.passwd == oldpass:
		user.passwd=newpass
		s.sendto('1'+changePassPre,addr)
	else:
		s.sendto('0'+changePassPre,addr)

def get_followers(data):
	global followersPre
	data = data[len(followersPre):]
	user = get_user(data)
	#print user.userName+' has followers:'+ ', '.join(user.followers)
	if user:
		s.sendto('1'+followersPre+return_json(user.followers),addr)
	else:
		s.sendto('0'+followersPre,addr)

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
		elif command == 'storedcount':
			i=0
			for user in userlist:
				if not user.isLogin:
					for message in user.messages:
						i += 1
			res=str(i) + ' messages have not yet been delivered because the user is offline'
		elif command == 'newuser':
			newUser=get_user(myj['newuser'])
			newIsAdmin=myj['isAdmin']
			newuser=myj['newuser']
			newpass=myj['passwd']
			if newIsAdmin == 'T':
				newIsAdmin=True
			else:
				newIsAdmin=False
			if not newUser and len(newuser) > 0 and len(newpass)>0:
				userlist.append(User(newuser,newpass,newIsAdmin))
				res='Successfully created user "'+newuser+'" isAdmin "'+str(newIsAdmin)+'"'
			elif newUser:
				res='User "'+newUser.userName+'" already exists'
			else:
				res='Failed to create user "'+newuser+'" isAdmin "'+str(newIsAdmin)+'"'
		elif command == 'commands':
			commands=['messagecount','usercount','storedcount','newuser']
			res='\n*'+'\n*'.join(commands)
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
	data = data[len(loginPre):]
	myj=json.loads(data)
	username=myj['username']
	passwd=myj['passwd']
	mesgs=''
	user = get_user(username)
	if user and user.passwd == passwd:
		print 'Logged in user: ' + user.userName
		mesgs=len(user.messages)
		user.isLogin=True
		wasValid=True;
		
	if wasValid:
		#print return_json(user)
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
		s.sendto('1'+subscriptionsPre+return_json(subs),addr);
	else:
		s.sendto('0'+subscriptionsPre,addr);
	
def user_drop_subscription(data):
	global subscribeDropPre
	text=data[len(subscribeDropPre):]
	username=text[:text.find(':')]
	subrm=text[text.find(':')+1:]
	user = get_user(username)
	subuser=get_user(subrm)
	if user:
		user.subscriptions.remove(subrm)
		subuser.followers.remove(user.userName)
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
			adduser.followers.append(user.userName)
			print 'Added "'+user.userName+'" to "'+subadd+'" followers'
			print 'Added \''+subadd+'\' to \''+user.userName+'\' subscriptions'
		s.sendto('1'+subscribePre,addr);
	else:
		s.sendto('0'+subscribePre,addr);
	
#list = Class(stuff) + list
	
def post_message(data):
	global postPre
	data = data[len(postPre):]
	myj = json.loads(data)
	username=myj["username"]
	message=myj["message"]
	hashtags=myj["hashtags"]
	allmsg=Message(message,hashtags,username)
	allmsg.isRead=True
	allPosts.append(allmsg)
	
	for user in userlist:
		if username in user.subscriptions:
			user.messages.append(Message(message,hashtags,username))
				
	s.sendto('1'+postPre,addr)
		
	
	
#receive messages and redistribute to appropiate subscribers in real time

#store list of messages sent, but not delivered because user was offline

#allow admin to type messagecount in order to display number of received messages since server was activated

def logout_user(data):
        global logoutPre
	username=data[len(logoutPre):]
	wasValid=False
	user = get_user(username)
	if user:
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

def make_msgs_read(msgs):
	for msg in msgs:
		msg.isRead=True

def offline_all(data):
	global offlinePre
	username=data[len(offlinePre):]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		res.append(msg)
	#res.reverse()
	s.sendto('1'+offlinePre+return_json(res),addr)
	make_msgs_read(res)
	return
	


def offline_user(data):
	global offlineUserPre
	username=data[len(offlineUserPre):data.find(':')]
	sub_user=data[data.find(':')+1:]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		if msg.username == sub_user:
			res.append(msg)
	#res.reverse()
	s.sendto('1'+offlineUserPre+return_json(res),addr)
	make_msgs_read(res)

def search_hashtag(data):
	global searchPre
	tags=data[len(searchPre):]
	tags = json.loads(tags)
	res=[]
	for searchtag in tags:
		for message in allPosts:
			if len(res) == 10:
				break
			for tag in message.hashtags:
				if tag.lower() == searchtag.lower():
					res.append(message)
					break
	#res.reverse()
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
	elif followersPre in data:
		get_followers(data)
	elif changePassPre in data:
		change_pass(data)
		
s.close()

