from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import BartForConditionalGeneration, BartTokenizer
from flask_cors import CORS 
import traceback
import os
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from googleapiclient.discovery import build


app = Flask(__name__)
CORS(app) 

nltk.download('vader_lexicon')

# Set up YouTube API key and service
api_key = "AIzaSyCrzz8jJ-XGQ9UOApEN8ZDo0l58hUy3eeA"  # Use your API key here
youtube = build('youtube', 'v3', developerKey=api_key)

# Load BART model and tokenizer once
model_name = "facebook/bart-large-cnn"
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

def extract_video_id(youtube_url):
    if "youtu.be" in youtube_url:
        video_id = youtube_url.split("/")[-1].split("?")[0]
    elif "youtube.com" in youtube_url:
        video_id = youtube_url.split("v=")[-1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube URL format")
    return video_id

def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_list])
        return transcript
    except Exception as e:
        raise Exception(f"Error fetching transcript: {e}")

def get_summary(transcript):
    inputs = tokenizer.encode("summarize: " + transcript, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

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

# Function to perform sentiment analysis
def perform_sentiment_analysis(comments):
    sia = SentimentIntensityAnalyzer()
    sentiments = []

    for comment in comments:
        sentiment_score = sia.polarity_scores(comment)
        sentiment = "positive" if sentiment_score["compound"] >= 0 else "negative"
        sentiments.append(sentiment)

    return sentiments

# New route to analyze YouTube video comments
@app.route('/analyze_comments', methods=['GET'])
def analyze_comments():
    youtube_url = request.args.get('url')
    try:
        video_id = extract_video_id(youtube_url)
        comments = get_video_comments(video_id)
        sentiments = perform_sentiment_analysis(comments)
        return jsonify({'comments': comments, 'sentiments': sentiments})
    except Exception as e:
        app.logger.error('Error in comment analysis: %s\n%s', str(e), traceback.format_exc())
        return jsonify({'error': 'Error analyzing comments'}), 500


@app.route('/summary', methods=['GET'])
def summary():
    youtube_url = request.args.get('url')
    try:
        video_id = extract_video_id(youtube_url)
        transcript = get_youtube_transcript(video_id)
        summary_text = get_summary(transcript)
        return jsonify({'summary': summary_text})
    except Exception as e:
        app.logger.error('Error in summary generation: %s\n%s', str(e), traceback.format_exc())
        return jsonify({'error': 'Error fetching summary'}), 500

if __name__ == '__main__':
    app.run(debug=True)