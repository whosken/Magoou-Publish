# editor.py, reporter.py
THREADLIMIT = 10

# editor.py
USAGESCORES = {
				'like':1.25,
				'want':1.375,
				'read':1.125,
				'dislike':0.625,
				'default':1,
			}

# keywordgenerator.py
TITLEWEIGHT = 0.5
INFOWEIGHT = 0.075
SUMMARYWEIGHT = 0.5
HIGHLIGHTWEIGHT = 0
CATEGORYWEIGHT = 1

MEHS = ('a','an','the','of','for','i', '', 'this', 'that', 'he', 'she', 'it', 'him', 'her', 'they', 'them', ' ', 'and', 'to', 'in', 'being', 'is', 'his', 'am', 'are')

# feedreader.py entryscraper.py
SUMMARYSIZE = 30 # words

# entryscraper.py
TIMEOUT = 30 # in secs = 0.5 minutes
OEMBEDMAPPINGS = [
					('title','title'),
					('author','author_name'),
					('source','provider_name'),
					('media','url'),
					('summary','description'),
					('media','html'),
					# TODO: add ico
				]
OEMBEDTYPES = {
				'photo':'image',
				'video':'video',
				'rich':'rich',
				'link':'article',
			}

# ensemble.py
ALPHAS = {
			'languageModel':1.5,
			'cosSim':1,
		}