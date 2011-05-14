# editor.py, reporter.py
THREADLIMIT = 10

# editor.py
FEEDBACKSCORES = {
				'like':1.25,
				'want':1.375,
				'read':1.125,
				'dislike':0.625,
			}

# keywordgenerator.py
BONUSES = {
			'title': 0.5,
			'info': 0.075,
			'summary': 0.5,
			'highlight': 0,
			'category': 1,
		}

FEEDDISCOUNT = 0.1 # discount of feed keywords
NEARDISCOUNT = 0.5 # discount of nearby keywords
DISTANCE = 0.3 # word distance threshold
LENGTH = 3 # word length to be considering distance
NAIVECHUNK = ('zh','ja','kr') # languages that requires naive chunking

# feedreader.py entryscraper.py
SUMMARYSIZE = 30 # words

# entryscraper.py
TIMEOUT = 90 # in secs = 1.5 minutes

# ensemble.py
ALPHAS = {
			'languageModel':1.5,
			'cosSim':1,
		}
BETAS = {
			'item':('languageModel','cosSim'),
			'user':(),
		}