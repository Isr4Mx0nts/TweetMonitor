from urlparse import urlparse
import time
import requests
import tweepy
import os
import re
import sys
import json
import thread
import threading
from lib.correo.clientcorreo import ClientCorreo
from lib.config.appconfig import CorreoConfig
from tweepy.auth import OAuthHandler
from termcolor import colored



class StdOutListener(tweepy.StreamListener ):

	def __init__(self, correo_config, StdOutListener, access_token, access_secret, consumer_key, consumer_secret, path):
		self.access_token = access_token
		self.access_secret = access_secret
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.path = path
		self.StdOutListener = StdOutListener
		self.correo_config = correo_config
	
	def validateConnectionOption(self):
		LIST = self.readFile()
		self.connectTo(LIST)		
		 
		
				
	def connectTo(self, LIST):
		l = StdOutListener(self.correo_config, self.StdOutListener, self.access_token, self.access_secret, self.consumer_key, self.consumer_secret, self.path)
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_secret)

		stream = tweepy.Stream(auth, l)
		stream.filter(track=LIST[1],async=True)


	def readFile(self):
		ListH = []
		ListU = []
		LIST = []
		
		if os.path.isfile(self.path+"users"):
			with open(self.path+"users") as my_file:
				for line in my_file:
					ListU.append(line.rstrip('\n'))
		else:
			print("Archivo vacio")
			

		if os.path.isfile(self.path+"hashtags"):
			with open(self.path+"hashtags") as my_file:
				for line in my_file:
					ListH.append(line.rstrip('\n'))
		else:
			print("Empty File")
			
		LIST.append(ListU)
		LIST.append(ListH)
		return LIST


	def detectaAlertaHilo(self, tweet, user, url):#paramas d, u, url
		LIST = self.readFile()#ListC	ListH
		
		config_file_path = os.path.join(os.getcwd(), 'config.yml')
		self.correo_config = CorreoConfig(config_file_path)

		correo_client = ClientCorreo(self.correo_config.get_property('user'), self.correo_config.get_property('pwd'), self.correo_config.get_property('dest'), self.correo_config.get_property('subject'))
		
		session = requests.Session() 

		#matches = re.findall(r'#\w*', line)
		#goo.gl/gZUiCA  #sre  #defacement
		for i in LIST[1]:#Lista de ataques (hashtags)
			matches = re.findall(r'#\w*', tweet)
			matches2 = re.findall(r'\w*', tweet)
			if ( (unicode(i, "utf-8")) in matches or (unicode,'#'+i) in matches2):
			#matches = re.findall(r'#\w*', tweet)
			#print (matches)
			#if (matches):
				if (url):
					for j in url:
						if (j['expanded_url'] or j['url']):
							
							urlCortada = j['url']
							#if "http" not in urlCortada:
							#	urlCortada = "http"+
							resp = session.head(urlCortada, allow_redirects=True)
							
							url_expandida = str(resp.url)
							print colored(url_expandida, 'blue')
							
							domain = urlparse(url_expandida)#.hostname #url_expandida.split("//")[-1].split("/")[0]
							
							
							for k in LIST[0]:#Lista de clientes
								
								if (k in str(domain.netloc)):#or k in url_expandida):
									print colored(user, 'red')
									print colored(tweet, 'red')
									print colored(url_expandida, 'red')
									#print('\x1b[6;30;42m' +user+ '\x1b[0m')
									correo_client.EnviaCorreo(tweet, user, url_expandida)
									thread.exit()
									
								else:
									continue
				else:
					for h in LIST[0]: #Lista de clientes
						twt = tweet.split(" ")		
						if (h in twt or ("#"+h) in twt):
							url_expandida = []
							print colored(user, 'red')
							print colored(tweet, 'red')
							print colored("Sin URL detectada")
							correo_client.EnviaCorreo(tweet, user, url_expandida)
							thread.exit()
				
			else:
				continue

			
		print colored(user, 'green')
		print colored(tweet, 'green')
		#print('\x1b[6;30;42m' +user+ '\x1b[0m')	
		#print('\x1b[6;30;42m' +tweet+ '\x1b[0m')
		thread.exit()

		
	def on_data(self, data):
		#print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
		
		decoded = json.loads(data)
		u = decoded["user"]["screen_name"]
		d = decoded['text']
		n = len(decoded['entities']['urls'])
 		#if (n > 0):
		url = decoded['entities']['urls']
		try:

			t = threading.Thread(target=self.detectaAlertaHilo, args=(d,u,url))
			#thread.start_new_thread( detectaAlertaHilo, (d, u, ))
			t.start()
		except e:
			print "Error: unable to start thread"
			print (e)

		return True

	def on_error(self, status):
		print ("Error")
        	print (status)

