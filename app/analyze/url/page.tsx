'use client';

import { useState } from 'react';

// Get the API URL from environment variable or fallback to production URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sentimentscope-j7sl.onrender.com';
import { Input } from '@/components/ui/input';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// URL validation helper
function isValidUrl(urlString: string): boolean {
  try {
    new URL(urlString);
    return true;
  } catch {
    return false;
  }
}


export default function URLAnalysis() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<null | {
    sentiment: 'positive' | 'negative' | 'neutral';
    score: number;
    confidence: number;
    wordFrequency: { word: string; count: number }[];
  }>(null);

  const handleAnalyze = async () => {
    // Validate URL
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    // Validate URL format
    if (!isValidUrl(url)) {
      setError('Please enter a valid URL');
      return;
    }

    // Debug logging
    console.log('Request details:', {
      API_URL,
      url: url.trim(),
      endpoint: `${API_URL}/analyze/url`
    });
    // Debug logging
    console.log('Current environment:', {
      NODE_ENV: process.env.NODE_ENV,
      API_URL: API_URL
    });
    if (!url.trim()) return;
    
    setLoading(true);
    try {
      // Ensure URL has protocol
      let processedUrl = url;
      if (!/^https?:\/\//i.test(url)) {
        processedUrl = 'https://' + url;
      }

      console.log('Making request to API:', {
        endpoint: `${API_URL}/analyze/url`,
        url: processedUrl
      });

      const response = await fetch(`${API_URL}/analyze/url`, {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ url: processedUrl }),
      });
      
      const responseData = await response.text();
      console.log('Raw response:', responseData);
      
      if (!response.ok) {
        let errorMessage = 'Failed to analyze URL';
        try {
          const errorData = JSON.parse(responseData);
          errorMessage = errorData.error || errorMessage;
        } catch {}
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      setResult({
        sentiment: data.sentiment,
        score: data.score,
        confidence: data.confidence,
        wordFrequency: data.wordFrequency
      });
    } catch (error: Error | unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze URL. Please try again.';
      console.error('Error analyzing URL:', error);
      setError(errorMessage);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 pt-32">
      <div className="mx-auto max-w-3xl">
        {/* Logo/Icon */}
        <div className="mx-auto mb-12 flex max-w-fit items-center justify-center">
          <div className="relative">
            <div className="absolute -inset-1 rounded-full bg-purple-500/30 blur-lg" />
            <div className="relative rounded-full bg-white/5 p-4 backdrop-blur-sm">
              <svg className="h-8 w-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="text-center">
          <h1 className="bg-gradient-to-b from-white to-white/70 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-5xl">
            URL Analysis
          </h1>
          <p className="mt-4 text-lg text-gray-400">
            Analyze the sentiment of any webpage content
          </p>
        </div>

        {/* Input Section */}
        <div className="relative mt-12">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl">
            <div className="relative">
              {error && (
                <div className="mb-4 rounded-lg border border-red-500/10 bg-red-500/5 p-4 text-sm text-red-400">
                  {error}
                </div>
              )}
              <Input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value.trim())}
                placeholder="   Enter URL to analyze"
                className="h-14 bg-white/5 px-6 text-base backdrop-blur-sm"
                icon={
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                }
              />
              <button
                onClick={handleAnalyze}
                disabled={!url.trim() || loading}
                className={`mt-4 w-full rounded-lg bg-purple-600 px-4 py-3 text-sm font-medium text-white transition-colors
                  hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20
                  ${!url.trim() || loading ? 'cursor-not-allowed opacity-50' : ''}`}
              >
                {loading ? 'Analyzing...' : 'Analyze URL'}
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-12"
          >
            <div className="grid md:grid-cols-2 gap-8">
              <div className="rounded-2xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl">
                <h3 className="text-xl font-semibold text-white mb-4">Analysis Results</h3>
                <div className="space-y-4">
                  <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                    <p className="text-sm text-gray-400">Overall Sentiment</p>
                    <p className="mt-1 text-2xl font-semibold text-white capitalize">{result.sentiment}</p>
                  </div>
                  <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                    <p className="text-sm text-gray-400">Confidence Score</p>
                    <p className="mt-1 text-2xl font-semibold text-white">{(result.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl">
                <h3 className="text-xl font-semibold text-white mb-4">Word Frequency</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={result.wordFrequency}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis type="number" stroke="#999" tick={{ fill: '#999' }} />
                      <YAxis dataKey="word" type="category" width={80} stroke="#999" tick={{ fill: '#999' }} />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                      />
                      <Bar dataKey="count" fill="#9333EA" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Background decorative elements */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-transparent" />
      </div>
    </div>
  );
}
