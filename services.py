from reporter import reporter
from editor import editor
from util import *
from util.storage import Storage
from datetime import datetime

"""
Enums
"""
feedTypes = ['publication','official','personal','media','hub'] # TODO: move to publish
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

def clean():
	with Storage() as storage:
		storage.deleteOldIssues()
		storage.deleteOldEntries()
		storage.compact()

"""
GET functions
"""
def getDocument(id,object=None):
	with Storage() as storage:
		doc = storage.getDocument(id)
		if object and doc['object'] != object:
			return None
		return doc
	
def getIssues(username):
	with Storage() as storage:
		def get_docs(issue):
			for id,weight in issue['entries']:
				yield {
						'weight':weight,
						'doc':storage.getDocument(id),
					}
		
		for issue in storage.getUserIssues(username):
			yield {
					'datetime':issue['datetime'],
					'docs':list(get_docs(issue)),
				}
	
def getKeywords(feeds=None,urls=None,string=None):
	keywords = {}
	if feeds:
		for feed in feeds:
			doc = getDocument(feed['url'])
			doc = doc or putFeed(feed,'article')
			tools.mergeDict(keywords,doc['keywords'])
	if urls:
		for url in urls:
			tools.mergeDict(keywords,reporter.getObjectKeywords(url=url))
	if string:
		tools.mergeDict(keywords,reporter.getObjectKeywords(text=string))
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
	print feed
	with Storage() as storage:
		storage.putFeed(feed)
	return feed
	
def putProfile(username,topics=None,samples=None,feeds=None,words=None):
	if not topics:
		topics = {}
	if samples:
		for sample in samples:
			keywords = getKeywords(urls=sample)
			tools.mergeDict(topics,keywords)
	if feeds:
		for feed in feeds:
			keywords = getKeywords(feed=feed)
			tools.mergeDict(topics,keywords)
	if words:
		word_dict = tools.completeDict(topics,words,1.0/float(len(words)))
		
	profile = {
			'username':username,
			'topics':topics,
		}
	with Storage() as storage:
		storage.putProfile(profile)
		editor.runEdit(profile,storage)
		return storage
	
def putFeedback(profileId,entryId,action):
	with Storage() as storage:
		if not storage.checkDocumentExistence(id=entryId):
			storage = {
					'profileid':profileId,
					'entryid':entryId,
					'action':action,
				}
			storage.putFeedback(feedback);
			return feedback