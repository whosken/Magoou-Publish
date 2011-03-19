from threading import Thread
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
			users.putUser(user)
			if len(threads) > config.THREADLIMIT:
				break
			
		for thread in threads:
			thread.join()
	except:
		logError(__name__)

def runEdit(user,users,contents):
	entries = contents.getEntriesWithKeywords(user['preferences'].keys(),start=user['datetime'])
	if not len(entries) > 0:
		logMessage(__name__,'No contents for '+user['username'])
		return {}
	
	release = selectCandidates(user['preferences'],entries)
	issue = {
				'username':user['username'],
				'entries':release,
				'public':user['public'] if 'public' in user else None,
			}
	return users.putIssue(issue)
	
def selectCandidates(prefer,pool):
	import languageModel as lang
	import cosSim as cos
	import ensemble
	
	candidates = {}
	
	# methods that don't require standardization
	candidates['languageModel'] = lang.scoreEntries(prefer,pool)
	
	# standardization
	allWords = _getKeys(prefer,pool)
	query = tools.completeDict(prefer,allWords,default=0)
	matrix = _getMatrix(pool,allWords)
	
	# methods that requires standardization
	candidates['cosSim'] = cos.scoreEntries(query,matrix)
	
	return ensemble.scoreEntries(candidates)
	
def _factorUsage(user,users,contents):
	# base on the action, reward each keyword
	for usage in users.getUserUsage(user['username']):
		if usage['datetime'] < user['datetime']:
			continue
		id = usage['entryid']
		if contents.checkDocumentExistence(id):
			entry = contents.getDocument(id)
			for word in entry['keywords'].keys():
				tools.updateDictValue(user['preferences'],word,usage['score'],additive=False)
	return user
	
def _getMatrix(entries,keys):
	# returns a matrix where each value is a dict with words not in value are 0
	matrix = {}
	for key,value in entries.items():
		matrix[key] = tools.completeDict(value,keys,default=0)
	return matrix
	
def _getKeys(prefer,entries):
	keys = set(prefer.keys())
	entryKeys = (set(entry.keys()) for entry in entries.values())
	return keys.union(*entryKeys)

def _updateKeywordWeights(candidates,keywords):
	# for adding keywords to queries
	for row in keywords:
		row['weight'] *= candidates[row['id']]
	return keywords
	
def test():
	logMessage(__name__,'commence testing!')
	# prefer = {
				# 'vintage':8,
				# '1930s':3,
				# 'boutiques':6,
				# 'edinburgh':10,
				# 'shop':2,
				# 'story':5,
				# 'fashion':7,
				# 'winter':4,
				# 'tweed':6,
			# }
	# testUser = {
				# 'username':'magoou_tester',
				# 'preferences':prefer,
			# }
	# from storage.managers import UserManager
	# with UserManager() as storage:
		# storage.putUser(testUser)
	# logMessage(__name__,'done creating mock user!')
	
	run()
	logMessage(__name__,'finished testing!')
	
if __name__ == '__main__':
	test()
