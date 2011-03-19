from threading import Thread
from util import *

def run(storage):
	try:
		def startThread(request,storage):
			thread = Thread(target=_runReport,args=(request,storage,))
			thread.start()
			return thread
		
		threads = []
		for feed in storage.getUnparsedFeeds():
			threads.append(startThread(feed,storage))
			storage.putFeed(feed)
			if len(threads) > config.THREADLIMIT:
				break
		
		for thread in threads:
			thread.join()
	except:
		logError(__name__)

def _runReport(feed,storage):
	from feedReader import readFeed
	from keywordGenerator import generateKeywords
	from entryScraper import scrapeEntry
	
	feedKeywords = feed['keywords'] if 'keywords' in feed else None
	for entry, needScrape in readFeed(feed):
		if storage.checkDocumentExistence(None,key=entry['url']):
			continue
		if needScrape:
			scrapeEntry(entry)
		entry['keywords'] = generateKeywords(entry,feedKeywords)
		storage.putEntry(entry)
		
def profileFeed(feed,aboutUrl):
	from keywordGenerator import generateKeywords
	from entryScraper import scrapeEntry
	mock = scrapeEntry({'url':aboutUrl,'type':'article'})
	feed['keywords'] = generateKeywords(mock)
	return feed
	
def profileShop(shop,summary,aboutUrl):
	if summary:
		shop['summary'] = summary
		mock = shop
	elif aboutUrl:
		from entryScraper import scrapeEntry
		mock = scrapeEntry({'url':aboutUrl,'type':'article'},raw)
	from keywordGenerator import generateKeywords
	shop['keywords'] = generateKeywords(mock)
	return shop
		
def test():
	logMessage(__name__,'commence testing!')
	# testFeed = {
				# 'url':'http://www.creativeboom.co.uk/feed/',
				# 'type':1
			# }
	# from storage.managers import ContentManager
	# with ContentManager() as storage:
		# storage.putFeed(testFeed)
	# logMessage(__name__,'done creating mock feed!')
	
	run()
	logMessage(__name__,'finished testing!')

if __name__ == '__main__':
	test()