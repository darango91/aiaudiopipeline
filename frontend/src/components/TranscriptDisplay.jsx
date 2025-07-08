import React, { useEffect, useRef, useState } from 'react';
import { getKeywords } from '../services/api';

function TranscriptDisplay({ transcript }) {
  const transcriptEndRef = useRef(null);
  const [filteredTranscript, setFilteredTranscript] = useState([]);
  const [filterSpeaker, setFilterSpeaker] = useState('all');
  const [uniqueSpeakers, setUniqueSpeakers] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [isLoadingKeywords, setIsLoadingKeywords] = useState(false);
  const [keywordError, setKeywordError] = useState(null);
  
  // Process transcript to handle different formats and extract unique speakers
  useEffect(() => {
    // Handle different transcript formats
    let processedTranscript = [];
    
    if (!transcript) {
      console.warn('Transcript is null or undefined');
      setFilteredTranscript([]);
      return;
    }
    
    // Handle simple string transcription
    if (typeof transcript === 'string') {
      processedTranscript = [{
        id: 'full-transcript',
        text: transcript,
        startTime: 0,
        endTime: 0,
        speaker: 'Transcription',
        isProspect: false,
        isFinal: true
      }];
    }
    // Handle array of segments
    else if (Array.isArray(transcript)) {
      processedTranscript = transcript;
    }
    // Handle object with text property
    else if (typeof transcript === 'object' && transcript !== null) {
      if (transcript.text) {
        processedTranscript = [{
          id: 'full-transcript',
          text: transcript.text,
          startTime: transcript.start_time || 0,
          endTime: transcript.end_time || 0,
          speaker: transcript.speaker || 'Transcription',
          isProspect: transcript.is_prospect || false,
          isFinal: transcript.is_final !== undefined ? transcript.is_final : true
        }];
      } else if (transcript.transcript) {
        processedTranscript = [{
          id: 'full-transcript',
          text: transcript.transcript,
          startTime: 0,
          endTime: 0,
          speaker: 'Complete Transcript',
          isProspect: false,
          isFinal: true
        }];
      }
    }
    
    // Extract unique speakers
    const speakers = new Set();
    processedTranscript.forEach(segment => {
      if (segment && segment.speaker) {
        speakers.add(segment.speaker);
      }
    });
    setUniqueSpeakers(Array.from(speakers));
    
    // Filter transcript if needed
    if (filterSpeaker === 'all') {
      setFilteredTranscript(processedTranscript);
    } else {
      setFilteredTranscript(processedTranscript.filter(segment => segment.speaker === filterSpeaker));
    }
  }, [transcript, filterSpeaker]);

  // Auto-scroll to the bottom when new transcripts arrive
  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredTranscript]);
  
  // Fetch keywords from the backend
  useEffect(() => {
    const fetchKeywords = async () => {
      try {
        setIsLoadingKeywords(true);
        setKeywordError(null);
        const data = await getKeywords();
        console.log('Fetched keywords:', data);
        if (data && Array.isArray(data)) {
          // Extract keyword text from the keyword objects
          const keywordTexts = data.map(keyword => keyword.text || keyword.keyword || '').filter(k => k);
          setKeywords(keywordTexts);
        } else {
          setKeywords([]);
        }
      } catch (error) {
        console.error('Error fetching keywords:', error);
        setKeywordError('Failed to load keywords');
        setKeywords([]);
      } finally {
        setIsLoadingKeywords(false);
      }
    };
    
    fetchKeywords();
  }, []);

  // Function to highlight keywords in text
  const highlightKeywords = (text) => {
    // Check if text is null or undefined
    if (!text) return '';
    
    // Use fetched keywords from the backend, or fallback to empty array if none available
    const keywordsToUse = keywords.length > 0 ? keywords : ['pricing', 'competitor', 'integration'];
    
    // Create parts array for rendering with highlighted keywords
    const parts = [];
    let lastIndex = 0;
    
    // Function to check if a word matches any keyword
    const findKeyword = (word) => {
      return keywordsToUse.find(keyword => 
        word.toLowerCase() === keyword.toLowerCase() ||
        word.toLowerCase().includes(keyword.toLowerCase())
      );
    };
    
    // Split text into words and process each word
    const words = text.split(/\b/);
    words.forEach((word, i) => {
      if (findKeyword(word)) {
        parts.push(
          <span key={`text-${i}`}>{text.substring(lastIndex, text.indexOf(word, lastIndex))}</span>,
          <span key={`highlight-${i}`} className="keyword-highlight">{word}</span>
        );
        lastIndex = text.indexOf(word, lastIndex) + word.length;
      }
    });
    
    // Add the remaining text
    if (lastIndex < text.length) {
      parts.push(<span key="text-end">{text.substring(lastIndex)}</span>);
    }
    
    // If no keywords were found, return the original text
    return parts.length > 0 ? parts : text;
  };

  const formatTime = (seconds) => {
    if (seconds === undefined || seconds === null) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Real-time Transcript</h2>
        
        {uniqueSpeakers.length > 1 && (
          <div className="flex items-center">
            <label htmlFor="speaker-filter" className="mr-2 text-sm text-gray-600">Filter by speaker:</label>
            <select
              id="speaker-filter"
              value={filterSpeaker}
              onChange={(e) => setFilterSpeaker(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value="all">All Speakers</option>
              {uniqueSpeakers.map(speaker => (
                <option key={speaker} value={speaker}>{speaker}</option>
              ))}
            </select>
          </div>
        )}
      </div>
      
      <div className="transcript-container max-h-96 overflow-y-auto">
        {!transcript ? (
          <p className="text-gray-500 italic">No transcript available yet. Start recording or upload an audio file.</p>
        ) : filteredTranscript.length === 0 ? (
          <p className="text-gray-500 italic">No transcript segments match the current filter.</p>
        ) : typeof transcript === 'string' ? (
          <p className="text-gray-800">{highlightKeywords(transcript)}</p>
        ) : (
          filteredTranscript.map((segment) => {
            if (!segment || typeof segment !== 'object') {
              console.warn('Invalid segment in transcript:', segment);
              return null;
            }
            
            return (
              <div 
                key={segment.id || `segment-${Math.random()}`}
                className={`mb-4 p-3 rounded-lg ${
                  segment.isProspect 
                    ? 'bg-blue-50 border-l-4 border-blue-500' 
                    : 'bg-gray-50 border-l-4 border-gray-300'
                }`}
              >
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>
                    {segment.speaker ? `Speaker: ${segment.speaker}` : 'Unknown Speaker'} 
                    {segment.isProspect ? ' (Prospect)' : ''}
                  </span>
                  <span>{formatTime(segment.startTime)} - {formatTime(segment.endTime)}</span>
                </div>
                <p className="text-gray-800">
                  {highlightKeywords(segment.text || '')}
                </p>
                {segment.isFinal === false && (
                  <span className="text-xs italic text-gray-500">(processing...)</span>
                )}
              </div>
            );
          })
        )}
        <div ref={transcriptEndRef} />
      </div>
    </div>
  );
}

export default TranscriptDisplay;
