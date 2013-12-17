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

_tmp_file = '%s.json' % (init)
URL_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../social-non-profit-data'))
FUND_MINED_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fund_mined_data'))
fund_mined_data_string = '%s/%s' % (FUND_MINED_DATA_PATH,_tmp_file)

f_tweet = open("final_mined_data/0.json","r+")

data = simplejson.load(f_tweet)
max_tweets = len(data['data_tweets'])

crowdsource_site_list = ['startsomegood', 'indiegogo', 'kickstarter']

def crowd_fund_comparison(title,site):
	if title.find(site) is not -1:
		return True
	else:
		return False

#super hacky
def url_check(url,string):
	if url.find(string) is not -1:
		return True
	else:
		return False



def check_crowd_fund_url(urls):
	'''
		Follow urls from within tweet and return url and site and status (if url is for crowdfunding) for each url 
	'''
	c_c_f_u_list = [] 
	for url in urls:
		if url not in check_url_list:
			if len(url) > 5:
				url_orig = url
				c_c_f_u_node = [] #0:soup,1:site,2:status(true or false),3:time
				if url_check(url, '/posts/') and url_check(url, 'kickstarter'):
					url_temp = re.split('/posts/', url)
					print 'Url Hack Used'
					url = url_temp[0]
				r = requests.get(url, stream=False, headers={'User-Agent':'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}, timeout=20, verify=False)
				scrape_time = time.time()
				sleep(.35)
				data = r.text
				soup = BeautifulSoup(data)
				goal =  soup.find_all('meta',attrs={"property": "og:site_name"})
				_title_row = []
				for go in goal:
					#print go['content']
					_title_row.append(go['content'].encode("utf-8").lower())
					break

				if len(_title_row) > 0:
					_title = _title_row[0]
					matches = [site for site in crowdsource_site_list if crowd_fund_comparison(_title, site)]

					if matches:
						temp_match_list = [soup, matches[0], True, scrape_time]
						c_c_f_u_node.append(temp_match_list)
						check_url_list.append(url_orig)
						cache_temp_list.append(temp_match_list)
					else:
						temp_match_list = [soup, False, False, scrape_time]
						c_c_f_u_node.append(temp_match_list)
						check_url_list.append(url_orig)
						cache_temp_list.append(temp_match_list)
					
					c_c_f_u_list.append(c_c_f_u_node)
				else:
					continue
		else:
			url_cached = [i for i,x in enumerate(check_url_list) if x == url]
			#print 'Get Cached Data for Url At Index:', url_cached[0]
			c_c_f_u_list.append([cache_temp_list[url_cached[0]]])
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
	data_val = re.compile("^Project?[0-9]+$")
	raised = html_soup.find_all('data',attrs={"class": data_val,"itemprop": "Project[pledged]"})
	for rai in raised:
		kickstarter_val_list.append(rai.text.encode("utf-8"))
		break
	#backers (count total to get contributors)
	backers = html_soup.find_all('data',attrs={"class": data_val,"itemprop": "Project[backers_count]"})
	for back in backers:
		kickstarter_val_list.append(back.text)
		break
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
	json_data = tweet_node
	_urls = re.split(',', json_data['urls'])
	checked_data = check_crowd_fund_url(_urls)
	for node in checked_data:
		print len(node[0])
		#pprint.pprint(node[0])
		if node[0][2] is True:
			if node[0][1] == 'startsomegood':
				return_data_node = parse_startsomegood(node[0][0])
				p_c_s_d_list.append([json_data, return_data_node, node[0][3]])
			elif node[0][1] == 'indiegogo':
				return_data_node = parse_indiegogo(node[0][0])
				p_c_s_d_list.append([json_data, return_data_node, node[0][3]])
			elif node[0][1] == 'kickstarter':
				return_data_node = parse_kickstarter(node[0][0])
				p_c_s_d_list.append([json_data, return_data_node, node[0][3]])

	return p_c_s_d_list

def update_crowdfund_data(d_nodes):
	'''
		grabs any previous data from files assocaited with previous d_nodes nodes returned, 
		and creates a new file with updated data (merge lists)
	'''
	pass

def save_crowdfund_data(p_c_s_d):
	'''
		create json data for node, and write to file
	'''
	
	d_nodes = []
	for p_node in p_c_s_d:
		temp_node_dict =  {'goal_amount': p_node[1][0], 
			'raised_amount': p_node[1][1], 
			'total_backers': p_node[1][2], 
			'days_or_hours_left': int(p_node[1][3]), 
			'time_parsed': float(p_node[2])
		} 

		temp_node_sum = p_node[0].copy()
		temp_node_sum.update(temp_node_dict)
		d_nodes.append(simplejson.dumps(temp_node_sum))

	
	for node in d_nodes:
		f_m.write('%s,' % node)	

	return d_nodes

filtered_tweet_nodes = []
filtered_tweet_ids = []
for i in range(0,max_tweets):
	# filter out tweets that are the same?
	tweet_id = data['data_tweets'][i]['tweet_id']
	if data['data_tweets'][i]['query'] == 'startsomegood':
		continue

	if tweet_id not in filtered_tweet_ids:
		filtered_tweet_nodes.append(data['data_tweets'][i])
		filtered_tweet_ids.append(tweet_id)

max_nodes = len(filtered_tweet_nodes)
f_m = open(fund_mined_data_string,"w+")
check_url_list = []
cache_temp_list = []
for i in range(0,max_nodes):
	p_c_s_d_list = parse_crowdfund_site(filtered_tweet_nodes[i])
	save_crowdfund_data(p_c_s_d_list)

f_m.close()
end = time.time()
duration = end - init
print 'Duration for crowdfund data mining:', duration , '\n'