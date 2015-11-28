
#socket client exmaple

import socket
import sys
import time
import os
import json
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
subscriptionsPre='subscriptions='
subscribeDropPre='subscribeDrop='
offlinePre='offline='
offlineUserPre='offlineUser='
postPre='post='
searchPre='search='
userMsgPre='msgcnt='

strline='\n-----------------------------------------------'

def return_json(obj):
	return json.dumps(obj, default=lambda o: o.__dict__)

def clear_screen():
	#time.sleep(.5)
	unused_var=os.system('clear')
	
def print_header(menu):
	#clear_screen()
	print '\n====== ' + menu + ' ======\n'

def print_tweets(tweets):
	print strline
	for message in tweets:
		#print message
		print_tweet(message)
	print strline

def print_tweet(message):
	#print '\n-----------------------------------------------'
	print '\n@' +message['username']
	if len(message['hashtags']) > 0:
		print '#' + '#'.join(message['hashtags'])
	if len(message['message']) > 0:
		print message['message']
	#print '\n-----------------------------------------------'

#------------------
#while user logged in make sure to display real time message sent by any subscriptions
#-----------------

def get_offline_messages():
	global offlinePre
	s.sendto(offlinePre+user,(host,port))
	d=s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply [:len(offlinePre)+1] == '1' + offlinePre:
		msgs= reply[len(offlinePre)+1:]
		print_header("Messages")
		myj=json.loads(msgs)
		print_tweets(myj)
	return


def get_offline_by_user():
	global offlineUserPre
	s.sendto(subscriptionsPre+user,(host,port));
	d = s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply[:len(subscriptionsPre)+1] == '1'+subscriptionsPre:
		subs = reply[len(subscriptionsPre)+1:]
		subscriptions = json.loads(subs)
		i = print_subscriptions(subs,'Show offline messages from user')
		if not i or i == 0:
			return
		choice=raw_input("Choice:")
		try:
			choice = int(choice)
		except ValueError:
			donothing=''
		if type(choice) ==int and choice >= 1 and choice <= i:
			if choice == i:
				return	
			#print 'sending:'+offlineUserPre+user+':'+subscriptions[choice-1]
			s.sendto(offlineUserPre+user+':'+subscriptions[choice-1],(host,port))
			d = s.recvfrom(1024)
			reply = d[0]
			addr = d[1]
			if reply [:len(offlineUserPre)+1] == '1' + offlineUserPre:
				msgs = reply[len(offlineUserPre)+1:]
				print_header("Messages from " + subscriptions[choice-1])
				myj = json.loads(msgs)
				print_tweets(myj)
			else:
				print 'something bad happened'
		else:
			print 'Invalid choice. Please Try again'
			get_offline_by_user()


#offline messages
#displays messages that were displayed when user was offline
#has option to display all or only from a subscription
#when user logs out these messages should be removed
def offline_message():
	global offlinePre
	print_header('Offline Messages')
	print '1: see all offline messages'
	print '2: see offline messages from user'
	choice = raw_input('choice:')
	if choice == '1':
		get_offline_messages()
	elif choice == '2':
		get_offline_by_user()
	else:
		print 'invalid choice. try again'
		offline_message()
	#print pleaseWait
	return

def print_subscriptions(subs,header):
	print_header(header)
	#subscriptions=subs.split(':')
	subscriptions = json.loads(subs)
	if len(subscriptions) == 0:
		print 'You have no subscriptions'
		return
	else:
		i=0
		for sub in subscriptions:
			i+=1
			print str(i) + ':' + sub
		i+=1
		print str(i) + ':cancel'
		return i;

#edit subscriptions
#allow user to add or drop a subscription (user)
#if drop only show current subscriptions
#if add ask for name and tell if user exists

def drop_subscription(subs):
	
#	print_header('Drop subscription')
	subscriptions = json.loads(subs)
	i = print_subscriptions(subs,'Drop subscription')
	if i and i !=0:
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
	myj = '{"username": "' + user + '", "sub" : "'+sub+'"}'
	s.sendto(subscribePre+myj,(host,port));
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
	#print pleaseWait
	global postPre
	message=raw_input("Message (no hashtags):")
	hashtags=raw_input("HashTags (separated by '#'):")
	if len(message)+len(hashtags) > 140:
		print 'Your message + hashtags was ' + str(len(message) + len(hashtags)) + ', which is larger than the allowed 140. \nPlease try again!'
		return post_message()
	
	if '"' in message:
		message = message.replace('"','\\"')
	#if "'" in message:
	#	message = message.replace("'","\\'")
	#	print 'replaced='+message
	if '"' in hashtags:
		hashtags = hashtags.replace('"','\\"')
	#if "'" in hashtags:
	#	hashtags = hashtags.replace("'","\\'")
	hashtags = hashtags.split('#')
	if '' in hashtags:
		hashtags=filter(None,hashtags)
	hashtags=return_json(hashtags)
	myj='{"username": "'+user+'", "message": "'+message+'", "hashtags": '+hashtags+'}'
	s.sendto(postPre+myj,(host,port))
	d = s.recvfrom(1024)
	reply = d[0]
	if reply [:len(postPre)+1] == '1' + postPre:
		print 'message sent successfully'
	else:
		print 'failed to post ' + reply
	return

#hashtag search
#user will see 10 tweets containing hashtag
def hashtag_search():
	global searchPre
	#print pleaseWait
	print_header('Search Hashtag')
	hashtags=raw_input("Search Hashtag:")
	hashtags = hashtags.split('#')
	if '' in hashtags:
		hashtags=filter(None,hashtags)
	s.sendto(searchPre+return_json(hashtags),(host,port))
	d = s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply[:len(searchPre)+1]=='1'+searchPre:
		msgs = reply[len(searchPre)+1:]
		myj=json.loads(msgs)
		if len(myj) == 0:
			print strline
			print '\nNo results found for #'+ '#'.join(hashtags)
			print strline
		else:
			print 'Results for #' + '#'.join(hashtags)
			print_tweets(myj)
	else:
		print 'something bad happened'
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
	s.sendto(userMsgPre+user,(host,port))
	d = s.recvfrom(1024)
	reply = d[0]
	msgcnt=''
	if reply[:len(userMsgPre)+1] == '1'+userMsgPre:
		msgcnt = reply[len(userMsgPre)+1:]
	elif not msgcnt:
		msgcnt='0'
		print 'not initialized'
	print_header('Menu')
	print 'Welcome ' + user + ' You have '+msgcnt+' unread messages.'
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

