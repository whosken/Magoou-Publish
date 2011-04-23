from math import sqrt
from operator import *
from datetime import datetime
import re
import json

def prod(one,two):
	return reduce(lambda x, y: x*y, list)
	
def dot(one,two):
	if len(one) != len(two):
		raise Exception('different length vectors')
	
	if type(one[0]) is iter or type(two[0]) is iter:
		product = dot(one[0]*two[0])
	else:
		product = float(one[0]) * float(two[0])
	
	if len(one) > 1:
		return product + dot(one[1:],two[1:])
	else:
		return product
	
def magnitude(list):
	return sqrt(dot(list,list))

def uniqify(list):
	set = {}
	map(set.__setitem__,list,[])
	return set.keys()
	
def jsonify(instance):
	def simplify(object):
		if type(object) is dict:
			object = cleanDict(object)
			for key,value in object.items():
				object[key] = simplify(value)
		elif type(object) is type(i for i in range(0)):
			object = simplify(list(object))
		elif type(object) is list:
			for value in object:
				value = simplify(value)
		elif isinstance(object,datetime):
			object = formatDateTime(object)
		return object
	return json.dumps(simplify(instance))

def formatDateTime(dt):
	if isinstance(dt,datetime):
		return [dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second]
	elif type(dt) is list:
		return dt
	
def jsonToDateTime(list):
	args = {
			'year':list[0],
			'month':list[1],
			'day':list[2],
			'hour':list[3],
			'minute':list[4],
			'second':list[5],
		}
	return datetime(**args)
	
HTMLCODES = (
				('&', '&amp;'),
				('<', '&lt;'),
				('>', '&gt;'),
				('"', '&quot;'),
				("'", '&#39;'),
				('>>', '&raquo;'),
				('/', '&frasl;'),
				(' ', '&nbsp;'),
				("'", '&#8217;'),
				('--', '&#8211;'),
			)
	
def htmlDecode(string,encode=False):
	for before,after in HTMLCODES:
		if not encode:
			before,after = after,before
		string = string.replace(before,after)
	return string
	
def removeTags(string):
	string = htmlDecode(string)
	return re.sub(r'<[^<]*?>',' ',string)
	
def cleanText(string):
	string = removeTags(string)
	string = string.decode('utf-8').strip()
	return unicode(string)
	
def updateDictValue(dict,key,value,additive=True):
	# update value in dict, only for numbers
	if type(value) not in (float,int):
		raise Exception('unsupported type: '+str(type(value)))
	
	if key in dict:
		if additive:
			dict[key] += value
		else:
			dict[key] *= value
	else:
		if additive:
			dict[key] = value
		else:
			dict[key] = value / len(dict)
	return dict
	
def updateDictValues(dict,value,additive=True):
	for key in dict:
		updateDictValue(dict,key,value,additive)
	return dict
	
def mergeDict(dict,dict2,additive=True):
	for key,value in dict2.items():
		updateDictValue(dict,key,value,additive)
	return dict
	
def sortDictByValue(dict,revert=False):
	return sorted(dict.iteritems(),key=itemgetter(1),reverse=revert)
	
def completeDict(dict,keys,default=None):
	# for creating dict containing all key in keys
	set = {}
	map(set.__setitem__,keys,list(default for key in keys))
	return mergeDict(dict,set)

def cleanDict(dict):
	# remove entries with None or '' values
	for key,value in dict.items():
		if value is None or value == '':
			dict.pop(key)
	return dict