import re
from datetime import *
import feedparser
from publish.util import *

def readFeed(feed):
	logMessage(__name__, 'reading ' + feed['url'])
	try:
		xml = feedparser.parse(feed['url'])
		return _traverseXml(feed,xml)
	except:
		logError(__name__)

def _traverseXml(feed,xml):
	for entry in xml.entries:
		# if feed is media or aggregator, scrape its entries
		needScrape = feed['type'] in ('media','hub')
		
		response = {
					'source':xml.feed.title,
					'type':'article', # assume entry is article
					'title':entry.title,
				}
		try:
			response['datetime'] = datetime(*entry.date_parsed[:6])
		except AttributeError:
			response['datetime'] = datetime.now()
				
		# parse url
		if not entry.link.count('feedproxy') > 0:
			response['url'] = entry.link
		else:
			response['url'] = entry.guid
		
		if 'language' in xml.feed:
			response['language'] = xml.feed.language[:2]
		if 'author_detail' in entry:
			response['author'] = entry.author_detail.name
		
		# parse summary
		summary = entry.description
		response['summary'] = tools.cleanText(summary)
		if response['summary'].count(' ') < config.SUMMARYSIZE:
			needScrape = True
		
		# catch favicon
		if 'icon' in feed:
			response['icon'] = feed['icon']
		
		# parse media
		def getMedia(media):
			t = 'article'
			if re.search('image',media.type):
				t = 'image'
			elif re.search('audio',media.type):
				t = 'audio'
			elif re.search('video',media.type):
				t = 'video'
			elif media.href.count('swf') > 0:
				t = 'rich'
			return t, media.href
		
		if len(entry.enclosures) > 0:
			media = entry.enclosures[0]
			response['type'], response['media'] = getMedia(media)
		elif len(entry.links) > 1:
			for link in entry.links:
				t, href = getMedia(link)
				if t != 'article':
					break
			response['type'], response['media'] = t, href
		
		# catch media that might be embedded in description
		if response['type'] == 'article' and re.search('img',summary) or re.search('object',summary):
			result = re.search('src="([^"]+(jpg|png|gif))"',summary)
			if result:
				response['type'] = 'image'
				response['media'] = result.group(1)
			else:
				result = re.search('\<object\s[^\w\W]+object\>',summary)
				if result:
					response['media'] = result.group(0)
				response['type'] = 'rich'
				
		if response['type'] != 'article' and 'media' in response:
			needScrape = True
		
		if 'categories' in entry:
			response['categories'] = [category if type(category) is unicode else category[1] for category in entry.categories]
		
		yield response, needScrape
	
def test():
	url = 'http://feeds.feedburner.com/bigthink/main?format=xml'
	# url = 'http://xkcd.com/atom.xml'
	request = {
				'url':url,
				'type':'article',
			}
	response = readFeed(request)
	print response
	return response

if __name__ == '__main__':
	test()