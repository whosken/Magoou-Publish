import sys
import traceback
import logging 

# TODO: use logging module
def logMessage(component, message):
	if type(message) not in (unicode,str):
		message = unicode(message)
	return _writeToLog(''.join((component, ': ', message)))

def logError(component):
	message = _writeToLog(' '.join(('ERROR: ', component, ': ', sys.exc_info()[1])))
	_sendNotice(message)
	raise
	
def _writeToLog(message):
	print message # TODO: write to file
	return message
	
def _sendNotice(message):
	pass # TODO: send email
	return message