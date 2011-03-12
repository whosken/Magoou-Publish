from util import *

def scoreEntries(query,matrix):
	try:
		return _cosSim(query,matrix)
	except:
		logError(__name__)
	
def _cosSim(query,matrix):
	# cos-sim = A dot B / |A||B|
	queryMag = tools.magnitude(query.values())
	queryVec = query.values()
	
	candidates = {}
	for id in matrix:
		vector = matrix[id].values()
		vectorMag = tools.magnitude(vector)
		dotProd = tools.dot(queryVec,vector)
		if dotProd:
			candidates[id] = dotProd / (queryMag * vectorMag)
	return candidates