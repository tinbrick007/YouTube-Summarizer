from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration

def get_youtube_transcript(youtube_link):
    video_id = youtube_link.split("v=")[-1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text_transcript = ' '.join([entry['text'] for entry in transcript])
    return text_transcript

def get_summary(transcript):
    # Use a specific BART model for summarization
    model_name = "facebook/bart-large-cnn"
    
    # Load BART model and tokenizer
    model = BartForConditionalGeneration.from_pretrained(model_name)
    tokenizer = BartTokenizer.from_pretrained(model_name)
    
    # Tokenize and summarize the text
    inputs = tokenizer.encode("summarize: " + transcript, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # Print the summary
    print("Summary:")
    print(summary)

# Example usage:
youtube_link = 'https://www.youtube.com/watch?v=pxiP-HJLCx0'
transcript_result = get_youtube_transcript(youtube_link)
get_summary(transcript_result)
