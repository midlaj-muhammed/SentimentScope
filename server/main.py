from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime, timedelta
import random  # For demo data

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["OPTIONS", "POST", "GET"],
        "allow_headers": ["Content-Type"]
    }
})

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    return text

def get_word_frequency(text, top_n=10):
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words and len(word) > 2]
    # Get frequency
    word_freq = Counter(tokens).most_common(top_n)
    return [{"word": word, "count": count} for word, count in word_freq]

@app.route('/analyze/url', methods=['POST', 'OPTIONS'])
def analyze_url():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("Received request:", request.get_json())  # Debug logging
        data = request.get_json()
        
        if not data:
            print("No JSON data received")  # Debug logging
            return jsonify({"error": "No JSON data received"}), 400
            
        url = data.get('url')
        
        if not url:
            print("URL is required")  # Debug logging
            return jsonify({"error": "URL is required"}), 400
            
        print(f"Analyzing URL: {url}")  # Debug logging
            
        # Fetch URL content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        
        if not text.strip():
            print("No text content found")  # Debug logging
            return jsonify({"error": "No text content found in the URL"}), 400
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Perform sentiment analysis
        blob = TextBlob(cleaned_text)
        sentiment_score = blob.sentiment.polarity
        
        # Determine sentiment
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Calculate confidence (normalize subjectivity)
        confidence = blob.sentiment.subjectivity
        
        # Get word frequency
        word_frequency = get_word_frequency(cleaned_text)
        
        result = {
            "sentiment": sentiment,
            "score": sentiment_score,
            "confidence": confidence,
            "wordFrequency": word_frequency
        }
        print("Analysis result:", result)  # Debug logging
        return jsonify(result)
        
    except requests.RequestException as e:
        print(f"Error fetching URL: {str(e)}")  # Debug logging
        return jsonify({"error": f"Error fetching URL: {str(e)}"}), 400
    except Exception as e:
        print(f"Error analyzing content: {str(e)}")  # Debug logging
        return jsonify({"error": f"Error analyzing content: {str(e)}"}), 500

@app.route('/analyze/hashtag', methods=['POST', 'OPTIONS'])
def analyze_hashtag():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("Received hashtag request:", request.get_json())  # Debug logging
        data = request.get_json()
        
        if not data:
            print("No JSON data received")  # Debug logging
            return jsonify({"error": "No JSON data received"}), 400
            
        hashtag = data.get('hashtag')
        
        if not hashtag:
            print("Hashtag is required")  # Debug logging
            return jsonify({"error": "Hashtag is required"}), 400
            
        print(f"Analyzing hashtag: {hashtag}")  # Debug logging

        # Analyze the hashtag text itself for base sentiment
        hashtag_words = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', hashtag)
        hashtag_text = ' '.join(hashtag_words).lower()
        base_sentiment = TextBlob(hashtag_text).sentiment.polarity

        # Use hashtag as seed for random number generation to ensure consistency
        random.seed(hashtag)

        # Generate timeline data
        now = datetime.now().replace(minute=0, second=0, microsecond=0)  # Round to nearest hour
        timeline = []
        
        # Base parameters - use hash of hashtag for consistency
        hashtag_hash = hash(hashtag)
        base_volume = 100 + abs(hashtag_hash % 900)  # Range: 100-1000
        trend_direction = 1 if hashtag_hash % 2 == 0 else -1
        
        for i in range(24):  # Last 24 hours
            hour = (now - timedelta(hours=23-i)).hour
            time = f"{hour:02d}:00"  # Use 24-hour format for consistency
            
            # Time-based volume adjustments
            time_factor = 1.0
            if 9 <= hour <= 22:  # Daytime hours
                time_factor = 1.5
            elif 23 <= hour or hour <= 4:  # Late night
                time_factor = 0.5
                
            # Use deterministic values based on hashtag and hour
            hour_seed = f"{hashtag}_{hour}"
            random.seed(hour_seed)
            
            # Calculate volume
            volume = int(base_volume * time_factor * (1 + random.uniform(-0.3, 0.3)))
            
            # Calculate sentiment
            time_progress = i / 23
            trend_component = trend_direction * (time_progress - 0.5) * 0.4
            random.seed(f"{hour_seed}_sentiment")
            noise = random.uniform(-0.2, 0.2)
            
            sentiment = max(-1, min(1, base_sentiment + trend_component + noise))
            
            timeline.append({
                "time": time,
                "sentiment": round(sentiment, 3),  # Round for consistency
                "volume": volume
            })
            
        # Calculate overall metrics
        total_volume = sum(t["volume"] for t in timeline)
        weighted_sentiment = sum(t["sentiment"] * t["volume"] for t in timeline) / total_volume
        
        # Determine overall sentiment
        if weighted_sentiment > 0.1:
            sentiment = "positive"
        elif weighted_sentiment < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Calculate confidence
        sentiment_std = (sum((t["sentiment"] - weighted_sentiment) ** 2 for t in timeline) / len(timeline)) ** 0.5
        volume_factor = min(1.0, total_volume / (1000 * 24))
        consistency_factor = 1 - sentiment_std
        confidence = round((volume_factor + consistency_factor) / 2, 3)  # Round for consistency
            
        result = {
            "sentiment": sentiment,
            "score": round(weighted_sentiment, 3),  # Round for consistency
            "confidence": confidence,
            "timeline": timeline
        }
        
        # Reset random seed
        random.seed()
        
        print("Hashtag analysis result:", result)  # Debug logging
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing hashtag: {str(e)}")  # Debug logging
        return jsonify({"error": f"Error analyzing hashtag: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
