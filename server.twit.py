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
		self.subscripts=[]
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
userlist.append(User('user','pass'));
userlist.append(User('u','p'));
userlist.append(User('admin','m'));

loginPre='login='
logoutPre='logout='
subscribePre='subscribe='
offlinePre='offline='
postPre='post='
searchPre='search='

def login_check(data):
	
        global loginPre
	wasValid=False
	#if data[:2] == '0=':
	username=data[len(loginPre):data.find(':')]
	passwd=data[data.find(':')+1:]
	print 'user:\"' + username + '\" pass:\"'+passwd+'\"'
	mesgs=''
	for user in userlist:
		if user.userName == username and user.passwd == passwd:
			print 'Logged in user: ' + user.userName
			mesgs=len(user.messages)
			user.isLogin=True
			wasValid=True;
			break;
	if wasValid:
		s.sendto('1'+loginPre+str(mesgs),addr);
	else:
		s.sendto('0'+loginPre,addr);
	return


#allow changing of subscriptions, but only subscribe to valid users

#receive messages and redistribute to appropiate subscribers in real time

#store list of messages sent, but not delivered because user was offline

#allow admin to type messagecount in order to display number of received messages since server was activated

def mylogout(data):
        global logoutPre
	username=data[len(logoutPre) : data.find(':')]
	passwd=data[data.find(':')+1:]
	print 'user:\"' + username + '\" pass:\"'+passwd+'\"'
	wasValid=False
	for user in userlist:
		if user.userName == username and user.passwd == passwd:
			print 'logged out user: ' + user.userName;
			user.isLogin=False
			wasValid=True
			break
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
		login_check(data)
	elif data.find(logoutPre) != -1:
		mylogout(data)

s.close()

