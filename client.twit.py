
#socket client exmaple

import socket
import sys
import time
import os
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
msgs=''


loginPre='login='
logoutPre='logout='
subscribePre='subscribe='
subscriptionsPre='subscriptions='
subscribeDropPre='subscribeDrop='
offlinePre='offline='
postPre='post='
searchPre='search='

def clear_screen():
	time.sleep(.5)
	unused_var=os.system('clear')
	
def print_header(menu):
	#clear_screen()
	print '\n====== ' + menu + ' ======\n'

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

def drop_subscription(subs):
	
	print_header('Drop subscription')
	subscriptions=subs.split(':')
	
	if len(subs) == 0:
		print 'You have no subscriptions'
	else:
		i=0
		for sub in subscriptions:
			i += 1
			print str(i) + ':' +sub
			
		i += 1
		print str(i) + ':cancel'
		choice=raw_input("Choice:")
		try:
			choice = int(choice)
		except ValueError:
			donothing=''
		if type(choice) ==int and choice >= 1 and choice <= i:
			if choice == i:
				return
			s.sendto(subscribeDropPre+user+':'+subscriptions[choice-1],(host,port))
			d = s.recvfrom(1024)
			reply = d[0]
			addr = d[1]
			if reply[:len(subscribeDropPre)+1] == '1'+subscribeDropPre:
				print 'Successfully unsubscribed to ' + subscriptions[choice-1]
			else:
				print 'Error occured for unsubscribing to ' + subscriptions[choice-1]
		else:
			print 'Invalid Choice'
			drop_subscription(subs)
			
def add_subscription():
	sub = raw_input("User to subscribe:")
	s.sendto(subscribePre+user+':'+sub,(host,port));
	d = s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply[:len(subscribePre)+1] == '1'+subscribePre:
		print 'Successfully subscribed to ' + sub
	else:
		print 'Error: ' + sub + ' does not exist'

def edit_subscriptions():
	#print pleaseWait
	print_header('Edit Subscriptions')
	print '1: add subscription'
	print '2: drop subscription'
	print '3: cancel'
	choice=raw_input("Choice:")
	if choice == '1':
		add_subscription()
	elif choice == '2':
		s.sendto(subscriptionsPre+user,(host,port));
		d = s.recvfrom(1024)
		reply = d[0]
		addr = d[1]
		if reply[:len(subscriptionsPre)+1] == '1'+subscriptionsPre:
			drop_subscription(reply[len(subscriptionsPre)+1:])
		else:
			print 'failed:' +reply
	elif choice == '3':
		return
	else:
		print 'Invalid choice! Please try again.'
		edit_subscriptions();
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
	
	print_header('Menu')
	print 'Welcome ' + user + ' You have '+msgs+' unread messages.'
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
		print 'Invalid Response! Try again!'
		menu_disp()
	menu_disp()


def login_user():
	global user
	global passwd
	global loginPre
	global msgs

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
		menu_disp();
	else:
		print 'Login Failed! Please Re-try!'
		login_user()
	return

clear_screen();
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

