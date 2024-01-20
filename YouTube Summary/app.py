from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import BartForConditionalGeneration, BartTokenizer
from flask_cors import CORS 
import traceback

app = Flask(__name__)
CORS(app) 

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