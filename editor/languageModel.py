from util import *

def scoreEntries(prefers,matrix,wordBag):
	try:
		return _languageModel(prefers,matrix,wordBag)
	except:
		logError(__name__)
	
def _languageModel(prefers,docWordWeight,wordWeight):
	# language model with dirichlet smoothing
	
	docWeight = {} # weight per doc
	totalWeight = 0
	for id,doc in docWordWeight.items():
		tools.mergeDict(doc,prefers,additive=False)
		docWeight[id] = sum(doc.values())
		totalWeight += docWeight[id]
	
	candidates = {}
	for id in docWordWeight:
		weight = 1
		for word in docWordWeight[id]:
			weight *= _getScore(docWordWeight[id][word],wordWeight[word],docWeight[id],totalWeight)
		candidates[id] = weight
	return candidates
	
def _getScore(docWordWeight,wordWeight,docWeight,totalWeight):
	return (docWordWeight*totalWeight + wordWeight*docWeight) / (docWeight+totalWeight)