import socket
import sys
import time
import signal
from thread import *
#from check import ip_checksum

class Message(object):
	
	def __init__(self, message, isRead):
		self.message=message
		self.isRead=isRead

class User(object):
	

	def __init__(self, userName, passwd):
		self.userName=userName
		self.passwd=passwd
		self.messages=[]
		self.subscriptions=[]
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
test=User('user','pass')
test.subscriptions.append('u')
userlist.append(test);
userlist.append(User('u','p'));
userlist.append(User('admin','m'));

loginPre='login='
logoutPre='logout='
subscriptionsPre='subscriptions='
subscribePre='subscribe='
subscribeDropPre='subscribeDrop='
offlinePre='offline='
postPre='post='
searchPre='search='

def check_input(functionT,field,text):
	print functionT + '.'+field +':'+text

def get_user(username):
	for user in userlist:
		if user.userName == username:
			return user
	return

def login_user(data):
	
        global loginPre
	wasValid=False
	#if data[:2] == '0=':
	username=data[len(loginPre):data.find(':')]
	passwd=data[data.find(':')+1:]
	#print 'user:\"' + username + '\" pass:\"'+passwd+'\"'
	mesgs=''
	user = get_user(username)
	if user and user.passwd == passwd:
#	for user in userlist:
#		if user.userName == username and user.passwd == passwd:
		print 'Logged in user: ' + user.userName
		mesgs=len(user.messages)
		user.isLogin=True
		wasValid=True;
		
	if wasValid:
		s.sendto('1'+loginPre+str(mesgs),addr);
	else:
		s.sendto('0'+loginPre,addr);
	return


#allow changing of subscriptions, but only subscribe to valid users
def user_subscriptions(data):
	global subscriptionsPre
	username=data[len(subscriptionsPre):]
	check_input("user_sub",'data',data)
	check_input("user_sub","username",username)
	user = get_user(username)
	if user:
		subs=''
		for sub in user.subscriptions:
			if len(subs) == 0:
				subs += sub
			else:
				subs += ':'+sub
		s.sendto('1'+subscriptionsPre+subs,addr);
	else:
		s.sendto('0'+subscriptionsPre,addr);
	
def user_drop_subscription(data):
	global subscribeDropPre
	text=data[len(subscribeDropPre):]
	username=text[:text.find(':')]
	subrm=text[text.find(':')+1:]
	check_input("drop_sub",'data',data)
	check_input("drop_sub","username",username)
	check_input("drop_sub","sub",subrm)
	user = get_user(username)
	if user:
		user.subscriptions.remove(subrm)
		s.sendto('1'+subscribeDropPre,addr)
	else:
		s.sendto('0'+subscribeDropPre,addr)
	
	
def user_add_subscription(data):
	global subscribePre
	text=data[len(subscribePre):]
	username=text[:text.find(':')]
	subadd=text[text.find(':')+1:]
	check_input("add_sub",'data',data)
	check_input("add_sub","username",username)
	check_input("add_sub","sub",subadd)
	user = get_user(username)
	adduser=get_user(subadd)
	if adduser:
		if subadd not in user.subscriptions:
			user.subscriptions.append(subadd);
		s.sendto('1'+subscribePre,addr);
	else:
		s.sendto('0'+subscribePre,addr);
	
	
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
		wasValid=True
		
	if wasValid:
		s.sendto('1'+logoutPre,addr);
	else:
		s.sendto('0'+logoutPre,addr);
	return


while 1:
	d = s.recvfrom(1024)
	data = d[0]
	addr = d[1]
	
	if data.find(loginPre) != -1:
		login_user(data)
	elif data.find(logoutPre) != -1:
		logout_user(data)
	elif data.find(subscriptionsPre) != -1:
		user_subscriptions(data)
	elif data.find(subscribeDropPre) != -1:
		user_drop_subscription(data)
	elif data.find(subscribePre) != -1:
		user_add_subscription(data)
	elif data.find(offlinePre) != -1:
		pass
		#user_add_subscription(data)
	elif data.find(postPre) != -1:
		pass
		#user_add_subscription(data)
	elif data.find(searchPre) != -1:
		pass
		#user_add_subscription(data)

s.close()

