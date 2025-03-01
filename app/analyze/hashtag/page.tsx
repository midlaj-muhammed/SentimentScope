'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';

export default function HashtagAnalysis() {
  const [hashtag, setHashtag] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<null | {
    sentiment: 'positive' | 'negative' | 'neutral';
    score: number;
    confidence: number;
    timeline: {
      time: string;
      sentiment: number;
      volume: number;
    }[];
  }>(null);

  const handleHashtagChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHashtag(e.target.value.replace(/^#/, ''));
  };

  const handleAnalyze = async () => {
    if (!hashtag.trim()) return;
    
    setLoading(true);
    try {
      const cleanHashtag = hashtag.trim().replace(/^#/, '');
      const response = await fetch('http://localhost:8000/analyze/hashtag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ hashtag: cleanHashtag }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze hashtag');
      }
      
      const data = await response.json();
      setResult({
        sentiment: data.sentiment,
        score: data.score,
        confidence: data.confidence,
        timeline: data.timeline
      });
    } catch (error) {
      console.error('Error analyzing hashtag:', error);
      alert('Failed to analyze hashtag. Please try again.');
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
              </svg>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="text-center">
          <h1 className="bg-gradient-to-b from-white to-white/70 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-5xl">
            Hashtag Analysis
          </h1>
          <p className="mt-4 text-lg text-gray-400">
            Track sentiment trends across social media
          </p>
        </div>

        {/* Input Section */}
        <div className="relative mt-12">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl">
            <div className="relative">
              <Input
                type="text"
                value={hashtag}
                onChange={handleHashtagChange}
                placeholder="  Enter hashtag (without #)"
                className="h-14 bg-white/5 px-6 text-base backdrop-blur-sm"
                autoComplete="off"
                icon={
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                  </svg>
                }
              />
              <button
                onClick={handleAnalyze}
                disabled={!hashtag.trim() || loading}
                className={cn(
                  "mt-4 w-full rounded-lg bg-purple-600 px-4 py-3 text-sm font-medium text-white transition-colors",
                  "hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20",
                  "disabled:cursor-not-allowed disabled:opacity-50"
                )}
              >
                {loading ? 'Analyzing...' : 'Analyze Hashtag'}
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
            <div className="rounded-2xl border border-white/10 bg-black/20 p-8 backdrop-blur-xl">
              <h3 className="text-2xl font-bold mb-4">Analysis Results</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-gray-400">Overall Sentiment</p>
                  <p className="text-2xl font-bold capitalize">{result.sentiment}</p>
                </div>
                <div>
                  <p className="text-gray-400">Confidence Score</p>
                  <p className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
                </div>
              </div>
              <div className="h-64 mt-8">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={result.timeline}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="time" stroke="#999" />
                    <YAxis yAxisId="left" stroke="#4F46E5" />
                    <YAxis yAxisId="right" orientation="right" stroke="#10B981" />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="sentiment"
                      name="Sentiment"
                      stroke="#4F46E5"
                      activeDot={{ r: 8 }}
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="volume"
                      name="Volume"
                      stroke="#10B981"
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
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
