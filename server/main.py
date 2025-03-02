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
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import random
import os

# Configure NLTK data directory and download resources
def setup_nltk():
    nltk_dirs = [
        '/opt/render/nltk_data',  # Render's directory
        os.path.join(os.getcwd(), 'nltk_data'),  # Local directory
        os.path.expanduser('~/nltk_data')  # User's home directory
    ]
    
    # Add all possible NLTK directories to the search path
    for directory in nltk_dirs:
        if directory not in nltk.data.path:
            nltk.data.path.append(directory)
    
    print('NLTK search path:', nltk.data.path)
    
    # Define required NLTK resources
    resources = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'vader_lexicon': 'sentiment/vader_lexicon'
    }
    
    # Try to find or download each resource
    for resource, path in resources.items():
        try:
            nltk.data.find(path)
            print(f'✓ Found {resource} at {path}')
        except LookupError:
            print(f'Downloading {resource}...')
            try:
                # Try to download to the first available directory
                for directory in nltk_dirs:
                    try:
                        os.makedirs(directory, exist_ok=True)
                        nltk.download(resource, download_dir=directory, quiet=True)
                        print(f'✓ Downloaded {resource} to {directory}')
                        break
                    except (OSError, IOError) as e:
                        print(f'Failed to download to {directory}: {e}')
                        continue
            except Exception as e:
                print(f'Error downloading {resource}: {e}')
                raise

# Initialize NLTK on startup
print('Initializing NLTK...')
try:
    setup_nltk()
    print('NLTK initialization complete!')
except Exception as e:
    print(f'NLTK initialization error: {e}')
    # Log the error but don't prevent server startup

app = Flask(__name__)

# Configure CORS to allow all origins during development
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": False,
        "max_age": 120
    }
})

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', '', text)
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

def analyze_sentiment(text):
    # Initialize VADER sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Get VADER sentiment scores
    vader_scores = sia.polarity_scores(text)
    
    # Get TextBlob sentiment
    blob = TextBlob(text)
    textblob_sentiment = blob.sentiment.polarity
    
    # Combine VADER and TextBlob scores with weights
    # VADER is better for social media text, so we give it more weight
    compound_score = vader_scores['compound'] * 0.7 + textblob_sentiment * 0.3
    
    # Normalize to range [-1, 1]
    normalized_score = max(min(compound_score, 1.0), -1.0)
    
    # Calculate confidence based on:
    # 1. Agreement between VADER and TextBlob
    # 2. VADER's compound score magnitude
    # 3. TextBlob's subjectivity
    score_agreement = 1 - abs(vader_scores['compound'] - textblob_sentiment) / 2
    magnitude_confidence = abs(vader_scores['compound'])
    subjectivity_confidence = blob.sentiment.subjectivity
    
    confidence = (score_agreement * 0.4 + magnitude_confidence * 0.4 + subjectivity_confidence * 0.2)
    
    return {
        'score': normalized_score,
        'confidence': confidence,
        'vader_scores': vader_scores,
        'textblob_score': textblob_sentiment
    }

@app.route('/analyze/url', methods=['POST', 'OPTIONS'])
def analyze_url():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Log the raw request data
        print("Request headers:", dict(request.headers))
        print("Request body:", request.get_data(as_text=True))
        
        data = request.get_json()
        print("Parsed JSON data:", data)
        
        if not data:
            error_msg = "No JSON data received"
            print(error_msg)
            return jsonify({"error": error_msg}), 400
            
        url = data.get('url')
        print(f"Extracted URL: {url}")
        
        if not url:
            error_msg = "URL is required"
            print(error_msg)
            return jsonify({"error": error_msg}), 400
        
        if not isinstance(url, str):
            error_msg = f"URL must be a string, got {type(url)}"
            print(error_msg)
            return jsonify({"error": error_msg}), 400
            
        print(f"Analyzing URL: {url}")
            
        # Verify NLTK resources before proceeding
        required_resources = {
            'punkt': 'tokenizers/punkt',
            'stopwords': 'corpora/stopwords',
            'vader_lexicon': 'sentiment/vader_lexicon'
        }
        
        missing_resources = []
        for resource, path in required_resources.items():
            try:
                nltk.data.find(path)
            except LookupError:
                missing_resources.append(resource)
        
        if missing_resources:
            error_msg = f"NLTK resources not ready: {', '.join(missing_resources)}"
            print(error_msg)
            return jsonify({
                "error": "Server is initializing required resources. Please try again in a few moments.",
                "details": {
                    "type": "nltk_resource_error",
                    "missing_resources": missing_resources
                }
            }), 503
        
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
            print("No text content found")
            return jsonify({"error": "No text content found in the URL"}), 400
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Analyze sentiment
        sentiment_analysis = analyze_sentiment(cleaned_text)
        
        # Determine sentiment label
        score = sentiment_analysis['score']
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Get word frequency
        word_frequency = get_word_frequency(cleaned_text)
        
        result = {
            "sentiment": sentiment,
            "score": sentiment_analysis['score'],
            "confidence": sentiment_analysis['confidence'],
            "wordFrequency": word_frequency,
            "details": {
                "vader_scores": sentiment_analysis['vader_scores'],
                "textblob_score": sentiment_analysis['textblob_score']
            }
        }
        
        print("Analysis result:", result)
        return jsonify(result)
        
    except requests.RequestException as e:
        error_msg = f"Error fetching URL: {str(e)}"
        print(error_msg)
        return jsonify({
            "error": error_msg,
            "details": {
                "type": "request_error",
                "message": str(e)
            }
        }), 400
    except Exception as e:
        error_msg = str(e)
        error_type = "analysis_error"
        status_code = 500

        if "Resource" in error_msg and "not found" in error_msg:
            error_msg = "Server is initializing NLTK resources. Please try again in a few moments."
            error_type = "nltk_resource_error"
            status_code = 503  # Service Temporarily Unavailable

        print(f"Error: {error_msg}")
        print("Full error:", e)
        import traceback
        print("Traceback:", traceback.format_exc())

        return jsonify({
            "error": error_msg,
            "details": {
                "type": error_type,
                "message": str(e)
            }
        }), status_code

@app.route('/analyze/text', methods=['POST', 'OPTIONS'])
def analyze_text():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("Received text analysis request:", request.get_json())
        data = request.get_json()
        
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
            
        text = data.get('text')
        
        if not text:
            print("Text is required")
            return jsonify({"error": "Text is required"}), 400
            
        print(f"Analyzing text: {text}")

        # Clean the text
        cleaned_text = clean_text(text)
        
        # Get sentiment analysis
        sentiment_analysis = analyze_sentiment(cleaned_text)
        
        # Calculate overall sentiment
        score = sentiment_analysis['score']
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        result = {
            "sentiment": sentiment,
            "score": score,
            "confidence": sentiment_analysis['confidence'],
            "details": {
                "vader_scores": sentiment_analysis['vader_scores'],
                "textblob_score": sentiment_analysis['textblob_score']
            }
        }
        
        print("Text analysis result:", result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing text: {str(e)}")
        return jsonify({"error": f"Error analyzing text: {str(e)}"}), 500

@app.route('/analyze/hashtag', methods=['POST', 'OPTIONS'])
def analyze_hashtag():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("Received hashtag request:", request.get_json())
        data = request.get_json()
        
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
            
        hashtag = data.get('hashtag')
        
        if not hashtag:
            print("Hashtag is required")
            return jsonify({"error": "Hashtag is required"}), 400
            
        if not re.match(r'^[a-zA-Z0-9_]+$', hashtag):
            print("Invalid hashtag format")
            return jsonify({"error": "Invalid hashtag format. Only letters, numbers, and underscores are allowed."}), 400
            
        print(f"Analyzing hashtag: {hashtag}")

        # Improved hashtag text analysis
        # Split camelCase and snake_case into words
        words = []
        # Split by underscore first
        parts = hashtag.split('_')
        for part in parts:
            # Then split camelCase
            words.extend(re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', part))
        
        # Clean and join words
        hashtag_text = ' '.join(word.lower() for word in words if word)
        
        # If no words were extracted, use the original hashtag
        if not hashtag_text:
            hashtag_text = hashtag.lower()
        
        # Get sentiment analysis with context
        sentiment_analysis = analyze_sentiment(hashtag_text)
        base_sentiment = sentiment_analysis['score']

        # Use hashtag as seed for random number generation to ensure consistency
        random.seed(hashtag)

        # Generate timeline data with improved volume calculation
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        timeline = []
        
        # Base parameters - use hash of hashtag for consistency
        hashtag_hash = hash(hashtag)
        base_volume = 50 + abs(hashtag_hash % 450)  # Reduced base volume for more realistic numbers
        trend_direction = 1 if hashtag_hash % 2 == 0 else -1
        
        # Peak hours for social media activity (in 24-hour format)
        peak_hours = {
            9: 1.2,   # Morning
            12: 1.3,  # Lunch
            15: 1.2,  # Afternoon
            19: 1.5,  # Evening peak
            21: 1.4,  # Night
        }
        
        for i in range(24):
            hour = (now - timedelta(hours=23-i)).hour
            time = f"{hour:02d}:00"
            
            # Time-based volume adjustments
            time_factor = peak_hours.get(hour, 1.0)
            if 23 <= hour or hour <= 4:
                time_factor = 0.3  # Reduced activity during night hours
                
            # Use deterministic values based on hashtag and hour
            hour_seed = f"{hashtag}_{hour}"
            random.seed(hour_seed)
            
            # Calculate volume with more natural variation
            volume = int(base_volume * time_factor * (1 + random.uniform(-0.2, 0.2)))
            
            # Calculate sentiment with smoother transitions
            time_progress = i / 23
            trend_component = trend_direction * (time_progress - 0.5) * 0.3
            random.seed(f"{hour_seed}_sentiment")
            noise = random.uniform(-0.15, 0.15)
            
            sentiment = max(-1, min(1, base_sentiment + trend_component + noise))
            
            timeline.append({
                "time": time,
                "sentiment": round(sentiment, 3),
                "volume": volume
            })
            
        # Calculate overall metrics with volume-weighted sentiment
        total_volume = sum(t["volume"] for t in timeline)
        weighted_sentiment = sum(t["sentiment"] * t["volume"] for t in timeline) / total_volume if total_volume > 0 else base_sentiment
        
        # Determine overall sentiment with adjusted thresholds
        if weighted_sentiment > 0.15:
            sentiment = "positive"
        elif weighted_sentiment < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Calculate confidence with improved factors
        sentiment_std = (sum((t["sentiment"] - weighted_sentiment) ** 2 for t in timeline) / len(timeline)) ** 0.5
        volume_factor = min(1.0, total_volume / (500 * 24))  # Adjusted for lower volumes
        consistency_factor = 1 - sentiment_std
        base_confidence = sentiment_analysis['confidence']
        confidence = round((volume_factor + consistency_factor + base_confidence) / 3, 3)
            
        result = {
            "sentiment": sentiment,
            "score": round(weighted_sentiment, 3),
            "confidence": confidence,
            "timeline": timeline,
            "details": {
                "vader_scores": sentiment_analysis['vader_scores'],
                "textblob_score": sentiment_analysis['textblob_score']
            }
        }
        
        # Reset random seed
        random.seed()
        
        print("Hashtag analysis result:", result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing hashtag: {str(e)}")
        return jsonify({"error": f"Error analyzing hashtag: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
