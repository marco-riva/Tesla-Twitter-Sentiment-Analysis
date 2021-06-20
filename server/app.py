import nltk
import json
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import mysql.connector
from dateutil import parser
import pandas as pd
import func_utils
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt


consumer_key = 'sBx5o18FPqxTJ92D9BMMbRlDb'
consumer_secret = 'p8TBarSZmbtzEJCWHhr9R6GsonWz2FNoQsCvDIo8ARQuixrPl9'
access_token_key = '1249770961496207360-NwRkBUSZrCuIlHgreggXOcFjbZwLrI'
access_token_secret = 'McdjnZ9ZTMbkvSuQrPtEkQaUd76pePBpIravExn9e08ok'

HOST = '127.0.0.1'
USER = 'root'
PSSWD = 'aloha'
DATABASE = 'twitter'

# load pipeline with vectorizer and Logistic Regression model

optimized_lr = pickle.load(open("../optimized_lr.pickle", "rb"))

# Make database function
def make_db():
    # Create connection 
    twitter_db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PSSWD
        )
    cursor = twitter_db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS twitter")

    # Create table
    twitter_db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PSSWD,
        database=DATABASE
    )
    cursor = twitter_db.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS tweets(
                id int(11) NOT NULL AUTO_INCREMENT,
                tweet_id varchar(250) DEFAULT NULL,
                screen_name varchar(128) DEFAULT NULL,
                created_at timestamp NULL DEFAULT NULL,
                pred varchar(128) DEFAULT NULL,
                pred_proba_pos varchar(128) DEFAULT NULL,
                pred_proba_neutr varchar(128) DEFAULT NULL,
                pred_proba_neg varchar(128) DEFAULT NULL,
                text text, PRIMARY KEY (id)
                ) CHARSET=utf8
                """)

# ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8

    cursor.close()
    twitter_db.close()


# Store statuses streamed by Tweepy into a MySQL database
def store_data(created_at, text, screen_name, tweet_id, pred, pred_proba_pos, pred_proba_neutr, pred_proba_neg):
    twitter_db = mysql.connector.connect(host=HOST, 
                                         user=USER, 
                                         passwd=PSSWD, 
                                         db=DATABASE, 
                                         charset="utf8")
    cursor = twitter_db.cursor()
    insert_query = "INSERT INTO tweets (tweet_id, screen_name, created_at, pred, pred_proba_pos, pred_proba_neutr, pred_proba_neg, text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (tweet_id, screen_name, created_at, pred, pred_proba_pos, pred_proba_neutr, pred_proba_neg, text))
    twitter_db.commit()
    cursor.close()
    twitter_db.close()
    return

# Listener class to stream tweets
class listener(StreamListener): 
    count = 0

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
                    
    def on_error(self, status_code):
        if status_code == 420:
            return False

    def on_status(self, status):
        try:
            status.retweeted_status
            print('Skip RT')
        except AttributeError:
            try:
                text = status.extended_tweet['full_text'].encode('ascii', 'ignore')
            except AttributeError as e:
                text = status.text.encode('ascii', 'ignore')

            tweet_id = status.id
            id_str = status.id_str
            created_at = status.created_at
            processed_text = func_utils.tweet_cleaning(text)
            if processed_text is not None:
                X=pd.Series(processed_text)
                pred = optimized_lr.predict(X)[0]
                pred_proba = optimized_lr.predict_proba(X)
                pred_proba_neg = str(round(pred_proba[0][0], 4))
                pred_proba_neutr = str(round(pred_proba[0][1], 4))
                pred_proba_pos = str(round(pred_proba[0][2], 4))                

            screen_name = status.user.screen_name
            user_created_at = status.user.created_at
            user_location = status.user.location
            user_description = status.user.description
            user_followers_count =status.user.followers_count

            longitude = None
            latitude = None
            if status.coordinates:
                longitude = status.coordinates['coordinates'][0]
                latitude = status.coordinates['coordinates'][1]

            retweet_count = status.retweet_count
            favorite_count = status.favorite_count

            #insert the data into the MySQL database
            store_data(created_at, 
                       text, 
                       screen_name, 
                       tweet_id, 
                       pred, 
                       pred_proba_pos, 
                       pred_proba_neutr, 
                       pred_proba_neg)
            
            self.count += 1
            #print out a message to the screen that we have collected a tweet
            print("Tweet number " + str(self.count) + " collected at " + str(created_at))

            if self.count >= 10000:
                return False


# Generate database 
make_db()

# Authenticate to Twitter
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

 # Stream tweets live
twitter_stream = Stream(auth, listener(), tweet_mode='extended', lang='en')
twitter_stream.filter(languages=["en"], track=["tesla"])