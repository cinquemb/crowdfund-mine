import requests
import smtplib
import simplejson
import time
from time import sleep
import sys
import os
import random
import anyjson
import pprint
import codecs
import re
from bs4 import BeautifulSoup

'''
  Script to scrape crowdfunding site associated with each tweet and store data.
  Goal for script will be for every time script is ran, it will take new data, 
  associate it with old data, and create updated stats files.
'''

init = time.time()
requests.adapters.DEFAULT_RETRIES = 10

f_tweet = open("final_mined_data/0.json","r+")

data = simplejson.load(f_tweet)
max_tweets = len(data['data'])

def parse_crowdfund_site(tweet_node):
	'''
		Return crowdfund data from page if available, 
		time page is scraped, twitter user, 
		twitter status ID
	'''
	pass

def update_crowdfund_data(p_c_s_d):
	'''
		grabs any previous data from files assocaited with previous p_c_s_d nodes returned, 
		and creates a new file with updated data
	'''
	pass

def save_crowdfund_data(u_c_d):
	'''
		create json data for node, and write to file
	'''
	pass


for i in range(0,max_tweets):
	max_tweets[i]