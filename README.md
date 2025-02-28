# SentimentScope - Premium Sentiment Analysis Tool

SentimentScope is a modern web application that performs advanced sentiment analysis using Natural Language Processing (NLP). The app allows users to analyze text, URLs, and hashtags to determine sentiment and visualize the results in an interactive and visually appealing manner.

## Features

- **Text Analysis**: Analyze sentiment in any text with our advanced NLP engine
- **URL Analysis**: Extract and analyze sentiment from webpage content
- **Hashtag Analysis**: Track sentiment across social media posts
- **Interactive Visualizations**: View sentiment analysis results through beautiful charts and graphs
- **Multi-Language Support**: Analyze content in multiple languages
- **Modern UI**: Clean, responsive design with smooth animations

## Tech Stack

- **Frontend**: React + Next.js
- **UI Library**: Tailwind CSS + ShadCN
- **Backend**: FastAPI (Python)
- **NLP**: TextBlob, NLTK
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sentiment-scope.git
   cd sentiment-scope
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the frontend development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. Start the backend API server:
   ```bash
   cd api
   uvicorn main:app --reload
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## API Documentation

The backend API provides the following endpoints:

- `POST /analyze/text` - Analyze text sentiment
- `POST /analyze/url` - Analyze webpage content sentiment
- `POST /analyze/hashtag` - Analyze social media hashtag sentiment

For detailed API documentation, visit [http://localhost:8000/docs](http://localhost:8000/docs) when the backend server is running.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
# SentimentScope
