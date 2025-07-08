import React, { useState, useRef } from 'react';
import { AudioRecorder as VoiceRecorder } from 'react-audio-voice-recorder';
import { FaMicrophone, FaStop, FaUpload, FaSpinner, FaPaperPlane } from 'react-icons/fa';

function AudioRecorder({ onStartRecording, onStopRecording, onAudioData, onFileUpload, isProcessing }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const fileInputRef = useRef(null);
  
  const handleRecordingStart = () => {
    setIsRecording(true);
    onStartRecording && onStartRecording();
  };
  
  const handleRecordingStop = (audioBlob) => {
    setIsRecording(false);
    onStopRecording && onStopRecording();
    
    // Create a recordedBlob object that matches the expected format
    const recordedBlob = {
      blob: audioBlob,
      startTime: Date.now(),
      stopTime: Date.now(),
      options: { type: 'audio/webm' },
      blobURL: URL.createObjectURL(audioBlob)
    };
    
    // Store the recorded audio for later submission
    setRecordedAudio(recordedBlob);
  };
  
  const handleSubmitRecording = () => {
    if (recordedAudio) {
      onAudioData && onAudioData(recordedAudio);
      setRecordedAudio(null);
    }
  };
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('File selected:', file);
      onFileUpload && onFileUpload(e);
      
      // Reset the file input so the same file can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  return (
    <div className="space-y-4">
      {/* Recording interface */}
      <div className="flex flex-col items-center justify-center bg-gray-100 p-4 rounded-md">
        {!isProcessing ? (
          <>
            {/* Step 1: Record audio */}
            {!recordedAudio && (
              <div className="text-center">
                <div className="mb-2 text-sm font-medium text-gray-700">Step 1: Record your audio</div>
                <VoiceRecorder 
                  onRecordingComplete={handleRecordingStop}
                  onStartRecording={handleRecordingStart}
                  audioTrackConstraints={{
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                  }}
                  downloadOnSavePress={false}
                  downloadFileExtension="webm"
                  showVisualizer={true}
                />
              </div>
            )}
            
            {/* Step 2: Preview and submit */}
            {recordedAudio && (
              <div className="w-full text-center">
                <div className="mb-2 text-sm font-medium text-gray-700">Step 2: Review and submit your recording</div>
                <audio 
                  src={recordedAudio.blobURL} 
                  controls 
                  className="w-full max-w-md mb-4"
                />
                <div className="flex justify-center space-x-3">
                  <button 
                    onClick={() => setRecordedAudio(null)} 
                    className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition"
                  >
                    Discard & Re-record
                  </button>
                  <button 
                    onClick={handleSubmitRecording} 
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center"
                  >
                    <FaPaperPlane className="mr-2" />
                    Submit Recording
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-4">
            <FaSpinner className="animate-spin text-blue-500 text-2xl mb-2" />
            <p className="text-sm text-gray-600">Processing audio...</p>
          </div>
        )}
      </div>
      
      <div className="flex space-x-4 items-center">
        {/* Status indicators */}
        {isRecording && (
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-600 animate-pulse mr-2"></div>
            <span className="text-sm text-red-600">Recording...</span>
          </div>
        )}
        
        {isProcessing && !isRecording && (
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-600 animate-pulse mr-2"></div>
            <span className="text-sm text-blue-600">Processing...</span>
          </div>
        )}
        
        <div className="flex-1"></div>
        
        {/* File upload option */}
        <div className="flex items-center">
          <div className="mr-3 text-sm text-gray-700">Or</div>
          <label className={`cursor-pointer flex items-center px-4 py-2 ${isProcessing || recordedAudio ? 'bg-gray-400 cursor-not-allowed' : 'bg-gray-600 hover:bg-gray-700'} text-white rounded-md transition`}>
            {isProcessing ? (
              <>
                <FaSpinner className="animate-spin mr-2" />
                Processing...
              </>
            ) : (
              <>
                <FaUpload className="mr-2" />
                Upload Audio File
              </>
            )}
            <input 
              ref={fileInputRef}
              type="file" 
              className="hidden" 
              accept="audio/*" 
              onChange={handleFileChange}
              disabled={isProcessing || recordedAudio}
            />
          </label>
        </div>
      </div>
    </div>
  );
}

export default AudioRecorder;
