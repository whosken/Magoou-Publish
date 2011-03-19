from util import *

def scoreEntries(candidates):
	try: # TODO: mlp?
		return _ensembleScores(candidates)
	except:
		logError(__name__)
	
def _ensembleScores(candidates):
	release = {}
	for component,entries in candidates.items():
		weighting = config.ALPHAS[component] if component in config.ALPHAS else 1
		total = sum(entries.values())
		for id,score in entries.items():
			weight = score * weighting / total
			tools.updateDictValue(release,id,weight)
	return release