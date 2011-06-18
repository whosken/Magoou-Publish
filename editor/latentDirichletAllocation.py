from publish.util import *

# create dummy profiles from existing entries

def getTopicProfiles(entries):
	try:
		return _latentDirichletAllocation(entries)
	except Exception, e:
		error(e)
		return {}
	
def _latentDirichletAllocation(entries):
	pass
	