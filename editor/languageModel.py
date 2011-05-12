from publish.util import *
from math import exp
from copy import deepcopy

def scoreEntries(topics,matrix,wordBag):
	try:
		return _languageModel(topics,matrix,wordBag)
	except:
		logError(__name__)
	
def _languageModel(topics,matrix,wordWeight):
	# language model with dirichlet smoothing
	docWordWeight = deepcopy(matrix)
	docWeight = {} # weight per doc
	totalWeight = 0	
	for id,doc in docWordWeight.items():
		tools.mergeDict(doc,topics,additive=False)
		docWeight[id] = sum(doc.values())
		totalWeight += docWeight[id]
	
	def yieldScore(id):
		for word in docWordWeight[id]:
			yield _getScore(docWordWeight[id][word],wordWeight[word],docWeight[id],totalWeight)
	
	candidates = {}
	for id in docWordWeight:
		candidates[id] = tools.prod(yieldScore(id))
	
	return candidates
	
def _getScore(docWordWeight,wordWeight,docWeight,totalWeight):
	# widen gap between top scores to clearly differentiate between them
	return exp(float(docWordWeight*totalWeight + wordWeight*docWeight) / float(docWeight+totalWeight))