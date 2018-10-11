import tweepy
import socket
import requests
import time
from authentication import authentication  # Consumer and access token/key
from database_parser import query_db
from threading import Thread
import dataset
import json

db = dataset.connect("sqlite:///tweets.db")
table = db["tweets"]


"""
A comma-separated list of phrases which will be used to determine what Tweets will be delivered on the stream. 
A phrase may be one or more terms separated by spaces, and a phrase will match if all of the terms in the phrase are present in the Tweet, regardless of order and ignoring case. 
By this model, you can think of commas as logical ORs, while spaces are equivalent to logical ANDs (e.g. ‘the twitter’ is the AND twitter, and ‘the,twitter’ is the OR twitter).
"""
keyword_tracked = input("What are the keywords you want to track ? : ")

class TwitterStreamListener(tweepy.StreamListener):
	""" A listener handles tweets are the received from the stream
	Here, tweets are inserted into a sqlite db and calls the query_db function in a thread 
	so that it's able to keep up with the tweet flow
	"""

	def on_status(self, status):
		tweet_message, tweet_id = get_tweet(status)
		user_screen_name = get_user_informations(status)


		table.insert(dict(
			tweet_id = tweet_id,
			tweet_message = tweet_message,
			user_screen_name = user_screen_name,
		
		))
		
		#threading to avoid getting kicked out of twitter API if our sentiment analysis and reply to tweets can't keep up with the tweet flow
		thr = Thread(target=query_db) 
		thr.start()
	# Twitter error list : https://dev.twitter.com/overview/api/response-codes
	
	def on_error(self, status_code):
		if status_code == 403:
			print("The request is understood, but it has been refused or access is not allowed. Limit is maybe reached")
			return False


def get_tweet(tweet):
	print("Tweet Message : " + tweet.text)
	
	
	tweet_message = tweet.text
	tweet_id = tweet.id_str
	# Display sender and mentions user
	if hasattr(tweet, 'retweeted_status'):
		print("Tweet send by : " + tweet.retweeted_status.user.screen_name)
		#print("Original tweet ID :" + tweet.retweeted_status.id_str)

		#tweet_id = tweet.retweeted_status.id_str
		#user_screen_name = tweet.retweeted_status.user.screen_name
		
		# for screenname in tweet.retweeted_status.entities['user_mentions']:
		# 	print("Mention user: " + str(screenname['screen_name']))

	return tweet_message, tweet_id
		

def get_user_informations(tweet):
	print("User ID \t:" + str(tweet.user.id))
	print("User Name \t:" + tweet.user.name)
	print("User Screen name \t:" + tweet.user.screen_name)

	
	user_screen_name = tweet.user.screen_name

	# if hasattr(tweet.user, 'time_zone'):
	# 	print("User Time zone \t:", tweet.user.time_zone)
	# 	print("User UTC Offset \t:" + str(tweet.user.utc_offset))

	# 	print("User Status count \t:" + str(tweet.user.statuses_count))
			
	# 	print("User Description \t:", tweet.user.description)
	# 	print("User Follower count \t:" + str(tweet.user.followers_count))
	# 	print("User Created at \t:" + str(tweet.user.created_at))
	
	return user_screen_name
	
if __name__ == '__main__':
	
	# Get access and key from another class
	auth = authentication()

	consumer_key = auth.getconsumer_key()
	consumer_secret = auth.getconsumer_secret()

	access_token = auth.getaccess_token()
	access_token_secret = auth.getaccess_token_secret()

	# Authentication
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.secure = True
	auth.set_access_token(access_token, access_token_secret)
	
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=5)

	streamListener = TwitterStreamListener()
	myStream = tweepy.Stream(auth=api.auth, listener=streamListener)

	myStream.filter(track=[keyword_tracked], async=True)


