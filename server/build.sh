#!/bin/bash

# Create NLTK data directory
mkdir -p /opt/render/nltk_data

# Download NLTK data
python3 -c "
import nltk
import os

# Set NLTK data path
nltk.data.path.append('/opt/render/nltk_data')

# Download required resources
resources = ['punkt', 'stopwords', 'vader_lexicon']
for resource in resources:
    print(f'Downloading {resource}...')
    nltk.download(resource, download_dir='/opt/render/nltk_data', quiet=True)
    print(f'✓ Downloaded {resource}')

# Verify downloads
for resource in resources:
    try:
        if resource == 'punkt':
            nltk.data.find('tokenizers/punkt')
        elif resource == 'stopwords':
            nltk.data.find('corpora/stopwords')
        elif resource == 'vader_lexicon':
            nltk.data.find('sentiment/vader_lexicon')
        print(f'✓ Verified {resource}')
    except LookupError as e:
        print(f'Error verifying {resource}: {e}')
        exit(1)
"

# Make script executable
chmod +x "$0"
