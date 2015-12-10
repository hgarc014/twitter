import socket
import sys
import time
import signal
import json
import os
import hashlib

class Message(object):
	
	def __init__(self, message,hashtags,username):
		self.message=message
		self.hashtags=hashtags
		self.username=username
		self.isRead=False
		self.postTime=time.time()

class User(object):
	

	def __init__(self, userName, passwd,isAdmin):
		self.userName=userName
		self.passwd=passwd
		self.messages=[]
		self.subscriptions=[]
		self.followers=[]
		self.isAdmin=isAdmin
		self.connection=''
		self.isLogin=False


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
