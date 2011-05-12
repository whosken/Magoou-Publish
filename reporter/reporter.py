from publish.util.threadManager import runThreads
from publish.util import *

def run(storage):
	runThreads(_runReport,storage.getUnparsedFeeds,storage)

def _runReport(feed,storage):
	bag = storage.getKeywordWeights()
	
	from feedReader import readFeed
	from keywordGenerator import generateKeywords
	from entryScraper import scrapeEntry
	
	feed_keywords = feed['keywords'] if 'keywords' in feed else None
	for entry, need_scrape in readFeed(feed):
		if storage.checkDocumentExistence(None,key=entry['url']):
			continue
		if need_scrape:
			scrapeEntry(entry)
		entry['keywords'] = generateKeywords(entry,bag=bag,keywords=feed_keywords)
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
	from util.storage import Storage
	with Storage() as content:
		run(content)
	logMessage(__name__,'finished testing!')

if __name__ == '__main__':
	test()