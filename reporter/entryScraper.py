import re
import json
from operator import *
from datetime import *
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup, NavigableString
from util import *

TIMEOUT = 30 # in secs = 0.5 minutes
SUMMARYSIZE = 30 # words
OEMBEDMAPPINGS = [
					('title','title'),
					('author','author_name'),
					('source','provider_name'),
					('media','url'),
					('summary','description'),
					('media','html'),
					# TODO: add ico
				]
OEMBEDTYPES = {
				'photo':'image',
				'video':'video',
				'rich':'rich',
				'link':'article',
			}

def scrapeEntry(entry,tryEmbed=True):
	logMessage(__name__, "scraping " + entry['url'])
	try:
		raw, oEmbed = _crawlUrl(entry,tryEmbed)
		if oEmbed:
			data = json.loads(raw)
			return _traverseOEmbed(entry, data)
		else:
			soup = BeautifulSoup(raw)
			return _traverseHtml(entry, soup)
	except:
		logError(__name__)
		
def _crawlUrl(url,tryEmbed):
	if tryEmbed:
		try:
			return urlopen(_oEmbed(url),timeout=TIMEOUT).read(), True
		except:
			pass
	return urlopen(url,timeout=TIMEOUT).read(), False

def _traverseOEmbed(entry,data):
	if data['type'] == 'error':
		return scrapeEntry(entry,tryEmbed=False)
	
	entry['type'] = OEMBEDTYPES[data['type']]
	for key,field in OEMBEDMAPPINGS:
		if field in data and (key not in entry or entry[key] == ''):
			entry[key] = data[field]
	return entry
	
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
	
	# assume it's a media if there aren't much text
	if entry['type'] == 'article' and len(entry['highlight']) < 10:
		entry['type'] = type
		return _traverseHtml(entry,soup)
	
	media, type, highlight = _highlightMedia(soup,entry['type'],div)
	
	if highlight and ('highlight' not in entry):
		entry['highlight'] = unicode(highlight)
	if media and 'media' not in entry:
		entry['media'] = unicode(media)
	if 'summary' not in entry:
		entry['summary'] = tools.cleanText(entry['highlight'])
	return entry

def _highlightText(soup):
	# find the no-comment <div> and extract few <p> with highest word count
	ptags = []
	for p in findAllTags(soup.body,'p'):
		# filter out comments
		skip = False
		for div in p.findParents('div'):
			divClass = getAttribute(div,'class')
			if divClass and divClass.count('comment') > 0:
				skip = True
				break
		if skip:
			continue

		if not len(p.contents) > 0:
			continue
		text = unicode(p)
		if text.count('<script') > 0:
			continue
		
		score = 0
		for content in p.contents:
			if isinstance(content,NavigableString):
				score += len(content.split())
		ptags.append((score,p))
	
	def extract_top_ps(wordsSize):
		total = 0
		for ptag in sorted(ptags,key=itemgetter(0),reverse=True):
			if total > wordsSize:
				break
			total += ptag[0]
			yield ptag[1]
			
	topPs = list(extract_top_ps(SUMMARYSIZE))
	
	highlights = tools.uniqify(list(unicode(p) for p in topPs))
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

def _oEmbed(url):
	return 'http://api.embed.ly/1/oembed?url={0}'.format(url)
	
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
	import urllib2
	request = list(entry for entry in feedParser.test())[0][0]
	raw = urllib2.urlopen(request['url']).read()
	response = scrapeEntry(request,raw)
	print response
	return response

if __name__ == '__main__':
	test()