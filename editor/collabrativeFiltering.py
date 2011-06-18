from publish.util import *
import cosSim

# find the closest profiles
# aggregate the scores from their issues

def scoreEntries(query,models,issues):
	try:
		return _collabrativeFiltering(query,models,issues)
	except Exception, e:
		error(e)
		return {}
	
def _collabrativeFiltering(query,models,issues):
	# collaborative filtering through cos-sim scoring
	result = {}
	scores = cosSim.scoreEntries(query,models)
	for issue in issues:
		tools.updateDictValues(issue['entries'],scores[issue['_id']],additive=False)
		tools.mergeDicts(result,issue['entries'])
	return result