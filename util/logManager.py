import sys
import logging
from datetime import datetime

# TODO: use logging module
def logMessage(component, message):
	if type(message) not in (unicode,str):
		message = unicode(message)
	return _writeToLog(_form_message(component,message))

def logError(component):
	message = _writeToLog(_form_message(component,repr(sys.exc_info()[1])))
	_sendNotice(message)
	raise
	
def _form_message(header,message):
	return '{0} -- {1}: {2}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S'),header,message)
	
def _writeToLog(message):
	print message # TODO: write to file
	return message
	
def _sendNotice(message):
	pass # TODO: send email
	return message