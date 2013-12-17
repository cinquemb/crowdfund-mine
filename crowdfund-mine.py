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
requests.adapters.DEFAULT_RETRIES = 10

_tmp_file = '%s.json' % (init)
URL_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../social-non-profit-data'))

#uncomment for later tests

f_tweet = open("final_mined_data/0.json","r+")

data = simplejson.load(f_tweet)
max_tweets = len(data['data'])


crowdsource_site_list = ['startsomegood', 'indiegogo', 'kickstarter']

def crowd_fund_comparison(title,site):
	if title.find(site) is not -1:
		return True
	else:
		return False

def check_crowd_fund_url(urls):
	'''
		Follow urls from within tweet and return url and site and status (if url is for crowdfunding) for each url 
	'''
	c_c_f_u_list = [] 
	for url in urls:
		c_c_f_u_node = [] #0:soup,1:site,2:status(true or false),3:time
		r = requests.get(url, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=10, verify=False)
		scrape_time = time.time()
		sleep(.35)
		data = r.text
		soup = BeautifulSoup(data)
		_title = soup.title.string.lower()

		matches = [site for site in crowd_fund_comparison if crowd_fund_comparison(_title, site)]
		if matches:
			temp_match_list = [soup, matches[0], True, scrape_time]
			c_c_f_u_node.append(temp_match_list)
		else:
			temp_match_list = [soup, matches[0], False, scrape_time]
			c_c_f_u_node.append()
		c_c_f_u_list.append(c_c_f_u_node)

	return c_c_f_u_list

def parse_startsomegood(html_soup):
	'''
	for startsomegood_val_list
		0: tipping point goal
		1: raised dollars
		2: number of backers
		3: raised dollars
		4: days left
	'''
	startsomegood_val_list = []
	startsomegood_list = html_soup.find_all('span',attrs={"class": 'num'})
	#to get tipping point goal
	startsomegood_list_tl_price = html_soup.find_all(class_='tl_price')
	for tp_goal in startsomegood_list_tl_price:
		tp_goal_filt = re.split('\$', tp_goal.text.replace('  ',''))
		#goal
		goal = '$%s' % (tp_goal_filt[1])
		startsomegood_val_list.append(goal)
		break

	'''
	for startsomegood_list
		0: raised dollars
		1: number of backers
		2: raised dollars
		3: days left
	'''
	for data_node in startsomegood_list:
		data_node_val_filt = data_node.text.replace(' ','').replace('\n','')
		#number_list = test.find_all('span',attrs={"class": 'num'})
		#pprint.pprint(test_1)
		startsomegood_val_list.append(data_node_val_filt)

	# to may length of 4
	del startsomegood_val_list[3]
	return startsomegood_val_list

def parse_indiegogo(html_soup):
	'''
		0: goal
		1: raised amount
		2: total backers
		3: days left
	'''
	indiegogo_val_list = []
	indiegogo_backers_list = html_soup.select('section.perks > ul > a > li')
	
	#goal
	goal = html_soup.select('p.money-raised > span.currency > span')
	for go in goal:
		indiegogo_val_list.append(go.text)
		break
	#raised 
	raised = html_soup.select('p#big-goal > span.amount > span.currency > span')
	for rai in raised:
		indiegogo_val_list.append(rai.text)
		break

	indiegogo_backers_nodes = []
	for backers_node in indiegogo_backers_list:
		dummy = re.split(' ', backers_node.select('p.fl.claimed.big-perk-button')[0].text)
		if int(dummy[0]) != 0:
			indiegogo_backers_nodes.append(int(dummy[0]))

	total_backers = sum(indiegogo_backers_nodes)
	indiegogo_val_list.append(total_backers)

	#days left
	days_left = html_soup.select('p.days-left > span.amount')
	for day in days_left:
		indiegogo_val_list.append(day.text)
		break

	return indiegogo_val_list

def parse_kickstarter(html_soup):
	'''
		0: goal
		1: raised amount
		2: total backers
		3: days left
	'''
	kickstarter_val_list = []
	#goal
	goal =  html_soup.find_all('meta',attrs={"property": "twitter:label1"})
	for go in goal:
		go = re.split(' ',go['content'].encode("utf-8"))
		kickstarter_val_list.append(go[2])
		break
	#raised 
	raised = html_soup.find_all('data',attrs={"class": "Project301281478","itemprop": "Project[pledged]"})
	for rai in raised:
		kickstarter_val_list.append(rai.text.encode("utf-8"))
		break
	#backers (count total to get contributors)
	backers = html_soup.find_all('data',attrs={"class": "Project301281478","itemprop": "Project[backers_count]"})
	for back in backers:
		kickstarter_val_list.append(back.text)
		break
	#pprint.pprint(testing)
	#testing = soup.find_all('span',attrs={"class": 'num'})
	#days left
	days_left = html_soup.find_all('meta',attrs={"property": "twitter:data2"})
	for day in days_left:
		kickstarter_val_list.append(day['content'])
		break
	

	return kickstarter_val_list

def parse_crowdfund_site(tweet_node):
	'''
		Return crowdfund data from page if available, 
		time page is scraped, twitter user, 
		twitter status ID
	'''
	p_c_s_d_list = []
	json_data = simplejson.loads(tweet_node)
	_urls = re.split(',', json_data['urls'])
	checked_data = check_crowd_fund_url(_urls)
	for node in checked_data:
		if node[2] is True:
			if node[1] == 'startsomegood':
				return_data_node = parse_startsomegood(node[0])
				p_c_s_d_list.append([json_data, return_data_node, node[3]])
			elif node[1] == 'indiegogo':
				return_data_node = parse_indiegogo(node[0])
				p_c_s_d_list.append([json_data, return_data_node, node[3]])
			elif node[1] == 'kickstarter':
				return_data_node = parse_kickstarter(node[0])
				p_c_s_d_list.append([json_data, return_data_node, node[3]])

	return p_c_s_d_list
def update_crowdfund_data(p_c_s_d):
	'''
		grabs any previous data from files assocaited with previous p_c_s_d nodes returned, 
		and creates a new file with updated data (merge lists)
	'''

	for p_node in p_c_s_d:
		temp_node_pre =  '{"goal_amount": "%s", "raised_amount": "%s", "total_backers": %s, "days_left": %s, "time_parsed": %s}' % (p_node[1][0].encode("utf-8"), p_node[1][1].encode("utf-8"), p_node[1][2], p_node[1][3], p_node[2])

		temp_node_sum = p_node[0] + simplejson.loads(temp_node_pre)
		pprint.pprint(temp_node_sum)

def save_crowdfund_data(u_c_d):
	'''
		create json data for node, and write to file
	'''
	pass

for i in range(0,max_tweets):
	tweet_node = data['data'][i]
	p_c_s_d_list = parse_crowdfund_site(tweet_node)
	update_crowdfund_data(p_c_s_d_list)


end = time.time()
duration = end - init
print 'Duration for crowdfund data mining of ', html_file ,':', duration , '\n'