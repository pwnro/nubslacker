import sys
import time
import threading
import subprocess as sbp
import base64 as b64

from utils import *

from slackclient import SlackClient

shell_users = ["nutzu"]

try:
	with open('slack.token', 'r') as f:
		slack_token = f.read().strip()
except:
	print("can't read token from slack.token!")
	sys.exit(1)

sc = SlackClient(slack_token)

channels = {}
members = {}

# updates channels and members from the slack api every 10 minutes
def update_slack_data():
	global channels, members
	channels = get_channels(sc)
	members = get_members(sc)
	
	t = threading.Timer(10 * 60, update_slack_data)
	t.daemon = True
	t.start()

update_slack_data()
print("> got slack channels and members")

if sc.rtm_connect():
	print("> connected to slack RTM api")
	while True:
		for event in sc.rtm_read():
			if event["type"] == u"message" and "text" in event:
				
				# handle bot commands that start with "!"
				if event["text"].startswith("!"):
					cmd_line = event["text"].strip('!')
				
					try:
						cmd = cmd_line.split()[0]
					except:
						continue
					
					try:
						cmd_args = cmd_line[len(cmd):].strip()
					except:
						cmd_args = ""
						
					if cmd == "shell" and event["user"] in members:
						try:
							print("executing shell command: " + cmd_args)
							
							cmd_out = sbp.check_output(cmd_args, stderr=sbp.STDOUT, shell=True)
							sc.api_call( "chat.postMessage", channel="#" + channels[event["channel"]], text=cmd_out)
						except sbp.CalledProcessError as e:
							print("cmd_shell: can't execute command!")
							sc.api_call( "chat.postMessage", channel="#" + channels[event["channel"]], text="cmd failed: " + str(e.output))
					
					elif cmd == "say":
						sc.api_call("chat.postMessage", channel="#" + channels[event["channel"]], text=cmd_args)
						
					elif cmd == "die":
						# just fuck off and die
						print("> received !die command, existing..")
						sys.exit(1)

				# handle other text stuff that would trigger teh bot						
				else:
					if b64.b64decode("cGVwc2ltaW4=") in event["text"].lower():
						sc.api_call( "chat.postMessage", channel="#" + channels[event["channel"]], text=b64.b64decode("Y29rZSA+IHBleGk="))

	time.sleep(1)
else:
	raise Exception("rtm_connect: can not connect to slack RTM, invalid token?")
