import twitter

import csv
import time

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation

import keys

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

#modify to your own path
corpusFile = "C:\\Users\\Abhijit\\Documents\\Github\\SentimentAnalysis\\corpus.csv"
tweetDataFile = "C:\\Users\\Abhijit\\Documents\\Github\\SentimentAnalysis\\tweets.csv"

def getTest(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count = 100)

        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)

        return [(status.text, None) for status in tweets_fetched]
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

def getTrainingSet(tweetDataFile):
    training_set = []
    with open(tweetDataFile) as csvfile:
        lineReader = csv.reader(csvfile, delimiter=",", quotechar="\"")
        for row in lineReader: training_set.append((row[1], row[2]))
    return training_set

stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])

def processTweet(tweet):
    tweet = tweet.lower() # convert text to lower-case
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag
    tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
    return [word for word in tweet if word not in stopwords]

def processTweets(dataset):
    processed = []
    for tweet in dataset:
        processed.append((processTweet(tweet[0]),tweet[1]))
    return processed

def buildVocabulary(preprocessedTrainingData):
    all_words = []

    for (words, sentiment) in preprocessedTrainingData:
        all_words.extend(words)

    wordlist = nltk.FreqDist(all_words)
    word_features = wordlist.keys()

    return word_features

def extract_features(tweet):
    tweet_words = tweet[0]
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in tweet_words)
    return features

training = processTweets(getTrainingSet(tweetDataFile))
word_features = buildVocabulary(training)

trainingFeatures = nltk.classify.apply_features(extract_features, training)
NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)

raw_test = getTest("Uber")
test = processTweets(raw_test)
NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in test]

# get the majority vote
if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
    print("Overall Positive Sentiment")
    print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
else:
    print("Overall Negative Sentiment")
    print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")
