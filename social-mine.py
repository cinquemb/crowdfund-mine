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

init = time.time()
requests.adapters.DEFAULT_RETRIES = 10

_tmp_file = '%s.json' % (init)
MINED_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mined_data'))
mined_data_string = '%s/%s' % (MINED_DATA_DIR,_tmp_file)
#mined_data_string = '%s/%s' % (MINED_DATA_DIR,'temp.json')
f = open(mined_data_string,"w+")
#print mined_data_string

crowdsource_site_list = ['startsomegood', 'indigogo', 'kickstarter']

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def url_comparison(full_url,truncated_url):
	if full_url.find(truncated_url) is not -1:
		return True
	else:
		return False

def get_retweet_data(tweet_id):
	val = 'https://twitter.com/i/activity/retweeted_popup?id=%s' % (tweet_id)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.35)
	data = r.text
	data1 = simplejson.loads(data)
	general_print_dict(data1,'{"retweet')

def get_favorite_data(tweet_id):
	val = 'https://twitter.com/i/activity/favorited_popup?id=%s' % (tweet_id)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.35)
	data = r.text
	data1 = simplejson.loads(data)
	general_print_dict(data1, '{"favorite')

def get_tweet_data(tweet_id):
	#may need to edit since unless part of url isnt used in query
	val = 'https://twitter.com/i/status/%s' % (tweet_id)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.35)
	data = r.text
	check = overall_print_dict(data)

	if check != 0:
		if check == 3:
			get_retweet_data(tweet_id)
			f.seek(-1,1)
			f.write(',')
			get_favorite_data(tweet_id)
		elif check == 2:
			get_retweet_data(tweet_id)
		elif check == 1:
			get_favorite_data(tweet_id)
		f.write('   ]\n  }\n ]\n},\n')
	else:
		f.seek(-1,1)
		f.write(']},\n')

def general_print_dict(itr_dict, category):
	f.write('\n     %s-metadata": [\n' % (category))
	for key, value in itr_dict.iteritems():
		#data-user-id
		if key == 'htmlUsers':
			soup = BeautifulSoup(value)
			data_val = re.compile("^-?[a-zA-Z0-9]+$")
			nodes = soup.find_all(data_val)
			userid_nodes = []
			for node in nodes:
				data2 = simplejson.dumps(node.attrs)
				data2 = simplejson.loads(data2)
				for key, value in data2.iteritems():
					if key == 'data-user-id' and value not in userid_nodes:
						#temp_node =  '               {"user": %s}\n' % (value)
						userid_nodes.append(value)
						#f.write(temp_node)
			for i in range(0,len(userid_nodes)):
				if i == len(userid_nodes)-1:
					temp_node =  '        {"user": %s}\n      ]\n     }\n' % (userid_nodes[i])
					f.write(temp_node)
				else:
					temp_node =  '        {"user": %s},\n' % (userid_nodes[i])
					f.write(temp_node)


def overall_print_dict(html):
	soup = BeautifulSoup(html)
	node = soup.find("ul", "stats")

	temp_str_node = ''
	temp_node_pre_r = ''
	temp_node_pre_f = ''
	if node is not None:
		for li in node.find_all("li"):
			if 'js-stat-retweets' in li['class'] and 'stat-count' in li['class'] and  'js-stat-count' in li['class']:
				retweets = ''.join([c for c in li.get_text() if is_number(c)])
				temp_node_pre_r += '{"retweets": %s}' % (retweets)
				temp_str_node += temp_node_pre_r
			if 'js-stat-count' in li['class'] and 'js-stat-favorites' in li['class'] and 'stat-count' in li['class']:
				favorites = ''.join([c for c in li.get_text() if is_number(c)])
				temp_node_pre_f += '{"favorites": %s}' % (favorites)
				temp_str_node += temp_node_pre_f

	if len(temp_str_node) > 5:
		f.write(' {"metadata": [\n')
		if len(temp_node_pre_r) > 5 and len(temp_node_pre_f) > 5:
			temp_str_node = '   %s,\n   %s,\n' % (temp_node_pre_r,temp_node_pre_f)
			f.write('%s' % (temp_str_node))
			return 3
		elif len(temp_node_pre_r) > 5:
			temp_str_node = '   %s,\n' % (temp_node_pre_r)
			f.write('%s' % (temp_str_node))
			return 2
		elif len(temp_node_pre_f) > 5:
			temp_str_node = '   %s,\n' % (temp_node_pre_f)
			f.write('%s' % (temp_str_node))
			return 1
	else:
		return 0

def save_filter_dict(itr_zip, csl):
	twitter_ids = []
	for user, timestamps, tweet_id, tweet in itr_zip:
		# only track values that have links in them
		if 'http' in tweet:
			temp_node_pre =  '{"query": "%s", "user": %s, "time_created": %s, "tweet_id": %s, "urls": "%s", "data": [' % (csl, user, timestamps, tweet_id, tweet)
			temp_node = temp_node_pre.replace('\n', '')
			temp_node = '%s\n' % (temp_node)
			#n_s = temp_node.encode('ascii', 'ignore')
			f.write(temp_node.encode("utf-8"))
			twitter_ids.append(tweet_id)
			#f.write('       More Tweet Data\n')
			get_tweet_data(tweet_id)

	return twitter_ids

for c_s_l in crowdsource_site_list:
	# abstract into timeline function
	val = 'https://twitter.com/i/search/timeline?q=%s&composed_count=1&include_available_features=1&include_entities=1&include_new_items_bar=true&interval=1&f=realtime' % (c_s_l)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.35)
	data = r.text
	del r
	data1 = simplejson.loads(data)
	for key, value in data1.iteritems():
		#metadata in tweet stream
		if key == 'items_html':
			soup = BeautifulSoup(value)
			#data-tweet-id
			#"dir": data_val
			#data-time
			data_val = re.compile("^-?[a-zA-Z0-9]+$")
			testing = soup.find_all(data_val)
			nodes = soup.find_all(attrs={"data-tweet-id": data_val})
			unfiltered_userid_nodes = soup.find_all(attrs={"data-user-id": data_val})
			unfiltered_nodes_tweets = soup.find_all(attrs={"class":"js-tweet-text tweet-text"})
			unfiltered_timestamps = soup.find_all(attrs={"data-time": data_val})
			nodes_tweets = []
			tweet_id_in_order = []
			userid_nodes = []
			timestamps = []
			testing_nodes = []

			for test in testing:
				data2 = simplejson.dumps(test.attrs)
				data2 = simplejson.loads(data2)
				for key, value in data2.iteritems():
					if 'data-expanded-url' in key and value not in testing_nodes:
						testing_nodes.append(value)

			for timestamp in unfiltered_timestamps:
				data2 = simplejson.dumps(timestamp.attrs)
				data2 = simplejson.loads(data2)
				for key, value in data2.iteritems():
					if key == 'data-time':
						timestamps.append(value)
			
			for tweet in unfiltered_nodes_tweets:
				urls_to_crawl = ''
				unfilt_tweet = tweet.get_text()
				urls_list = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', unfilt_tweet)

				for url in urls_list:
					matches = [t_url for t_url in testing_nodes if url_comparison(t_url, url)]
					urls_to_crawl += '%s,' % (matches)
				
				if len(urls_to_crawl) > 2:
					nodes_tweets.append(urls_to_crawl)

			for node in nodes:
				data2 = simplejson.dumps(node.attrs)
				data2 = simplejson.loads(data2)
				for key, value in data2.iteritems():
					if key == 'data-tweet-id' and value not in tweet_id_in_order:
						tweet_id_in_order.append(value)

			for node in nodes:
				data2 = simplejson.dumps(node.attrs)
				data2 = simplejson.loads(data2)
				for key, value in data2.iteritems():
					if key == 'data-user-id' and value not in userid_nodes:
						userid_nodes.append(value)

			tweet_ziped = zip(userid_nodes, timestamps, tweet_id_in_order, nodes_tweets)
			ids = save_filter_dict(tweet_ziped, c_s_l)
			#pprint.pprint(ids)
f.close()

end = time.time()
duration = end - init
print 'Duration:', duration , '\n'