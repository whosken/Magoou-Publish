from publish.util import *

def scoreEntries(candidates,*args):
	return _ensembleScores(candidates,*args)
	
# TODO: implement collaborative filtering?
# TODO: implement latent dirichlet allocation
	
def _ensembleScores(candidates,topic,topicBag,pool,wordBag):
	release = {}
	for component,entries in candidates.items():
		alpha = config.ALPHAS.get(component,default=1)
		total = sum(entries.values())
		for id,score in entries.items():
			beta = len(pool[id]) / len(wordBag) if component in config.BETAS['item'] else len(topic) / len(topicBag)
			weight = score * alpha * beta / total
			tools.updateDictValue(release,id,weight)
	return release