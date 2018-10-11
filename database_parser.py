import sqlite3
from sentimentanalyzer import sentimentAnalyzer
from send_message_to_slack import send_message_to_slack
import shelve




word_list_to_detect = ['places','concert','fnac','ticketmaster']

def parse_tweet(tweets):
    """
    analyzes the sentiment of a tweet if it hasn't been done already and prints it if it's relevant (presence of negative or keywords)
    """
    already_parsed = shelve.open('already_parsed')

    for tweet in tweets:
        tweet_message = tweet[3]
        tweet_id = tweet[2]

        if tweet_id not in already_parsed.keys():
            already_parsed[tweet_id] = True    
            snt = sentimentAnalyzer(tweet_message)

            if snt['compound'] < 0:
                print(tweet_message)
                print(snt)
                #reply to tweet?

            elif any(word in tweet_message for word in word_list_to_detect):
                print(tweet_message)

    already_parsed.close()

def query_db():
    """
    fetches the lasts 3 tweets from the sqlite db so that if there's a high flow of incoming tweets
    added to the db, we don't miss any by just fetching the last one
    """

    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM "tweets" ORDER BY id DESC LIMIT 3')
    all_tweets = c.fetchall()
    conn.close()

    return parse_tweet(all_tweets)

    # conn.commit()
