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
			if len(threads) > config.THREADLIMIT:
				break
		
		for thread in threads:
			thread.join()
	except:
		logError(__name__)

def _runReport(feed,storage):
	bag = storage.getKeywordWeights()
	
	from feedReader import readFeed
	from keywordGenerator import generateKeywords
	from entryScraper import scrapeEntry
	
	feedKeywords = feed['keywords'] if 'keywords' in feed else None
	for entry, needScrape in readFeed(feed):
		if storage.checkDocumentExistence(None,key=entry['url']):
			continue
		if needScrape:
			scrapeEntry(entry)
		entry['keywords'] = generateKeywords(entry,bag=bag,keywords=feedKeywords)
		storage.putEntry(entry)
	storage.putFeed(feed)
	
def profileObject(text=None,url=None):
	if text:
		mock = {'url':text[:20],'type':'article','summary':text}
	elif url:
		from entryScraper import scrapeEntry
		mock = scrapeEntry({'url':url,'type':'article'})
	from keywordGenerator import generateKeywords
	return generateKeywords(mock)
	
def test():
	logMessage(__name__,'commence testing!')
	from storage.couchManager import ContentManager
	with ContentManager() as content:
		run(content)
	logMessage(__name__,'finished testing!')

if __name__ == '__main__':
	test()