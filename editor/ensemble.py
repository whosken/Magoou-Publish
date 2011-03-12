from util import *

ALPHAS = {
			'languageModel':1.5,
			'cosSim':1,
		}

def scoreEntries(candidates):
	try: # TODO: mlp?
		return _ensembleScores(candidates)
	except:
		logError(__name__)
	
def _ensembleScores(candidates):
	release = {}
	for component,entries in candidates.items():
		weighting = ALPHAS[component] if component in ALPHAS else 1
		total = sum(entries.values())
		for id,score in entries.items():
			weight = score * weighting / total
			tools.updateDictValue(release,id,weight)
	return release