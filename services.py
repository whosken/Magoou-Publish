from reporter import reporter
from editor import editor
from util import *
from util.storage import Storage
from datetime import datetime

"""
Enums
"""
feedTypes = ['publication','official','personal','media','hub']
actions = config.FEEDBACKSCORES.keys()

"""
POST functions
"""
def report():
	with Storage() as storage:
		reporter.run(storage)

def edit():
	with Storage() as storage:
		editor.run(storage)

def clean(object='all'):
	with Storage() as storage:
		if object == 'all':
			storage.deleteOldEntries()
			storage.deleteOldIssues()
			storage.deleteTopicProfiles()
			storage.compact()
		elif object == 'entry':
			storage.deleteOldEntries()
		elif object == 'issue':
			storage.deleteOldIssues()
		elif object == 'model':
			storage.deleteTopicProfiles()
		
def modelTopics():
	with Storage() as storage:
		return editor.modelTopics(storage)

"""
GET functions
"""
def getDocument(id,object=None):
	with Storage() as storage:
		doc = storage.getDocument(id)
		if doc and object and doc['object'] != object:
			return None
		return doc
	
def getIssues(username):
	with Storage() as storage:
		for issue in storage.getUserIssues(username):
			yield issue
			# yield {
					# 'datetime':issue['datetime'],
					# 'docs':list({'weight':weight,'doc':storage.getDocument(id)} for id,weight in issue['entries']),
				# }
	
def getKeywords(feeds=None,urls=None,string=None):
	keywords = {}
	if feeds:
		for feed in feeds:
			doc = getDocument(feed['url'])
			doc = doc or putFeed(feed,'article')
			tools.mergeDicts(keywords,doc['keywords'])
	if urls:
		for url in urls:
			tools.mergeDicts(keywords,reporter.getObjectKeywords(url=url))
	if string:
		tools.mergeDicts(keywords,reporter.getObjectKeywords(text=string))
	return keywords

"""
PUT functions
"""
def putFeed(url,type,aboutUrl=None,aboutText=None,icon=None):
	feed = {
			'url':url,
			'type':type,
		}
	feed['keywords'] = getKeywords(urls=[aboutUrl] if aboutUrl else [],string=aboutText)
	if icon:
		feed['icon'] = icon
	with Storage() as storage:
		return storage.putFeed(feed)
	
def putProfile(username,topics=None,samples=None,feeds=None,words=None):
	if not topics:
		topics = {}
	if samples:
		for sample in samples:
			keywords = getKeywords(urls=sample)
			tools.mergeDicts(topics,keywords)
	if feeds:
		for feed in feeds:
			keywords = getKeywords(feed=feed)
			tools.mergeDicts(topics,keywords)
	if words:
		word_dict = tools.completeDict(topics,words,1.0/float(len(words)))
		
	profile = {
			'username':username,
			'topics':topics,
		}
	with Storage() as storage:
		result = storage.putProfile(profile)
		editor.runEdit(profile,storage)
		return result
	
def putFeedback(profileId,entryId,action):
	with Storage() as storage:
		if not storage.checkDocumentExistence(id=entryId):
			storage = {
					'profileid':profileId,
					'entryid':entryId,
					'action':action,
				}
			return storage.putFeedback(feedback);
