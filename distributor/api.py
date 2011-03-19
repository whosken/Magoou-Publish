import web
from handlers import *

urls = (
		'/', 'RequestHandler'
	)

app = web.application(urls, globals())


		
if __name__ == '__main__':
	app.run()