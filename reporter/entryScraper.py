import re
import json
from operator import *
from datetime import *
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup, NavigableString
from publish.util import *

configLogging(__name__)

def scrapeEntry(entry):
	info('scraping ' + entry['url'])
	try:
		raw = _crawlUrl(entry['url'])
		soup = BeautifulSoup(raw)
		return _traverseHtml(entry, soup)
	except Exception, e:
		error(e) # continues process after logging error
		
def _crawlUrl(url):
	return urlopen(url,timeout=config.TIMEOUT).read()
	
def _traverseHtml(entry,soup):
	if 'icon' not in entry:
		for tag in findAllTags(soup,'link'):
			href = getAttribute(tag,'href')
			if href and href.count('.ico') > 0:
				entry['icon'] = href
				break

	if 'title' not in entry:
		titles = soup.body.findAll('h1')
		if len(titles) > 0:
			entry['title'] = titles[0].string
	
	entry['highlight'], div = _highlightText(soup)
	
	media, type, highlight = _highlightMedia(soup,entry['type'],div)
	
	# assume it's a media if there aren't much text
	if entry['type'] == 'article' and len(entry['highlight']) < 10:
		entry['type'] = type
		return _traverseHtml(entry,soup)
	
	if highlight and ('highlight' not in entry):
		entry['highlight'] = unicode(highlight)
	if media and 'media' not in entry:
		entry['media'] = unicode(media)
	if 'summary' not in entry:
		entry['summary'] = tools.cleanText(entry['highlight'])
		entry.pop('highlight')
	return entry

def _highlightText(soup):
	# find the no-comment <div> and extract few <p> with highest word count
	ptags = []
	if soup.body:
		for p in findAllTags(soup.body,'p'):
			text = unicode(p)
			if text.count('<script') > 0:
				continue		
			texts = tools.cleanText(text)
			score = float(len(texts.split()))
			ptags.append((score, p))
	
	def extract_top_ps(size):
		total = 0
		for ptag in sorted(ptags,key=itemgetter(0),reverse=True):
			if total > size:
				break
			total += ptag[0]
			yield ptag[1]
			
	topPs = list(extract_top_ps(config.SUMMARYSIZE))
	
	highlights = set(unicode(p) for p in topPs)
	return '<br />'.join(highlights), topPs[0].findParent('div')
	
def _highlightMedia(soup,type,div):
	# extract dominate media and its embedded highlight
	if type != 'image':
		# check for flash object
		mediae = findInScript(soup,'\<object\s[^\w\W]+object\>')
		if mediae:
			return mediae[0], 'rich', None
		# check for div or iframe with 'player'
		for media in findAllTags(soup,'div|iframe'):
			id, clas = getAttribute(media,'id'), getAttribute(media,'class')
			if (id and id.count('player') > 0) or (clas and clas.count('player') > 0):
				return media, 'rich', None
	
	# check for image
	else:
		image = findTag(div,'img')
		if image:
			try:
				description = image['alt']
			except:
				description = None
			return image, 'image', description

	return None, None, None
	
def findAllTags(tag,regex):
	results = tag.findAll(re.compile(regex.lower()))
	if not len(results) > 0:
		xmls = re.findall(str(tag),r'<[{0}][^>]*>.*?</{0}>|<[{0}][^>]*/>'.format(regex))
		results = list(BeautifulStoneSoup(xml,convertEntities=['xml','html']) for xml in xmls)
	return results
	
def findTag(tag,regex,string=False):
	# return the first result or its string
	results = findAllTags(tag,regex)
	if len(results) > 0:
		if string:
			return results[0].string
		return results[0]
	else:
		if string:
			return ''
		return None

def getAttribute(tag,attribute):
	try:
		return tag[attribute]
	except:
		return None
	
def findInScript(tag,regex):
	for script in findAllTags(tag,'script'):
		result = re.match(regex,str(tag))
		if result:
			return result
	return None
	
def findMeta(tag,attributes=None,name=None):
	if attributes:
		return unicode(tag.findAll('meta',attrs=attributes)[0]['content'])
	return unicode(tag.findAll('meta',attrs={'name':name})[0]['content'])
	
def test():
	import feedReader
	request = list(entry for entry in feedReader.test())[0][0]
	response = scrapeEntry(request)
	print response
	return response
	
def test2():
	url = 'http://www.codinghorror.com/blog/2004/02/about-me.html'
	response = scrapeEntry({'url':url,'type':'article'})
	print response
	return response

if __name__ == '__main__':
	test()
	test2()