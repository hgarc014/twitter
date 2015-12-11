import socket
import sys
import time
import signal
import json
import os
import hashlib

class Message(object):
	
	def __init__(self, message,hashTags,userName):
		self.message=message
		self.hashTags=hashTags
		self.userName=userName
		self.isRead=False
		self.postTime=time.time()
		
	#~ def __init__(self, message,hashTags,userName,postTime):
		#~ self.message=message
		#~ self.hashTags=hashTags
		#~ self.userName=userName
		#~ self.postTime=postTime
		#~ self.isRead=False
		
		

class User(object):

	def __init__(self, userName, passwd,isAdmin):
		self.userName=userName
		self.passwd=passwd
		self.isAdmin=isAdmin
		self.messages=[]
		self.subscriptions=[]
		self.followers=[]
		self.connection=''
		self.isLogin=False
		
	#~ def __init__(self, userName, passwd,isAdmin,messages,subscriptions,followers):
		#~ self.userName=userName
		#~ self.passwd=passwd
		#~ self.isAdmin=isAdmin
		#~ self.messages=messages
		#~ self.subscriptions=subscriptions
		#~ self.followers=followers
		#~ self.connection=''
		#~ self.isLogin=False


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

class FUNCTION:
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
