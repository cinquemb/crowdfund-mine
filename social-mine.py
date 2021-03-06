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
import urllib

init = time.time()
requests.adapters.DEFAULT_RETRIES = 10

_tmp_file = '%s.json' % (init)
MINED_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mined_data'))
mined_data_string = '%s/%s' % (MINED_DATA_DIR,_tmp_file)
f = open(mined_data_string,"w+")

crowdsource_site_list = ['teb']#['startsomegood', 'indiegogo', 'kickstarter']

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
	sleep(.25)
	data = r.text
	data1 = simplejson.loads(data)
	general_print_dict(data1,'{"retweet')

def get_favorite_data(tweet_id):
	val = 'https://twitter.com/i/activity/favorited_popup?id=%s' % (tweet_id)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.25)
	data = r.text
	data1 = simplejson.loads(data)
	general_print_dict(data1, '{"favorite')

def get_tweet_data(tweet_id):
	val = 'https://twitter.com/i/status/%s' % (tweet_id)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.25)
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
		if key == 'htmlUsers':
			soup = BeautifulSoup(value, "lxml")
			data_val = re.compile("^[a-zA-Z0-9]+$")
			nodes = soup.find_all(data_val)
			userid_nodes = []
			for node in nodes:
				for key, value in node.attrs.iteritems():
					if key == 'data-user-id' and value not in userid_nodes:
						userid_nodes.append(value)

			#hackish to detect if there are Retweets/favorites but hidden users
			if len(userid_nodes) == 0:
				temp_node =  '        {"user": "Hidden"}\n      ]\n     }\n'
				f.write(temp_node)
			else:
				for i in range(0,len(userid_nodes)):
					if i == len(userid_nodes)-1:
						temp_node =  '        {"user": %s}\n      ]\n     }\n' % (userid_nodes[i])
						f.write(temp_node)
					else:
						temp_node =  '        {"user": %s},\n' % (userid_nodes[i])
						f.write(temp_node)


def overall_print_dict(html):
	soup = BeautifulSoup(html, "lxml")
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
	for user, timestamps, tweet_id, tweet, tweet_content in itr_zip:
		# only track values that have links in them
		if 'http' in tweet:
			temp_node_pre =  '{"query": "%s", "user": %s, "time_created": %s, "tweet_id": %s, "tweet_content_urlencoded": "%s", "urls": "%s", "data": [' % (csl, user, timestamps, tweet_id, tweet_content, tweet)
			temp_node = temp_node_pre.replace('\n', '')
			temp_node = '%s\n' % (temp_node)
			f.write(temp_node.encode("utf-8"))
			twitter_ids.append(tweet_id)
			get_tweet_data(tweet_id)

	return twitter_ids

timeline_data_nodes = []
for c_s_l in crowdsource_site_list:
	val = 'https://twitter.com/i/search/timeline?q=%s&composed_count=1&include_available_features=1&include_entities=1&include_new_items_bar=true&interval=1&f=realtime' % (c_s_l)
	r = requests.get(val, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
	sleep(.35)
	data = r.text
	del r
	temp_data = [data,c_s_l]
	timeline_data_nodes.append(temp_data)

for node in timeline_data_nodes:
	dump = node[0]
	source = node[1]
	data1 = simplejson.loads(dump)
	for key, value in data1.iteritems():
		#metadata in tweet stream
		if key == 'items_html':
			value1 = value.replace('&lt;', '<')
			value2 = '<html>%s</html>' % (value1.replace('&gt;','>').encode("utf-8"))
			soup = BeautifulSoup(value2, "lxml")
			nodes_tweets = []
			tweet_id_in_order = []
			userid_nodes = []
			timestamps = []
			tweet_content = []

			tweets = soup.select('li.js-stream-item.stream-item.stream-item.expanding-stream-item')
			for tweet in tweets:
				
				url_s = tweet.select('p.js-tweet-text.tweet-text > a.twitter-timeline-link')
				urls_to_crawl = ''
				if url_s:
					for url in url_s:
						if 'data-expanded-url' in url.attrs:
							urls_to_crawl += '%s,' % (url['data-expanded-url'])
						else:
							urls_to_crawl += '%s,' % (url['href'])
				else:
					continue

				check_tweet_text = tweet.find('p', class_="js-tweet-text tweet-text")
				if check_tweet_text is not None:
					tweet_text = tweet.find('p', class_="js-tweet-text tweet-text").get_text().encode('ascii', 'ignore')
				else:
					tweet_text = ''
					
				tweet_text_filtered = urllib.quote_plus(tweet_text)
				urls_to_crawl = urls_to_crawl.lstrip()
				tweet_id = tweet['data-item-id']
				user_id_l = tweet.select('div.tweet.original-tweet.js-stream-tweet.js-actionable-tweet.js-profile-popup-actionable.js-original-tweet')

				user_id = user_id_l[0]['data-user-id']
				time_l = tweet.select('span._timestamp.js-short-timestamp.js-relative-timestamp')
				if len(time_l) == 0:
					time_l = tweet.select('span._timestamp.js-short-timestamp')
				
				timestamp = time_l[0]['data-time']

				nodes_tweets.append(urls_to_crawl)
				tweet_id_in_order.append(tweet_id)
				userid_nodes.append(user_id)
				timestamps.append(timestamp)
				tweet_content.append(tweet_text_filtered)

			tweet_ziped = zip(userid_nodes, timestamps, tweet_id_in_order, nodes_tweets, tweet_content)
			ids = save_filter_dict(tweet_ziped, source)
			break
f.close()

end = time.time()
duration = end - init
print 'Duration for social data mining:', duration , '\n'