# How to obtain social crowdsoursing data #

- Use Twitter + PhantomJs?

- crowdsours site = {startsomegood, indigogo,  kickstarter}

- ex json: https://twitter.com/i/search/timeline?q={crowsourse site}&composed_count=1&include_available_features=1&include_entities=1&include_new_items_bar=true&interval=1&f=realtime

- ex to get full tweet data: https://twitter.com/austinmusic/status/{tweet id}

- ex to get twitter profile by profile id: https://twitter.com/account/redirect_by_id?id={ profile id}

# grab data-user-id values from below links #
- ex to get retweet activity for tweet of interest: https://twitter.com/i/activity/retweeted_popup?id={tweet id}
- ex to get favorited activity for tweet of interest: https://twitter.com/i/activity/favorited_popup?id={tweet id}

- scrape posts that have {crowsourse site} and urls in them

- check if the words non-profit is listed on {crowsourse site} page?

- scrape tweet of post:
	1) (amount/names) of followers of poster
	2) Favs/RT's of post:
		a) who
		b) follower amount/names (how far down the rabit hole/useful?)
	3) time posted

- scrape {crowsourse site} page with data over time period for how many backers, catergory, how much, time period (start/end time), past data on founder of project?

