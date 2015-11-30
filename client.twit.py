
#socket client exmaple

import socket
import sys
import time
import os
import json
import getpass
from thread import *
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


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

pleaseWait='\nPlease do not use this function it is under construction, thanks!\n'
user=''
passwd=''
isAdmin=''
msgcnt=''

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
adminPre='admin='
followersPre='followers='

strline=color.BOLD+'\n-----------------------------------------------'+color.END

def get_followers():
	global followersPre
	s.sendto(followersPre+user,(host,port))
	d = s.recvfrom(1024)
	reply = d[0]
	if reply[:len(followersPre)+1] == '1'+followersPre:
		data = reply[len(followersPre)+1:]
		myj=json.loads(data)
		print_header('Followers')
		i=1
		for name in myj:
			print str(i)+':'+name
			i+=1
		if i == 1:
			print 'You have no followers'
		wait_enter()

def update_msg_count():
	global msgcnt
	us.sendto(userMsgPre+user,(host,port))
	d=us.recvfrom(1024)
	reply = d[0]
	if reply[:len(userMsgPre)+1] == '1'+userMsgPre and msgcnt != reply[len(userMsgPre)+1:]:
		msgcnt = reply[len(userMsgPre)+1:]
		return True
	else:
		return False

def updateThread(name,empty):
	global msgcnt
	try:
		us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		us.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		while 1:
			if len(user) > 0:
				us.sendto(userMsgPre+user,(host,port))
				d=us.recvfrom(1024)
				reply = d[0]
				if reply[:len(userMsgPre)+1] == '1'+userMsgPre and msgcnt != reply[len(userMsgPre)+1:]:
					oldcnt=msgcnt
					msgcnt = reply[len(userMsgPre)+1:]
					if oldcnt < msgcnt:
						print_messages()
				time.sleep(1)
				#~ else:
					#~ print 'msgcnt wansnt updated'
			else:
				break
		us.close()
	except socket.error, msg:
		print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
		sys.exit();

def return_json(obj):
	return json.dumps(obj, default=lambda o: o.__dict__)

def clear_screen():
	#time.sleep(.5)
	unused_var=os.system('clear')
	
def print_header(menu):
	clear_screen()
	print color.GREEN + '\n====== ' + menu + ' ======\n' +color.END

def print_messages():
	print color.BOLD + '\nYou have '+msgcnt+' unread messages.' + color.END

def wait_enter():
	nothin=raw_input(color.GREEN + "\nPress <Enter> to continue" + color.END)

def check_plural(val):
	if int(val) == 1:
		return ''
	return 's'

def get_current_time(old):
	seconds=time.time() - old
	multi=check_plural(seconds)
	if seconds < 60:
		return str(int(seconds)) + ' second'+multi+' ago'
	minutes = seconds / 60
	multi=check_plural(minutes)
	if minutes < 60:
		return str(int(minutes)) + ' minute'+multi+' ago'
	hours = minutes / 60
	multi=check_plural(hours)
	if hours < 24:
		return str(int(hours)) + ' hour'+multi+' ago'
	days = hours / 24
	multi=check_plural(days)
	if days < 365:
		return str(int(days)) + ' day'+multi+' ago'
	years = days/365
	multi=check_plural(years)
	return str(int(years)) + ' year'+multi+' ago'
	
	

def print_tweets(tweets,emptymsg):
	print strline
	if len(tweets) > 0:
		for message in tweets:
			if not message['isRead']:
				print color.BOLD
				print_tweet(message)
				print color.END
			else:
				print_tweet(message)
			print strline
	else:
		print color.YELLOW + '\n'+emptymsg + color.END
		print strline

def print_tweet(message):
	timeago=get_current_time(message['postTime'])
	print '\n@' +message['username'] + '\t'+ timeago
	if len(message['hashtags']) > 0:
		print '#' + '#'.join(message['hashtags'])
	if len(message['message']) > 0:
		print message['message']

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
		print_tweets(myj,'No new messages')
		wait_enter()
	return


def choose_offline_by_user(subs):
	subscriptions = json.loads(subs)
	i = print_subscriptions(subs,'Show offline messages from user')
	if not i or i == 0:
		wait_enter()
		return
	choice=raw_input("Choice:")
	try:
		choice = int(choice)
	except ValueError:
		pass
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
			print_tweets(myj,'No new messages from '+subscriptions[choice-1])
			wait_enter()
		else:
			print 'something bad happened'
	else:
		choose_offline_by_user(subs)

def get_offline_by_user():
	global offlineUserPre
	s.sendto(subscriptionsPre+user,(host,port));
	d = s.recvfrom(1024)
	reply = d[0]
	addr = d[1]
	if reply[:len(subscriptionsPre)+1] == '1'+subscriptionsPre:
		subs = reply[len(subscriptionsPre)+1:]
		choose_offline_by_user(subs)


#offline messages
#displays messages that were displayed when user was offline
#has option to display all or only from a subscription
#when user logs out these messages should be removed
def offline_message():
	global offlinePre
	print_header('Offline Messages')
	print '1: see all messages'
	print '2: see messages from a user'
	print '3: Cancel'
	choice = raw_input('choice:')
	if choice == '1':
		get_offline_messages()
	elif choice == '2':
		get_offline_by_user()
	elif choice == '3':
		return
	else:
		offline_message()
	return

def print_subscriptions(subs,header):
	print_header(header)
	#subscriptions=subs.split(':')
	subscriptions = json.loads(subs)
	if len(subscriptions) == 0:
		print color.YELLOW + 'You have no subscriptions'+ color.END
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
				wait_enter()
			else:
				print 'Error occured for unsubscribing to ' + subscriptions[choice-1]
		else:
			drop_subscription(subs)
	else:
		wait_enter()
			
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
		print 'user "' + sub + '" does not exist'
	wait_enter()

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
		edit_subscriptions();
	return

def post_message():
	#print pleaseWait
	global postPre
	message=raw_input("Message (no hashtags):")
	hashtags=raw_input("HashTags (separated by '#'):")
	if len(message)+len(hashtags) > 140:
		print 'Your message + hashtags was ' + str(len(message) + len(hashtags)) + ', which is larger than the allowed 140. \nPlease try again!'
		wait_enter()
		return post_message()
	elif len(message) + len(hashtags) == 0:
		print 'Your message + hashtags was ' + str(len(message) + len(hashtags)) + ', which is not a valid message. \nPlease try again!'
		wait_enter()
		return post_message()
	
	if '"' in message:
		message = message.replace('"','\\"')
	if '"' in hashtags:
		hashtags = hashtags.replace('"','\\"')
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
		wait_enter()
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
			print_tweets(myj,'No results found for #'+'#'.join(hashtags))
			wait_enter()
		else:
			print_header('Results for #' + '#'.join(hashtags))
			#print 'Results for #' + '#'.join(hashtags)
			print_tweets(myj,'No results found for #'+'#'.join(hashtags))
			wait_enter()
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
		user=''
		passwd=''
		wait_enter()
	else:
		print 'WARNING: error occured'
		return logout_user()
	#TODO: tell server you logged out
	login_user();
	return

def admin_options():
	global adminPre
	print_header("Admin Commands")
	command=raw_input("command:")
	myj=''
	if command == 'newuser':
		newuser=raw_input('new username:')
		newpass=raw_input('new user passwd:')
		newIsAdmin=raw_input('is user admin (T/F):')
		myj='{"user":"'+user+'","command":"'+command+'","newuser":"'+newuser+'","passwd":"'+newpass+'","isAdmin":"'+newIsAdmin+'"}'
	else:
		myj='{"user":"'+user+'","command":"'+command+'"}'
	s.sendto(adminPre+myj,(host,port))
	d=s.recvfrom(1024)
	reply=d[0]
	if reply[:len(adminPre)+1] == '1'+adminPre:
		res = reply[len(adminPre)+1:]
		print res
	else:
		print 'You do not have admin privilege'
	wait_enter()
	

def menu_disp():
	global msgcnt
	if not msgcnt:
		msgcnt='0'
		print 'not initialized'
	print_header('Menu')
	print 'Welcome ' + color.GREEN+ user+color.END + ' You have '+msgcnt+' unread messages.\n'
	if isAdmin:
		print '0: Admin'
	print '1: Messages'
	print '2: Edit Subscriptions'
	print '3: Post a Message'
	print '4: Hashtag Search'
	print '5: Followers'
	print '6: Logout'
	
	choice=raw_input("Choice:")
	
	if isAdmin and choice == '0':
		admin_options()
	elif choice == '1':
		offline_message();
	elif choice =='2':
		edit_subscriptions();
	elif choice == '3':
		post_message();
	elif choice == '4':
		hashtag_search();
	elif choice == '5':
		get_followers()
	elif choice == '6':
		logout_user();
	else:
		print 'Invalid Response! Try again!'
		menu_disp()
	menu_disp()


def login_user():
	global user
	global passwd
	global loginPre
	global isAdmin

	clear_screen();
	euser='Username:'
	epass='Password:'
	
	user=raw_input(euser)
	passwd=getpass.getpass(epass)
	
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
		data = reply[len(loginPre)+1:]
		myj = json.loads(data)
		isAdmin=myj["isAdmin"]
		start_new_thread(updateThread,(user,''))
		menu_disp();
	else:
		print color.YELLOW+'Login Failed! Please Re-try!'+color.END
		wait_enter()
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

