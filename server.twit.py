#~ import socket
#~ import sys
#~ import time
#~ import signal
#~ import json
#~ import os
#~ import hashlib
#~ from thread import *
from serverfunc import *
from shared import *


	
clear_screen()


#def handler(signum, frame):
#	print 'Timeout'
#	raise Exception("Resend")

#signal.signal(signal.SIGALRM, handler)

HOST = '' #means all available
PORT = 6481

pkt='packet'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	

except socket.error, msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()


print 'Socket bind complete'

s.listen(10)


#~ 
#~ userlist=[]
#~ allPosts=[]

postfile='posts.json'
userfile='users.json'

with open(userfile) as userdata:
	try:
		tempUsers=json.load(userdata)
		for user in tempUsers:
			tuser=User(user['userName'],user['passwd'],user['isAdmin'])
			tuser.messages=user['messages']
			tuser.subscriptions=user['subscriptions']
			tuser.followers=user['followers']
			#~ userName, passwd,isAdmin,messages,subscriptions,followers
			userlist.append(tuser)
	except ValueError:
		userlist=[]
	

with open(postfile) as postdata:
	try:
		tempPosts=json.load(postdata)
		for post in tempPosts:
			tpost=Message(post['message'],post['hashTags'],post['userName'])
			tpost.postTime=post['postTime']
			tpost.isRead=True
			#~ message,hashTags,userName,postTime
			allPosts.append(tpost)
	except ValueError:
		allPosts=[]


if len(userlist) == 0:
	print 'no users were saved'
	userlist.append(User('user',md5('p'),False));
	userlist.append(User('u',md5('p'),False));
	userlist.append(User('admin',md5('p'),True));

	for i in range(1,51):
		userlist.append(User('u'+str(i),md5('p'),False));





try:	
	while 1:
		conn, addr = s.accept()
		start_new_thread(clientthread,(conn,addr))
except KeyboardInterrupt:
	print
	saveInfo(allPosts,postfile)
	saveInfo(userlist,userfile)
	sys.exit(0)
		
s.close()

