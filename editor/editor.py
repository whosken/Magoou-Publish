from publish.util import *
from copy import deepcopy

configLogging(__name__)

def run(storage):
	runThreads(runEdit,storage.getUnprocessedProfiles,storage)

def runEdit(profile,storage):
	release = selectCandidates(profile['topics'],storage)
	issue = {
				'username':profile.['username'],
				'entries':release,
			}
	result = storage.putIssue(issue)
	storage.putUser(user)
	return result
	
def selectCandidates(topics,storage):
	entries = storage.getLatestEntries()
	pool = _getPool(entries)
	wordBag = storage.getKeywordWeights()
	topicBag = storage.getTopicWeights()
	
	# standardization
	words = set(topics.keys() + wordBag.keys())
	query = deepcopy(topics)
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
	
	return ensemble.scoreEntries(candidates,topics,topicBag,pool,wordBag)
	
# to do, move out of editor
def _factorFeedback(profile,storage):
	# base on the action, reward each keyword
	for feedback in storage.getUserFeedbacks(profile['username']):
		if feedback['datetime'] < profile['datetime']:
			continue
		action = feedback['action'] if feedback['action'] in config.FEEDBACKSCORES else None
		if action:
			score = config.FEEDBACKSCORES[action]
			id = feedback['entryid']
			if contents.checkDocumentExistence(id):
				entry = contents.getDocument(id)
				for word in entry['keywords'].keys():
					tools.updateDictValue(profile['topics'],word,score,additive=False)
	return profile
	
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
	info('commence testing!')
	from util.storage import Storage
	with Storage() as storage:
		run(storage)
	info('finished testing!')
	
if __name__ == '__main__':
	test()
