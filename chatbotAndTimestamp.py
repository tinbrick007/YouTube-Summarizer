import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from youtube_transcript_api import YouTubeTranscriptApi
import pyttsx3
import re

nltk.download('stopwords')
nltk.download('punkt')

# Part 1: Get YouTube Transcript
def get_youtube_transcript(youtube_link):
    global transcript
    # Extract video ID from the YouTube link
    if "youtu.be" in youtube_link:
        video_id = youtube_link.split("/")[-1].split("?")[0]
    elif "youtube.com" in youtube_link:
        video_id = youtube_link.split("v=")[-1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube link format")

    # Get transcript using the video ID
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text_transcript = ' '.join([entry['text'] for entry in transcript])
    return text_transcript

youtube_link = 'https://youtu.be/Y6e_m9iq-4Q?si=BTFd2mbGKPKeLwqO'
transcript_result = get_youtube_transcript(youtube_link)
paragraph = transcript_result

# Part 2: Print Time Function
def print_time(search_word, time):
    print(f"mentioned at:")
    # calculate the accurate time according to the video's duration
    for t in time:
        hours = int(t // 3600)
        min = int((t // 60) % 60)
        sec = int(t % 60)
        print(f"{hours:02d}:{min:02d}:{sec:02d}")

# Part 3: Preprocess Transcript
data = [t['text'] for t in transcript]
data = [re.sub(r"[^a-zA-Z0-9]", "", line) for line in data]

# Part 4: Find Word in Transcript
def find_word_in_transcript(search_word, transcript):
    pattern = re.compile(rf'\b{re.escape(search_word)}\b', re.IGNORECASE)
    
    closest_match = None
    min_distance = float('inf')

    for entry in transcript:
        text = entry['text']
        match = re.search(pattern, text)
        
        if match:
            distance = abs(len(text) - len(search_word))
            if distance < min_distance:
                min_distance = distance
                closest_match = entry

    return closest_match['start'] if closest_match else None


# Part 5: TF-IDF Vectorizer and Answer Query Function
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return [word for word in words if word.isalnum() and word not in stop_words]

def create_vectorizer(text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(text)
    return vectors, vectorizer

def answer_query(query, vectors, vectorizer):
    query_vector = vectorizer.transform([query])
    similarity = cosine_similarity(query_vector, vectors)
    max_similarity_index = similarity.argmax()
    return paragraph_sentences[max_similarity_index]

# Preprocess the paragraph
paragraph_sentences = sent_tokenize(paragraph)
processed_paragraph = [' '.join(preprocess_text(sentence)) for sentence in paragraph_sentences]

# Create TF-IDF vectors and vectorizer
tfidf_vectors, tfidf_vectorizer = create_vectorizer(processed_paragraph)

# Chatbot loop
while True:
    global response
    user_query = input("Ask me a question (or type 'exit' to end): ")
    if user_query.lower() == 'exit':
        break

    # Preprocess the user query
    processed_query = ' '.join(preprocess_text(user_query))
    
    # Find the response in the transcript using keyword matching
    response_entry = None
    for entry in transcript:
        text = entry['text']
        if all(keyword in text.lower() for keyword in processed_query.split()):
            response_entry = entry
            break

    # Print the response and timestamp if found
    if response_entry:
        response = response_entry['text']
        print("Answer:", response)
        print("Timestamp:", response_entry['start'])
    else:
        print("Info not found in the text.")
