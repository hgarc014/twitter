import socket
import sys
import time
import signal
import json
import os
import hashlib
from thread import *
from shared import *




userlist=[]
allPosts=[]


def saveInfo(data,filename):
	myj=json.loads(return_json(data))
	with open(filename,'w') as outf:
		json.dump(myj,outf)

def clear_screen():
	unused_var=os.system('clear')
	
def md5(passwd):
	return hashlib.md5(passwd.encode('utf-8')).hexdigest()
	
	
	

def change_pass(conn,data):
	#global changePassPre
	data = data[len(FUNCTION.changePassPre):]
	myj=json.loads(data)
	username=myj['username']
	oldpass=myj['currentpass']
	newpass=myj['newpass']
	user = get_user(username)
	if user and user.passwd == oldpass:
		user.passwd=newpass
		conn.send('1'+FUNCTION.changePassPre)
	else:
		conn.send('0'+FUNCTION.changePassPre)

def get_followers(conn,data):
	#global followersPre
	data = data[len(FUNCTION.followersPre):]
	user = get_user(data)
	#print user.userName+' has followers:'+ ', '.join(user.followers)
	if user:
		conn.send('1'+FUNCTION.followersPre+return_json(user.followers))
	else:
		conn.send('0'+FUNCTION.followersPre)

def return_json(obj):
	return json.dumps(obj, default=lambda o: o.__dict__)

def check_input(functionT,field,text):
	print functionT + '.'+field +':'+text


def admin_options(conn,data):
	#~ global adminPre
	data=data[len(FUNCTION.adminPre):]
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
		conn.send('1'+FUNCTION.adminPre+res)
	else:
		conn.send('0'+FUNCTION.adminPre)

def get_user_message_count(conn,data):
	#~ global userMsgPre
	username=data[len(FUNCTION.userMsgPre):]
	#print 'received:'+username
	user = get_user(username)
	msgcnt=0
	if user:
		user.connection=conn
		for msg in user.messages:
			if not msg.isRead:
				msgcnt += 1
		#~ print 'returned ' + str(msgcnt)
		conn.send('1'+FUNCTION.userMsgPre+str(msgcnt))
	else:
		print 'failed'
		conn.send('0'+FUNCTION.userMsgPre)

def get_user(username):
	for user in userlist:
		if user.userName == username:
			return user
	return

def login_user(conn,data):
	
	#~ global loginPre
	wasValid=False
	data = data[len(FUNCTION.loginPre):]
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
		conn.send('1'+FUNCTION.loginPre+return_json(user));
		return username
	else:
		conn.send('0'+FUNCTION.loginPre);
	return


#allow changing of subscriptions, but only subscribe to valid users
def user_subscriptions(conn,data):
	#~ global subscriptionsPre
	username=data[len(FUNCTION.subscriptionsPre):]
	user = get_user(username)
	if user:
		subs=[]
		for sub in user.subscriptions:
			subs.append(sub)
		#print 'Returned subscriptions for \'' + user.userName + '\''
		conn.send('1'+FUNCTION.subscriptionsPre+return_json(subs));
	else:
		conn.send('0'+FUNCTION.subscriptionsPre);
	
def user_drop_subscription(conn,data):
	#~ global subscribeDropPre
	text=data[len(FUNCTION.subscribeDropPre):]
	username=text[:text.find(':')]
	subrm=text[text.find(':')+1:]
	user = get_user(username)
	subuser=get_user(subrm)
	if user:
		user.subscriptions.remove(subrm)
		subuser.followers.remove(user.userName)
		print 'Removed \''+subrm+'\' from \''+user.userName + '\' subscriptions'
		conn.send('1'+FUNCTION.subscribeDropPre)
	else:
		conn.send('0'+FUNCTION.subscribeDropPre)
	
	
def user_add_subscription(conn,data):
	#~ global subscribePre
	data=data[len(FUNCTION.subscribePre):]
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
		conn.send('1'+FUNCTION.subscribePre);
	else:
		conn.send('0'+FUNCTION.subscribePre);
	
#list = Class(stuff) + list
	
def post_message(conn,data):
	#~ global postPre
	data = data[len(FUNCTION.postPre):]
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
			if user.connection:
				#print 'Calling count for ' + user.userName
				get_user_message_count(user.connection,FUNCTION.userMsgPre+user.userName)
				
	conn.send('1'+FUNCTION.postPre)
		
	
	
#receive messages and redistribute to appropiate subscribers in real time

#store list of messages sent, but not delivered because user was offline

#allow admin to type messagecount in order to display number of received messages since server was activated

def logout_username(username):
	user = get_user(username)
	if user and user.isLogin:
		user.isLogin=False
		user.messages=[]
		user.connection=''
		print 'logged out user: ' + user.userName;
		return True
	return False 

def logout(conn,data):
        #~ global logoutPre
	username=data[len(FUNCTION.logoutPre):]
	wasValid=logout_username(username)
	#~ user = get_user(username)
	#~ if user:
#~ #	for user in userlist:
#~ #		if user.userName == username and user.passwd == passwd:
		#~ print 'logged out user: ' + user.userName;
		#~ user.isLogin=False
		#~ user.messages=[]
		#~ user.connection=''
		#~ wasValid=True
		
	if wasValid:
		conn.send('1'+FUNCTION.logoutPre);
	else:
		conn.send('0'+FUNCTION.logoutPre);

def make_msgs_read(msgs):
	for msg in msgs:
		msg.isRead=True

def offline_all(conn,data):
	#~ global offlinePre
	username=data[len(FUNCTION.offlinePre):]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		res.append(msg)
	#res.reverse()
	conn.send('1'+FUNCTION.offlinePre+return_json(res))
	make_msgs_read(res)
	get_user_message_count(user.connection,FUNCTION.userMsgPre+user.userName)


def offline_user(conn,data):
	#~ global offlineUserPre
	username=data[len(FUNCTION.offlineUserPre):data.find(':')]
	sub_user=data[data.find(':')+1:]
	user = get_user(username)
	res=[]
	for msg in user.messages:
		if msg.username == sub_user:
			res.append(msg)
	#res.reverse()
	conn.send('1'+FUNCTION.offlineUserPre+return_json(res))
	make_msgs_read(res)
	get_user_message_count(user.connection,FUNCTION.userMsgPre+user.userName)
	#user.connection=''

def search_hashtag(conn,data):
	#~ global searchPre
	tags=data[len(FUNCTION.searchPre):]
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
	conn.send('1'+FUNCTION.searchPre+return_json(res))

def clientthread(conn,addr):
	
	user=''
	while True:
		data = conn.recv(1024)
		if not data:
			break
		elif FUNCTION.loginPre in data:
			user = login_user(conn,data)
		elif FUNCTION.userMsgPre in data:
			get_user_message_count(conn,data)
		elif user and FUNCTION.logoutPre in data:
			logout(conn,data)
			user=''
		elif user and FUNCTION.subscriptionsPre in data:
			user_subscriptions(conn,data)
		elif user and FUNCTION.subscribeDropPre in data:
			user_drop_subscription(conn,data)
		elif user and FUNCTION.subscribePre in data:
			user_add_subscription(conn,data)
		elif user and FUNCTION.offlinePre in data:
			offline_all(conn,data)
		elif user and FUNCTION.offlineUserPre in data:
			offline_user(conn,data)
		elif user and FUNCTION.postPre in data:
			post_message(conn,data)
		elif user and FUNCTION.searchPre in data:
			search_hashtag(conn,data)
		elif user and FUNCTION.adminPre in data:
			admin_options(conn,data)
		elif user and FUNCTION.followersPre in data:
			get_followers(conn,data)
		elif user and FUNCTION.changePassPre in data:
			change_pass(conn,data)
	if user:
		logout_username(user)
	conn.close()
