from math import log1p
from copy import deepcopy
from util import *
import re

def generateKeywords(entry,bag=None,keywords=None):
	logMessage(__name__, "selecting keywords from " + entry['url'])
	try: # TODO: consider better hieuristics for assigning bonuses
		if not keywords:
			keywords = {}
		else:
			tools.updateDictValues(keywords,config.FEEDDISCOUNT,additive=False) # reduce weighting of keywords from feeds
		
		naive = entry['language'] in config.NAIVECHUNK
		
		if 'title' in entry:
			_collectKeywords(collectTerms(entry['title'],ngram=False),keywords,config.BONUSES['title'])
			
		if 'summary' in entry:
			_collectKeywords(collectTerms(entry['summary'],naive=naive),keywords,config.BONUSES['summary'])
		if 'highlight' in entry: # if content has been scraped
			_collectKeywords(collectTerms(entry.pop('highlight'),naive=naive),keywords,config.BONUSES['highlight'])
		
		infos = []
		for key in ('author','source','language'):
			if key in entry:
				infos.append(entry[key])
		infos = list(_filteredTerms(infos))
		_collectKeywords(infos,keywords,config.BONUSES['info'],False)
		
		if 'categories' in entry:
			categories = []
			for category in entry['categories']:
				categories += collectTerms(category,naive=naive)
			_collectKeywords(categories,keywords,config.BONUSES['category'])
			
		if bag:
			_getNearTerms(keywords,bag)
		
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
	
cache = {} # cache for word distances
def _getNearTerms(words,bag):
	for word in deepcopy(words):
		if len(word) > config.LENGTH:
			for term,score in bag.items():
				key = sorted((word,term))
				if key not in cache:
					cache[key] = _calcWordDistance(word,term) < config.DISTANCE
				if cache[key]:
					tools.updateDictValue(words,term,score * config.NEARDISCOUNT)
	return words
	
def collectTerms(string,ngram=True,naive=False):
	string = re.sub(r'<[^<]*?>|\W',' ', string)
	tokens = list(_filteredTerms(string.split()))
	if ngram:
		count = len(tokens)-1 #dont count the last term
		for i in range(count):
			if naive:
				tokens.append(tokens[i:i+2])
			else:
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
		if len(token) > 1:
			yield token
			
def _weightTerm(term,docLength,bonus): #TODO: use better weightings
	termLength = term.count(' ') + 1
	charLength = len(term)
	#update term weight by log(character length + bonus) * term length -- tf weights
	return log1p(charLength + bonus)*termLength/docLength
	
def _calcWordDistance(first,second):
	# find the Levenstein distance between two strings
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return 1
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
    for j in range(second_length):
        distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return float(distance_matrix[first_length-1][second_length-1]) / float(len(second))

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