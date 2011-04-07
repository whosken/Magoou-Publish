from math import log1p
from util import *
import re

def generateKeywords(entry,keywords=None):
	logMessage(__name__, "selecting keywords from " + entry['url'])
	try: # TODO: consider better hieuristics for assigning bonuses
		if not keywords:
			keywords = {}
		else:
			tools.updateDictValues(keywords,config.DISCOUNT,additive=False) # reduce weighting of keywords from feeds
		
		if 'title' in entry:
			_collectKeywords(collectTerms(entry['title'],False),keywords,config.TITLEWEIGHT)
		if entry['type'] == 'article': # if content is article
			_collectKeywords(collectTerms(entry['summary']),keywords,config.SUMMARYWEIGHT)
			if 'highlight' in entry: # if content has been scraped
				_collectKeywords(collectTerms(entry.pop('highlight')),keywords,config.HIGHLIGHTWEIGHT)
		
		infos = []
		for key in ('author','source','language'):
			if key in entry:
				infos.append(entry[key])
		infos = list(_filteredTerms(infos))
		_collectKeywords(infos,keywords,config.INFOWEIGHT,False)
		
		if 'categories' in entry:
			categories = []
			for category in entry['categories']:
				categories += collectTerms(category)
			_collectKeywords(categories,keywords,config.CATEGORYWEIGHT)
		
		return keywords
	except:
		logError(__name__)
	
def _collectKeywords(terms,words,bonus=0,calcWeight=True):
	for term in terms:
		term = term.lower().encode('utf-8')
		if calcWeight:
			words = tools.updateDictValue(words,term,_weightTerm(term,len(terms),bonus))
		else:
			words = tools.updateDictValue(words,term,bonus)
	return words
	
def collectTerms(string,nGram=True):
	string = re.sub(r'<[^<]*?>|\W',' ', string)
	tokens = list(_filteredTerms(string.split()))
	if nGram:
		count = len(tokens)-1 #dont count the last term
		for i in range(count):
			j = i
			while tokens[j].istitle():
				if j < count:
					j += 1
				else:
					break
			token = tokens[i:j]
			if len(token) > 1:
				tokens.append(' '.join(token))
	return tokens

def _filteredTerms(tokens): #TODO: use better NLP algorithms
	for token in tokens:
		#not an oversaturated word
		if not token.lower() in config.MEHS:
			if len(token) > 1:
				yield token.strip()
			
def _weightTerm(term,docLength,bonus): #TODO: use better weightings
	termLength = term.count(" ") + 1
	charLength = len(term)
	#update term weight by log(character length + bonus) * term length -- tf weights
	return log1p(charLength + bonus)*termLength/docLength
	
def test():
	import feedReader
	request = list(entry for entry in feedReader.test())
	response = generateKeywords(request[0][0])
	print response
	return response
	
def test2():
	import entryScraper
	request = entryScraper.test2()
	response = generateKeywords(request)
	print response
	return response

if __name__ == '__main__':
	# test()
	test2()