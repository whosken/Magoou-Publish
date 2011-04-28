from util import *

def scoreEntries(candidates,*args):
	try: # TODO: mlp?
		return _ensembleScores(candidates,*args)
	except:
		logError(__name__)
	
def _ensembleScores(candidates,prefer,preferBag,pool,wordBag):
	release = {}
	for component,entries in candidates.items():
		alpha = config.ALPHAS[component] if component in config.ALPHAS else 1
		total = sum(entries.values())
		if total > 0:
			for id,score in entries.items():
				beta = len(pool[id]) / len(wordBag) if component in config.BETAS['item'] else len(prefer) / len(preferBag)
				weight = score * alpha * beta / total
				tools.updateDictValue(release,id,weight)
		else:
			print component
			print entries
			raise Exception, 'No entries are recommended to the user'
	return release