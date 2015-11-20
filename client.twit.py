
#socket client exmaple

import socket
import sys
import time
#from check import ip_checksum

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

except socket.error, msg:
	print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
	sys.exit();

print 'Socket Created'

host = 'localhost'
port = 6481 

pleaseWait='\nPlease do not use this function it is under construction, thanks!\n'
user=''
passwd=''


loginPre='login='
logoutPre='logout='
subscribePre='subscribe='
offlinePre='offline='
postPre='post='
searchPre='search='

#------------------
#while user logged in make sure to display real time message sent by any subscriptions
#-----------------



#offline messages
#displays messages that were displayed when user was offline
#has option to display all or only from a subscription
#when user logs out these messages should be removed
def offline_message():
	print pleaseWait
	return

#edit subscriptions
#allow user to add or drop a subscription (user)
#if drop only show current subscriptions
#if add ask for name and tell if user exists
def edit_subscriptions():
	print pleaseWait
	return

#post message
#140 characters or less
#ask for hashtags afterwards
#if larger than 140 notify user and tell them to re-enter (or cancel)
def post_message():
	print pleaseWait
	return

#hashtag search
#user will see 10 tweets containing hashtag
def hashtag_search():
	print pleaseWait
	return

def logout_user():
	global user
	global passwd
	global logoutPre
	
	s.sendto(logoutPre+user+':'+passwd, (host,port));
	d= s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply == '1'+logoutPre:
		print 'You have been logged out!'
	else:
		print 'WARNING: error occured'
		return logout_user()
	#TODO: tell server you logged out
	login_user();
	return

def menu_disp():
	print '1: See Offline Message'
	print '2: Edit Subscriptions'
	print '3: Post a Message'
	print '4: Hashtag Search'
	print '5: Logout'
	
	choice=raw_input("Choice:")
	if choice == '1':
		offline_message();
	elif choice =='2':
		edit_subscriptions();
	elif choice == '3':
		post_message();
	elif choice == '4':
		hashtag_search();
	elif choice == '5':
		logout_user();
	else:
		print '\nInvalid Response! Try again!\n'
		menu_disp()
	menu_disp()


def login_user():
	global user
	global passwd
	global loginPre

	euser='Enter Username:'
	epass='Enter Password:'
	
	user=raw_input(euser)
	passwd=raw_input(epass)
	
	msg =loginPre+user+':'+passwd 
	
	try:
		s.sendto(msg, (host, port))
	except socket.error, msg:
		print 'Error code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	
	d = s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	
	if reply[:len(loginPre)+1] == '1'+loginPre:
		msgs=reply[len(loginPre)+1:]
		print 'Welcome ' + user + ' You have '+msgs+' unread messages.'
		menu_disp();
	else:
		print 'Login Failed! Please Re-try!'
		login_user()
	return

login_user();

#while 1:
#
#	d = s.recvfrom(1024)
#	reply = d[0]
#	addr = d[1]
#
#	print 'Server reply : ' + reply
#
#	try:
#		s.sendto(reply, (host, port))
#
#	except socket.error, msg:
#		print 'Error code : ' + str(msg[0]) + ' Message ' + msg[1]
#		sys.exit()

s.close()

