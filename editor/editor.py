from publish.util import *
from copy import deepcopy

def run(storage):
	runThreads(runEdit,storage.getUnprocessedProfiles,storage,wait=False)

def runEdit(profile,storage):
	profile = factorFeedback(profile,storage)
	issue = {
				'username':profile['username'],
				'entries':selectCandidates(profile,storage),
			}
	result = storage.putIssue(issue)
	storage.putProfile(profile)
	return result
	
def selectCandidates(profile,storage,cf=True):
	def prepareQueryMatrix(topics,wordBag,pool):
		# standardization
		words = topics.viewkeys() | wordBag.viewkeys()
		query = deepcopy(topics)
		bag = deepcopy(wordBag)
		tools.updateDictValues(query,1.0/sum(query.values()),additive=False) # nornmalize query
		tools.completeDict(query,words,default=0)
		tools.completeDict(bag,words,default=0)
		matrix = _getMatrix(pool,words)
		return query,matrix,bag
	
	topics = profile['topics']
	entries = storage.getLatestEntries()
	wordBag = storage.getKeywordWeights()
	topicBag = storage.getTopicWeights()
	query,matrix,wordWeights = prepareQueryMatrix(topics,wordBag,_getPool(entries))
	
	import languageModel as lang
	import cosSim as cos
	import ensemble
	
	candidates = {}
	candidates['cosSim'] = cos.scoreEntries(query,matrix)
	candidates['languageModel'] = lang.scoreEntries(query,matrix,wordWeights)
	
	if 'model' not in profile or not profile['model']: # if profile is not a topic model
		models = _getPool(storage.getLatestProfiles(),model=True)
		issues = storage.getLatestIssues()
		query,models = prepareQueryMatrix(topics,topicBag,models)
		
		import collabrativeFiltering as coFilter
		candidtates['collabrativeFiltering'] = coFilter.scoreEntries(query,models,issues)
	
	return ensemble.scoreEntries(candidates,topics,topicBag,pool,wordBag)
	
def factorFeedback(profile,storage):
	# base on the action, reward each keyword
	for feedback in storage.getUserFeedbacks(profile['username']):
		try:
			score = config.FEEDBACKSCORES[feedback['action']];
			entry = contents.getDocument(feedback['entryid'])
			if entry:
				tools.completeDict(
						profile['topics'],
						entry['keywords'].keys(),
						default=score,
						additive=False
					)
			# remove processed feedback
			storage.deleteDocument(feedback['_id'],feedback['_rev'])
		except KeyError, e:
			error(e)
	return profile
	
def modelTopics(storage):
	# run topic modelling techniques to create topic profiles
	import latentDirichletAllocation as lda
	from hashlib import sha1
	
	entries = storage.getLatestEntries()
	for topics in lda.getTopics(entries):
		profile = {
				'username':sha1('$'.join(topics.keys())).hexdigest(),
				'topics':topics,
				'model':True
			}
		yield storage.putProfile(profile)
	
def _getPool(entries,model=False):
	# return a map from entry id to keywords
	if not len(entries) > 0:
		raise Exception ,'No entries found! Try running reporter first'
	pool = {}
	for entry in entries:
		pool[entry['_id']] = entry['keywords' if not model else 'topics']
	return pool
	
def _getMatrix(entries,keys):
	# returns a matrix where each value is a dict with words not in value are 0
	matrix = {}
	for id,doc in entries.iteritems():
		matrix[id] = tools.completeDict(deepcopy(doc),keys,default=0)
	return matrix
	
def test():
	info('commence testing!')
	from publish.util.storage import Storage
	with Storage() as storage:
		run(storage)
	info('finished testing!')
	
if __name__ == '__main__':
	test()
