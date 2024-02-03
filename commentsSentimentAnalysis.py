import os
import json
import nltk

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
# Download the VADER lexicon
nltk.download('vader_lexicon')


# Set up YouTube API key
api_key = "YOUR_API_KEY"

# Set up YouTube service
youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_comments(video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    )
    
    while request:
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        request = youtube.commentThreads().list_next(request, response)

    return comments

def perform_sentiment_analysis(comments):
    sia = SentimentIntensityAnalyzer()
    sentiments = []

    for comment in comments:
        sentiment_score = sia.polarity_scores(comment)
        sentiment = "positive" if sentiment_score["compound"] >= 0 else "negative"
        sentiments.append((comment, sentiment))

    return sentiments

def main():
    video_url = "https://www.youtube.com/watch?v=TNQsmPf24go"
    
    # Extract video ID from the URL
    video_id_parts = video_url.split("v=")
    if len(video_id_parts) > 1:
        video_id = video_id_parts[1]
        
        # Extract comments
        comments = get_video_comments(video_id)

        # Perform sentiment analysis
        sentiments = perform_sentiment_analysis(comments)
        countP = 0
        countN = 0
        # Display results
        for comment, sentiment in sentiments:
            print(f"Comment: {comment}")
            print(f"Sentiment: {sentiment}\n")
            if(sentiment == 'positive') : 
                countP+=1
            else :
                countN+=1
            
        print(f"{round((countP*100)/(countP+countN),2)} % viewers found this useful.")


    else:
        print("Error: Video ID not found in the URL.")

if __name__ == "__main__":
    main()
