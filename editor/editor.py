from threading import Thread
from copy import deepcopy
from util import *

def run(users,contents):
	try:
		def startThread(request,users,contents):
			thread = Thread(target=runEdit,args=(request,users,contents,))
			thread.start()
			return thread
		
		threads = []
		for user in users.getUninformedUsers():
			user = _factorUsage(user,users,contents)
			threads.append(startThread(user,users,contents))
			if len(threads) > config.THREADLIMIT:
				break
			
		for thread in threads:
			thread.join()
	except:
		logError(__name__)

def runEdit(user,users,contents):
	release = selectCandidates(user['preferences'],users,contents)
	issue = {
				'username':user['username'],
				'entries':release,
				'public':user['public'] if 'public' in user else None,
			}
	result = users.putIssue(issue)
	users.putUser(user)
	return result
	
def selectCandidates(prefer,users,contents):
	entries = contents.getLatestEntries()
	pool = _getPool(entries)
	wordBag = contents.getKeywordWeights()
	preferBag = users.getPreferenceWeights()
	
	# standardization
	words = set(prefer.keys() + wordBag.keys())
	query = deepcopy(prefer)
	tools.updateDictValues(query,1.0/sum(query.values()),additive=False) # nornmalize query
	tools.completeDict(query,words,default=0)
	tools.completeDict(wordBag,words,default=0)
	matrix = _getMatrix(pool,words)
	
	import languageModel as lang
	import cosSim as cos
	import ensemble
	
	candidates = {}
	candidates['cosSim'] = cos.scoreEntries(query,matrix)
	candidates['languageModel'] = lang.scoreEntries(query,matrix,wordBag)
	
	return ensemble.scoreEntries(candidates,prefer,preferBag,pool,wordBag)
	
def _factorUsage(user,users,contents):
	# base on the action, reward each keyword
	for usage in users.getUserUsage(user['username']):
		if usage['datetime'] < user['datetime']:
			continue
		action = usage['action'] if usage['action'] in config.USAGESCORES else None
		if action:
			score = config.USAGESCORES[action]
			id = usage['entryid']
			if contents.checkDocumentExistence(id):
				entry = contents.getDocument(id)
				for word in entry['keywords'].keys():
					tools.updateDictValue(user['preferences'],word,score,additive=False)
	return user
	
def _getPool(entries):
	# return a map from entry id to keywords
	pool = {}
	for entry in entries:
		pool[entry['_id']] = entry['keywords']
	if not len(pool) > 0:
		raise Exception ,'No entries found! Try run reporter first'
	return pool
	
def _getMatrix(entries,keys):
	# returns a matrix where each value is a dict with words not in value are 0
	matrix = {}
	for id,doc in entries.items():
		matrix[id] = tools.completeDict(doc,keys,default=0)
	return matrix
	
def _updateKeywordWeights(candidates,keywords):
	# for adding keywords to queries
	for row in keywords:
		row['weight'] *= candidates[row['id']]
	return keywords
	
def test():
	logMessage(__name__,'commence testing!')

	from storage.couchManager import UserManager, ContentManager
	with UserManager() as users:
		with ContentManager() as contents:
			run(users,contents)
	logMessage(__name__,'finished testing!')
	
if __name__ == '__main__':
	test()
