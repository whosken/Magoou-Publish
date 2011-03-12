from util import *

def scoreEntries(prefers,matrix):
	try:
		return _languageModel(prefers,matrix)
	except:
		logError(__name__)
	
def _languageModel(prefers,wordDocWeight):
	# language model with dirichlet smoothing
	
	wordWeight = {} # word per all doc
	docWeight = {} # weight per doc
	totalWeight = 0
	totalPrefers = sum(prefers.values())
	
	for id in wordDocWeight:
		for word in wordDocWeight[id]:
			weight = wordDocWeight[id][word]
			if word in prefers:
				weight *= prefers[word] / totalPrefers
			
			# update weight of the word
			tools.updateDictValue(wordWeight,word,weight)
			
			#update weight of the character
			tools.updateDictValue(docWeight,id,weight)
			
			wordDocWeight[id][word] = weight
			totalWeight += weight
	
	candidates = {}
	for id in wordDocWeight:
		weight = 1
		if word in wordDocWeight[id]:
			weight *= _getScore(wordDocWeight[id][word],wordWeight[word],docWeight[id],totalWeight)
		candidates[id] = weight
	return candidates
	
def _getScore(wordDocWeight,wordWeight,docWeight,totalWeight):
	return (wordDocWeight*totalWeight + wordWeight*docWeight) / (docWeight+totalWeight)