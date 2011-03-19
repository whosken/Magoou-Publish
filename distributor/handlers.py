from web.form import *
from util import *
from storage import *

class RequestHandler:
	def __init__(self):
		pass
	
	def GET(self):
		return 'get!'
		
	def POST(self):
		return 'post!'

class LandingHandler(RequestHandler):
	def get_login_form(self):
		return Form(
				Textbox('Username'),
				Password('Password'),
				Button('Login'),
			)
	
	def get_register_form(self):
		return Form(
				TextBox('Username'),
				Password('Password'),
				Password('Confirm Password'),
				Button('Register'),
			)

	def POST(self):
		hash = sha256(password).hexdigest()
		with UserManager as storage:
			return storage.authenticateUser(username,hash)
			
class ServiceHandler(RequestHandler):
	def 