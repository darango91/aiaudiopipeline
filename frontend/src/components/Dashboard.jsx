import React, { useState, useEffect, useRef } from 'react';
import AudioRecorder from './AudioRecorder';
import TranscriptDisplay from './TranscriptDisplay';
import TalkingPointsPanel from './TalkingPointsPanel';
import { createSession, uploadAudioChunk, uploadAudioFile } from '../services/api';
import { connectWebSocket } from '../services/websocket';

function Dashboard({ sessionId, setSessionId }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [talkingPoints, setTalkingPoints] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const wsRef = useRef(null);
  const chunkCounter = useRef(0);
  
  // Initialize session and WebSocket connection
  useEffect(() => {
    const initializeSession = async () => {
      try {
        if (!sessionId) {
          // Create a new session
          const response = await createSession({
            title: `Session ${new Date().toLocaleString()}`,
            description: "Audio transcription session"
          });
          setSessionId(response.session_id);
          
          // Reset transcript and talking points for new session
          setTranscript([]);
          setTalkingPoints([]);
        }
      } catch (err) {
        setError(`Error creating session: ${err.message}`);
      }
    };
    
    initializeSession();
  }, [sessionId, setSessionId]);
  
  // Connect to WebSocket when sessionId is available
  useEffect(() => {
    if (sessionId) {
      const connectToWebSocket = async () => {
        try {
          setConnectionStatus('connecting');
          
          wsRef.current = await connectWebSocket(sessionId, {
            onTranscriptionUpdate: (data) => {
              console.log('Received transcription update:', data);
              
              // Check if this is a complete transcript notification
              const isCompleteTranscript = data.type === 'transcription_complete' || 
                                         (data.transcript && !data.segments);
              
              // Reset talking points for complete transcripts
              if (isCompleteTranscript) {
                setTalkingPoints([]);
              }
              
              // Handle different data formats based on notification type
              if (data.segments && Array.isArray(data.segments) && data.segments.length > 0) {
                // Handle segments array (from partial_transcription or transcription_complete)
                const newSegments = data.segments.map(segment => ({
                  id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                  text: segment.text || '',
                  startTime: segment.start_time || 0,
                  endTime: segment.end_time || 0,
                  speaker: segment.speaker || 'Unknown',
                  isProspect: segment.is_prospect || false,
                  isFinal: segment.is_final !== undefined ? segment.is_final : true
                }));
                
                if (isCompleteTranscript) {
                  // Replace transcript for complete notifications
                  setTranscript(newSegments);
                } else {
                  // Append segments for partial notifications
                  setTranscript(prev => [...prev, ...newSegments]);
                }
              } else if (data.transcript) {
                // Handle complete transcript (from transcription_complete)
                if (typeof data.transcript === 'string') {
                  // Simple string transcript
                  setTranscript(data.transcript);
                } else {
                  // Object with transcript property
                  setTranscript([{
                    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    text: data.transcript || '',
                    startTime: 0,
                    endTime: 0,
                    speaker: 'Complete Transcript',
                    isProspect: false,
                    isFinal: true
                  }]);
                }
              } else if (typeof data === 'string') {
                // Handle plain text transcription
                setTranscript(data);
              } else {
                // Handle single segment update (from transcription_update)
                setTranscript(prev => {
                  // If previous state is a string, convert to array format
                  const prevArray = typeof prev === 'string' ? [] : prev;
                  
                  return [...prevArray, {
                    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    text: data.text || '',
                    startTime: data.start_time || 0,
                    endTime: data.end_time || 0,
                    speaker: data.speaker || 'Unknown',
                    isProspect: data.is_prospect || false,
                    isFinal: data.is_final !== undefined ? data.is_final : true
                  }];
                });
              }
            },
            onKeywordDetected: (data) => {
              console.log('Received keyword detection:', data);
              
              // Extract keyword and confidence from the nested structure
              const keywordText = data.keyword?.keyword || data.keyword || 'Unknown keyword';
              const confidence = data.keyword?.confidence || data.confidence || 1.0;
              
              // Create a default talking point from the segment if no talking_points are provided
              const defaultTalkingPoint = data.segment ? [
                {
                  title: `Segment containing "${keywordText}"`,
                  content: data.segment.text || 'No content available'
                }
              ] : [];
              
              setTalkingPoints(prev => [
                ...prev,
                {
                  id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                  keyword: keywordText,
                  confidence: confidence,
                  talkingPoints: data.talking_points || defaultTalkingPoint
                }
              ]);
            },
            onError: (error) => {
              setError(`WebSocket error: ${error.message}`);
            },
            onConnectionChange: (status) => {
              setConnectionStatus(status);
            }
          });
        } catch (err) {
          setError(`Error connecting to WebSocket: ${err.message}`);
          setConnectionStatus('error');
        }
      };
      
      connectToWebSocket();
      
      return () => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [sessionId]);
  
  const handleStartRecording = () => {
    setIsRecording(true);
  };
  
  const handleStopRecording = () => {
    setIsRecording(false);
  };
  
  const handleAudioData = async (recordedBlob) => {
    if (!sessionId) return;
    
    try {
      setIsProcessing(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('sequence_number', chunkCounter.current++);
      formData.append('timestamp', Date.now() / 1000);
      formData.append('is_final', 'true');
      formData.append('audio_chunk', recordedBlob.blob);
      
      await uploadAudioChunk(formData);
      
      // Keep processing state for a moment to allow WebSocket to receive initial transcription
      setTimeout(() => {
        setIsProcessing(false);
      }, 1000);
    } catch (err) {
      setError(`Error uploading audio: ${err.message}`);
      setIsProcessing(false);
    }
  };
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !sessionId) return;
    
    try {
      setIsProcessing(true);
      setError(null);
      setUploadProgress(0);
      
      // Reset transcript and talking points for new upload
      setTranscript([]);
      setTalkingPoints([]);
      
      // Create FormData object for file upload
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('audio_file', file);
      
      // Create custom axios config to track upload progress
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      };
      
      await uploadAudioFile(formData, config);
      
      setUploadProgress(100);
    } catch (err) {
      setError(`Error uploading file: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Audio Assistant</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Session ID: {sessionId || 'Creating session...'}
          </p>
          <p className="text-sm text-gray-600">
            Status: <span className={`font-medium ${connectionStatus === 'connected' ? 'text-green-600' : connectionStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'}`}>
              {connectionStatus}
            </span>
          </p>
        </div>
        
        <AudioRecorder 
          isRecording={isRecording}
          isProcessing={isProcessing}
          onStartRecording={handleStartRecording}
          onStopRecording={handleStopRecording}
          onAudioData={handleAudioData}
          onFileUpload={handleFileUpload}
        />
        
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Uploading: {uploadProgress}%
            </label>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TranscriptDisplay transcript={transcript} />
        </div>
        <div>
          <TalkingPointsPanel talkingPoints={talkingPoints} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
