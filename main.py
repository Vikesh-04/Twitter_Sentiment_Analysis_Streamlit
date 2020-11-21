import streamlit as st
import numpy as np
import pandas as pd
import time
import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
import plotly.express as px
plt.style.use('fivethirtyeight')

def authentication(myfile):	
	consumerKey = myfile['API key'][0]
	consumerSecret = myfile['API secret key'][0]
	accessToken = myfile['Access token'][0]
	accessTokenSecret = myfile['Access token secret'][0]
	authenticate = tweepy.OAuthHandler(consumerKey,consumerSecret) 
	authenticate.set_access_token(accessToken, accessTokenSecret)
	api = tweepy.API(authenticate, wait_on_rate_limit = True)
	return api

def search_twitter_handle(api,twitter_handle,count):
	posts = api.user_timeline(screen_name=twitter_handle, count = count, lang ="en", tweet_mode="extended")
	return posts

def search_hashtag(api,hashtag,date,count):
	posts=tweepy.Cursor(api.search,q=[hashtag],lang='en',since=date).items(count)
	return posts

def make_dataframe(flag,posts):
	if flag==0:
		df = pd.DataFrame([tweet.text for tweet in posts], columns=['Tweets'])
	else:
		df = pd.DataFrame([tweet.full_text for tweet in posts], columns=['Tweets'])
	df['Clean_Tweets'] = df['Tweets'].apply(cleanTxt)    
	df['Subjectivity'] = df['Clean_Tweets'].apply(getSubjectivity)
	df['Polarity'] = df['Clean_Tweets'].apply(getPolarity)
	df['Analysis'] = df['Polarity'].apply(getAnalysis)
	return df

def cleanTxt(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
    text = re.sub('#', '', text) # Removing '#' hash tag
    text = re.sub('RT[\s]+', '', text) # Removing RT
    text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink 
    return text

def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text):
    return  TextBlob(text).sentiment.polarity

def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

def word_cloud_chart(df):
	allWords = ' '.join([twts for twts in df['Clean_Tweets']])	
	wordCloud = WordCloud(width=500, height=300, random_state=21, max_font_size=110).generate(allWords)
	fig, ax = plt.subplots()
	ax.imshow(wordCloud, interpolation="bilinear")
	ax.axis('off')
	st.pyplot(fig)

def bar_chart(df):
	fig, ax = plt.subplots(figsize=(10,5))
	ax =df['Analysis'].value_counts().plot(kind='bar')
	ax.grid(False)
	st.pyplot(fig)

page_bg_img = '''
<style>
body {
background-image: url("https://www.abc.net.au/news/image/11769268-3x2-940x627.png");
background-size: cover;
}
</style>
'''
def main():
	st.markdown(page_bg_img, unsafe_allow_html=True)
	myfile = pd.read_excel(r"C:\Users\vikesh\Desktop\mytwitter.xlsx")
	api=authentication(myfile)
	st.markdown("<h1 style='text-align: center;'>Live Twitter Dashboard</h1>", unsafe_allow_html=True)
	choice = st.selectbox("Fetch tweets using ",("Hashtag", "Twitter handle") )
	if choice == 'Hashtag': 
		hashtag=st.text_input("Enter Hashtag")
		date = st.date_input("Fetch Tweets since date")
		count = st.slider("Fetch count",min_value=1, max_value=500,value=50)
		twitter_handle=''
	else:
		twitter_handle = st.text_input('Enter twitter handle')
		count = st.slider("Fetch count",min_value=1, max_value=500,value=50)
		hashtag=''

	if st.button('Click to fetch'):
		if hashtag!='' or twitter_handle!='':	
			with st.spinner('Wait while it fetches the tweets...'):
				time.sleep(5)
			if choice == 'Hashtag':
				posts=search_hashtag(api,hashtag,date,count)
				st.header("Showing result for "+'#'+hashtag)
				df=make_dataframe(0,posts)
			else:			
				posts=search_twitter_handle(api,twitter_handle,count)
				st.header("Showing result for "+'@'+twitter_handle)
				df=make_dataframe(1,posts)
			sentiment_result = st.beta_expander("Click here to see the Tweets")
			sentiment_result.table(df)
			st.markdown("<h1 style='text-align: center;'>Sentiment analysis</h1>", unsafe_allow_html=True)
			st.header("Most occuring words")
			word_cloud_chart(df)
			st.header("Tweets count by sentiment")
			bar_chart(df)
		else:
			st.warning('Please enter your input')

if __name__ == '__main__':
	main()