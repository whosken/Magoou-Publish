from utility import *
from utility.tools import *
from datetime import datetime, timedelta
import config

class Storage(CouchManager):
	DB = 'content_farm'
	
	def __init__(self):
		CouchManager.__init__(self,self.DB)
	
	def putFeed(self,feed):
		feed['datetime'] = formatDateTime(datetime.now())
		return self.putObject('feed',feed,id=feed['url'])
		
	def putEntry(self,entry):
		# remove unwanted fields
		for key in ('categories','highlight'):
			entry.pop(key,default=None)

		entry['datetime'] = formatDateTime(entry['datetime'])
		entry['summary'] = entry['summary'].replace('\'','"')
		return self.putObject('entry',entry,id=entry['url'],overwrite=False)
		
	def putProfile(self,profile):
		profile['datetime'] = formatDateTime(datetime.now())
		id = profile['username']+jsonify(profile['datetime'])
		return self.putObject('profile',profile,id=id)
		
	def putIssue(self,issue):
		issue['datetime'] = formatDateTime(datetime.now())
		id = issue['username']+jsonify(issue['datetime'])
		return self.putObject('issue',issue,id=id,overwrite=False)
		
	def putFeedback(self,feedback):
		feedback['datetime'] = formatDateTime(datetime.utcnow())
		id = feedback['profileid']+feedback['entryid']+jsonify(feedback['datetime'])
		return self.putObject('feedback',feedback,id=id,overwrite=False)
		
	def getOutOfDateObjects(self,object,age):
		timespan = timedelta(hours=age)
		end,_ = getTimeframe(span=timespan)
		view = '{0}?endkey={1}'.format(object,end)
		response = self.getOrPostObject(view=('datetime',view))
		return extractValues(response)
		
	def getUnparsedFeeds(self,age=config.FEEDAGE):
		return self.getOutOfDateObjects('feed',age)
		
	def getUnprocessedProfiles(self,age=config.ISSUEAGE):
		return self.getOutOfDateObjects('profile',age)
		
	def getUserObject(self,username,type):
		view = 'by_username?key={0}'.format(jsonify([username,type]))
		response = self.getOrPostObject(view=('document',view))
		return extractValues(response)
		
	def getUserIssues(self,username):
		return self.getUserObject(username,'issue')
		
	def getUserProfiles(self,username):
		return self.getUserObject(username,'profile')
		
	def getUserFeedbacks(self,username):
		return self.getUserObject(username,'feedback')
		
	def getLatestObject(self,object,start,age):
		if start:
			start,end = _getTimeframe(start=start)
		else:
			timespan = timedelta(hours=age)
			start,end = getTimeframe(span=timespan)
		view = '{0}?startkey={1}&endkey={2}'.format(object,start,end)
		response = self.getOrPostObject(view=('datetime',view))
		return extractValues(response)
		
	def getLatestEntries(self,start=None,age=config.ISSUEAGE+config.FEEDAGE):
		return getLatestObject(self,'entry',start,age)
	
	def getLatestProfiles(self,start=None,age=config.ISSUEAGE):
		return getLatestObject(self,'profile',start,age)
	
	def getLatestIssues(self,start=None,age=config.ISSUEAGE):
		return getLatestObject(self,'issues',start,age)
	
	def getTermWeights(self,type=None,term=None):
		view = 'word_weight?group=true'
		if term:
			key = [term,type] if type else [term]
			view += '&key={0}'.format(key)
		response = self.getOrPostObject(view=('statistics',view))
		results = {}
		for row in response:
			if type and row['key'][1] != type:
				continue
			results[row['key'][0]] = row['value']
		return results
		
	def getKeywordWeights(self,word=None):
		return self.getTermWeights('entry',term=word)
		
	def getTopicWeights(self,topic=None):
		return self.getTermWeights('profile',term=topic)
	
	def deleteOldObjects(self,type,age):
		timespan = timedelta(hours=age)
		end,_ = getTimeframe(span=timespan)
		view = '{0}?endkey={1}'.format(type,end)
		response = self.getOrPostObject(view=('datetime',view))
		for row in response:
			result = row['value']
			self.deleteDocument(result['_id'],result['_rev'])
		return response
	
	def deleteOldEntries(self,age=config.ISSUEAGE*config.STORED):
		return self.deleteOldObjects('entry',age=age)
		
	def deleteOldIssues(self,age=config.ISSUEAGE*config.STORED):
		return self.deleteOldObjects('issue',age=age)
		
	def deleteTopicProfiles(self):
		view = 'by_object?key={0}'.format('profile')
		response = self.getOrPostObject(view=('document',view))
		for row in response:
			result = row['value']
			if 'model' in result and result['model']:
				self.deleteDocument(result['_id'],result['_rev'])
		return response
		
def test():
	info('commence testing!')
	Storage()
	info('finished testing!')

if __name__ == '__main__':
	test()