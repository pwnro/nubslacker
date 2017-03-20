import threading
import time

def get_channels(sc):
	channels = {}
	
	try:
		for channel in sc.api_call("channels.list")['channels']:
			channels[channel['id']] = channel['name']
	except:
		raise Exception("api_call: could not get channels list!")

	return channels

def get_members(sc):
	members = {}
	
	try:
		for member in sc.api_call("users.list")['members']:
			members[member['id']] = member['name']
	except:
		raise Exception("api_call: could not get members list!")

	return members
