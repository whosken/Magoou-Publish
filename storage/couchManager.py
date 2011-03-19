import hashlib
import json
from urllib2 import *
from datetime import datetime, timedelta
from util import *

SERVER = '127.0.0.1'
PORT = '5984'

CONTENTDB = 'content_farm'
USERDB = 'user_vault'

FEEDAGE = 12 # hours = 1 days
ISSUEAGE = 168 # hours = 7 days
ISSUESSTORED = 12 # save latest issues, ~3 months

TIMEOUT = 10 # secs = 1/6 minutes

class CouchManager:
	def __init__(self,db):
		self._db = db
		self._connect = build_opener(HTTPHandler)
		
	def __enter__(self):
		return self
		
	def __exit__(self,type,value,traceback):
		self._connect.close()

	def _request(self,path,method='GET',data=None):
		try:
			path = self._db + '/' + path.replace(' ','%20')
			
			request = Request('http://{0}:{1}/{2}'.format(SERVER,PORT,path))
			request.get_method = lambda:method
			request.add_header('Content-Type','application/json')
			
			if data:
				request.add_data(data)

			logMessage(__name__,request.get_full_url())
			response = self._connect.open(request,timeout=TIMEOUT)
			
			if method == 'HEAD':
				return response.info()
			return _checkResponse(response)
		except:
			logMessage(__name__,request.get_full_url())
			logError(__name__)
			return None
		
	def _putObject(self,type,object,id=None,overwrite=True):
		if id:
			rev = self.checkDocumentExistence(id)
			if rev:
				if overwrite:
					object['_rev'] = rev
				else:
					return
		
		if 'highlight' in object:
			object.pop('highlight')
		object['object'] = type
		data = tools.jsonify(object)
		return self._request(id,'PUT',data)
		
	def _getOrPostObject(self,id=None,view=None,post=None):
		if view:
			path = '_design/{0}/_view/{1}'.format(view[0],view[1])
			return self._request(path,data=post)['rows']
		elif id:
			return self._request(id)
	
	def _deleteDocument(self,id,rev):
		return self._request('{0}?rev={1}'.format(id,rev),method='DELETE')
			
	def checkDocumentExistence(self,id=None,key=None):
		if key:
			id = _getId(key)
		try:
			return self._request(id,method='HEAD').getheader('Etag').replace('"','') # revision
		except:
			return None
	
	def getDocument(self,docId):
		return _cleanValue(self._getOrPostObject(id=docId))
	
	def compact(self):
		return self._request('_compact',method='POST')

class ContentManager(CouchManager):
	def __init__(self):
		CouchManager.__init__(self,CONTENTDB)
	
	def putFeed(self,feed):
		id = _getId(feed['url'])
		feed['datetime'] = _formatDatetime(datetime.now())
		return self._putObject('feed',feed,id)
		
	def putEntry(self,entry):
		#remove unwanted fields
		for key in ('categories','highlight'):
			if key in entry:
				entry.pop(key)

		id = _getId(entry['url'])
		entry['datetime'] = _formatDatetime(entry['datetime'])
		entry['summary'] = entry['summary'].replace('\'','"')
		return self._putObject('entry',entry,id,overwrite=False)
		
	def putShop(self,shop):
		id = _getId(shop['shopname']+shop['market'])
		shop['summary'] = shop['summary'].replace('\'','"')
		return self._putObject('shop',shop,id)
		
	def getUnparsedFeeds(self,age=FEEDAGE):
		# get feeds older than [refresh] hours
		timespan = timedelta(hours=age)
		end,_ = _getTimeframe(span=timespan)
		view = 'feed?endkey={0}'.format(end)
		response = self._getOrPostObject(view=('datetime',view))
		return _extractValues(response)
		
	def getEntriesWithKeywords(self,words,start=None,age=ISSUEAGE+FEEDAGE):
		query = set(words)
		if start:
			start,end = _getTimeframe(start=start)
		else:
			timespan = timedelta(hours=age)
			start,end = _getTimeframe(span=timespan)
		view = 'entry?startkey={0}&endkey={1}'.format(start,end)
		response = self._getOrPostObject(view=('datetime',view))
		
		results = {}
		for row in response:
			result = row['value']
			keywords = set(result['keywords'].keys())
			if not query.isdisjoint(keywords):
				results[result['_id']] = result['keywords']
		return results
		
	def getShopsWithKeywords(self,location,words):
		query = set(words)
		start,end = _getTimeframe(span=timespan)
		view = 'by_location?key='+tools.jsonify([location,'shop'])
		response = self._getOrPostObject(view=('documebnt',view))
		
		results = {}
		for row in response:
			result = row['value']
			keywords = set(result['keywords'].keys())
			if not query.isdisjoint(keywords):
				 results[result['_id']] = result['keywords']
		return results
	
	def deleteOldEntries(self,age=ISSUEAGE*ISSUESSTORED):
		# delete entries that are too old
		timespan = timedelta(hours=age)
		end,_ = _getTimeframe(span=timespan)
		view = 'entry?endkey={0}'.format(end)
		response = self._getOrPostObject(view=('datetime',view))
		for row in response:
			result = row['value']
			self._deleteDocument(result['_id'],result['_rev'])
		return response
	
class UserManager(CouchManager):
	def __init__(self):
		CouchManager.__init__(self,USERDB)
		
	def putUser(self,user):
		id = _getId(user['username'])
		user['datetime'] = _formatDatetime(datetime.now())
		return self._putObject('user',user,id)
		
	def putIssue(self,issue):
		issue['datetime'] = _formatDatetime(datetime.now())
		id = _getId(issue['username']+tools.jsonify(issue['datetime']))
		return self._putObject('issue',issue,id,overwrite=False)
	
	def putUsage(self,usage):
		usage['datetime'] = _formatDatetime(datetime.utcnow())
		idString = usage['username']+usage['entryid']+tools.jsonify(usage['datetime'])
		id = _getId(idString)
		return self._putObject('usage',usage,id,overwrite=False)
		
	def putSession(self,session,logout=False):
		if not '_id' in session: # login
			session['login'] = _formatDatetime(datetime.now())
			id = _getId(session['username']+tools.jsonify(session['login']))
		elif logout: # logout
			id = session['_id']
			session['logout'] = _formatDatetime(datetime.now())
		self._putObject('session',session,id)
		return id
		
	def authenticateUser(self,username,hash):
		view = 'authenticate?limit=1'
		login = {'keys':[username,hash]}
		try:
			response = self._getOrPostObject(view=('security',view),post=login)
			return _extractValues(response).next()
		except:
			return None
			
	def getUninformedUsers(self,age=ISSUEAGE):
		# get users whose last update is over [refresh] hours
		timespan = timedelta(hours=age)
		end,_ = _getTimeframe(timespan)
		view = 'user?endkey={0}'.format(end)
		response = self._getOrPostObject(view=('datetime',view))
		return _extractValues(response)
	
	def getUsersWithPreferences(self,prefers):
		pass
	
	def getUserIssues(self,username):
		view = 'by_username?key={0}'.format(tools.jsonify([username,'user']))
		response = self._getOrPostObject(view=('document',view))
		return _extractValues(response)
		
	def getPublicIssues(self,username=None):
		if username:
			view = 'by_public?key={0}'.format(tools.jsonify([True,username,'isue']))
		else:
			view = 'by_public?key=true&group_level=1'
		response = self._getOrPostObject(view=('document',view))
		return _extractValues(response)
		
	def getUserUsage(self,username):
		view = 'by_username?key={0}'.format(tools.jsonify([username,'usage']))
		response = self._getOrPostObject(view=('document',view))
		return _extractValues(response)

	def getEntryUsage(self,id):
		view = 'entry_score?key='+tools.jsonify(id)
		response = self._getOrPostObject(view=('statistics',view))
		return _extractValues(response)
		
	def deleteOldIssues(self,age=ISSUEAGE*ISSUESSTORED):
		# delete issues that are too old
		timespan = timedelta(hours=age)
		end,_ = _getTimeframe(span=timespan)
		view = 'issue?endkey={0}'.format(end)
		response = self._getOrPostObject(view=('datetime',view))
		for row in response:
			result = row['value']
			self._deleteDocument(result['_id'],result['_rev'])
		return response
		
def _getId(value):
	return hashlib.md5(value).hexdigest()
	
def _extractValues(response,type=None):
	for row in response:
		data = row['value']
		if type and data['object'] != type:
			continue
		yield _cleanValue(data)

def _cleanValue(data):
	if 'datetime' in data:
		data['datetime'] = _jsonToDatetime(data['datetime'])
	if 'password' in data: data.pop('password')
	if 'hash' in data: data.pop('hash')
	return data
		
def _getTimeframe(span=None,start=None,end=None):
	if not end:
		end = datetime.now()
	if (not start) and span:
		start = end - span
	elif start and span:
		end = start + span
	return _formatDatetime(start), _formatDatetime(end)
	
def _formatDatetime(dt):
	if isinstance(dt,datetime):
		return [dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second]
	elif type(dt) is list:
		return dt
	
def _jsonToDatetime(list):
	args = {
			'year':list[0],
			'month':list[1],
			'day':list[2],
			'hour':list[3],
			'minute':list[4],
			'second':list[5],
		}
	return datetime(**args)
	
def _checkResponse(response):
	responseJson = json.loads(response.read())
	if 'error' in responseJson:
		raise Exception('{0}:{1}'.format(responseJson['error'],responseJson['reason']))
	return responseJson