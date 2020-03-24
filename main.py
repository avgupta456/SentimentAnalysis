import twitter
import keys

import csv
import time

key_list = keys.get_keys()
CONSUMER_KEY = key_list[0]
CONSUMER_SECRET = key_list[1]
TOKEN_KEY = key_list[2]
TOKEN_SECRET = key_list[3]

# initialize api instance
twitter_api = twitter.Api(consumer_key=CONSUMER_KEY,
                        consumer_secret=CONSUMER_SECRET,
                        access_token_key=TOKEN_KEY,
                        access_token_secret=TOKEN_SECRET)

# test authentication
print(twitter_api.VerifyCredentials())

#modify to your own path
corpusFile = "C:\\Users\\Abhijit\\Documents\\Github\\SentimentAnalysis\\corpus.csv"
tweetDataFile = "C:\\Users\\Abhijit\\Documents\\Github\\SentimentAnalysis\\tweets.csv"

def buildTestSet(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count = 100)

        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)

        return [{"text":status.text, "label":None} for status in tweets_fetched]
    except:
        print("Unfortunately, something went wrong..")
        return None

def buildTrainingSet(corpusFile, tweetDataFile):
    corpus = []

    with open(corpusFile,'r') as csvfile:
        lineReader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        for row in lineReader: corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})

    sleep_time = 900/180 #rate limit

    for tweet in corpus:
        try:
            csvfile = open(tweetDataFile, 'a', newline='')
            linewriter = csv.writer(csvfile, delimiter=',', quotechar="\"")

            status = twitter_api.GetStatus(tweet["tweet_id"])
            print("Tweet fetched: " + status.text)

            linewriter.writerow([tweet["tweet_id"], status.text, tweet["label"], tweet["topic"]])
            csvfile.close()

            time.sleep(sleep_time)
        except: continue

trainingData = buildTrainingSet(corpusFile, tweetDataFile)
