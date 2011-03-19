from storage import *
from editor import editor
from reporter import reporter

from hashlib import sha256
from datetime import datetime

from util import *
from util import config2

"""
authentication functions
"""
def authenticate(username,password):
	hash = sha256(password).hexdigest()
	with UserManager as storage:
		return storage.authenticateUser(username,hash)
	
def login(username):
	logout(username)
	# start new session
	with UserManager as storage:
		session = {'username':username}
		return storage.putSession(session)
	
def logout(cookie):
	with UserManager as storage:
		session = storage.getDocument(cookie)
		if session:
			return storage.putSession(session,logout=True)
	
def checkSession(username,cookie):
	session = getVaultDoc(id=cookie)
	if session and session['username'] == username and 'logout' not in session:
		return session

def updateSession(username,cookie,action):
	session = checkSession(username,cookie)
	if session:
		if action not in ('logout',''):
			session[action] = datetime.now()
			with UserManager as storage:
				return storage.putSession(session)
		return logout(cookie)

"""
control functions
"""
def report():
	with ContentManager() as storage:
		reporter.run(storage)

def edit():
	with UserManager() as users, ContentManager() as contents:
		editor.run(users,contents)

def clean():
	with UserManager() as users, ContentManager() as contents:
		users.deleteOldIssues()
		contents.deleteOldEntries()
		users.compact()
		contents.compact()

"""
GET functions
"""
def getFarmDoc(id=None,key=None):
	with ContentManager as storage:
		return storage.getDocument(id=id,key=key)

def getVaultDoc(id=None,key=None):
	with UserManager as storage:
		return storage.getDocument(id=id,key=key)

def getIssues(username=None,public=False):
	with UserManager() as storage:
		if username and not Public:
			issues = storage.getUserIssues(username)
		else:
			issues = storage.getPublicIssues(username)
	
	def retrieveEntries(issue):
		for id,weight in issue['entries']:
			yield weight, storage.getDocument(id)
	
	with ContentManager as storage:
		for issue in issues:
			yield issue['datetime'], list((weight,entry) for weight,entry in retrieveEntries(issue))
	
def getShops(location,entryId):
	with ContentManager() as contents:
		keywords = contents.getDocument(entryId)['keywords']
		shops = contents.getShopsWithKeywords(location,keywords.keys())
		if len(shops) < config2.MINSHOPS:
			shops += contents.getShopsWithKeywords('online',keywords.keys())
	if len(shops) < config2.MINSHOPS:
		pass # TODO: talk to yelp api to get the rest
	return editor.selectCandidates(keywords,shops)
	
def getKeywords(urls=None,string=None):
	pass

"""
PUT functions
"""
def addFeed(feedUrl,feedType,aboutUrl=None,icon=None):
	feed = {
			'url':feedUrl,
			'type':feedType,
		}
	if aboutUrl:
		reporter.profileFeed(feed,aboutUrl)
	if icon:
		feed['icon'] = icon
	with ContentManager() as storage:
		storage.putFeed(feed)
	return feed
	
def addShop(shopname,type,location,address,summary=None,aboutUrl=None):
	shop = {
			'shopname':shopname,
			'address':address,
			'location':location, # city/town name, or online
			'keywords':{},
		}
	reporter.profileShop(shop,summary,aboutUrl)
	with ContentManager as storage:
		return storage.putShop(shop)
	
def addUser(username,password,email,location,preferences,update=False):
	if not update:
		with UserManager as users:
			if checkDocumentExistence(key=username):
				return None
	
	from hashlib import sha256
	hash = sha256(password).hexdigest()
	user = {
			'username':username,
			'password':hash,
			'email':email,
			'location':location,
			'preferences':preferences,
		}
	with ContentManager() as contents:
		runEdit(user,users,contents)
	with UserManager as users:
		return users.putUser(user)
	
def addUsage(username,entryId,action):
	with UserManager() as users, ContentManager() as contents:
		if not contents.checkDocumentExistence(id=entryId):
			usage = {
					'username':username,
					'entryid':entryId,
					'action':action,
				}
			users.putUsage(usage)
			return usage

def publishIssue(id,publish=True):
	with UserManager as storage:
		issue = storage.getDocument(id)
		issue['public'] = publish
		storage.putIssue(issue)