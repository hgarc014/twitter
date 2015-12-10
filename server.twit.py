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
	saveInfo(allPosts,'posts.json')
	saveInfo(userlist,'users.json')
	sys.exit(0)
		
s.close()

