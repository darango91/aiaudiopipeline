// WebSocket connection management

/**
 * Connects to the WebSocket server for a specific session
 * 
 * @param {string} sessionId - The ID of the audio session
 * @param {Object} handlers - Event handlers for WebSocket events
 * @param {Function} handlers.onTranscriptionUpdate - Called when a new transcription segment is received
 * @param {Function} handlers.onKeywordDetected - Called when a keyword is detected
 * @param {Function} handlers.onError - Called when an error occurs
 * @param {Function} handlers.onConnectionChange - Called when connection status changes
 * @returns {WebSocket} The WebSocket connection
 */
export const connectWebSocket = (sessionId, handlers) => {
  return new Promise((resolve, reject) => {
    try {
      // Use localhost for WebSocket URL
      const wsUrl = `ws://localhost:8000/ws/connect/${sessionId}`;
      console.log(`Connecting to WebSocket at: ${wsUrl}`);
      
      // Create WebSocket connection
      const ws = new WebSocket(wsUrl);
      
      // Connection opened
      ws.addEventListener('open', () => {
        console.log('WebSocket connection established');
        if (handlers.onConnectionChange) {
          handlers.onConnectionChange('connected');
        }
        resolve(ws);
      });
      
      // Listen for messages
      ws.addEventListener('message', (event) => {
        try {
          console.log('WebSocket message received:', event.data);
          const data = JSON.parse(event.data);
          
          // Handle different message types
          switch (data.type) {
            case 'transcription_update':
              if (handlers.onTranscriptionUpdate) {
                handlers.onTranscriptionUpdate(data.payload);
              }
              break;
              
            case 'partial_transcription':
              if (handlers.onTranscriptionUpdate) {
                console.log('Received partial transcription:', data.payload);
                handlers.onTranscriptionUpdate(data.payload);
              }
              break;
              
            case 'transcription_complete':
              if (handlers.onTranscriptionUpdate) {
                console.log('Received complete transcription:', data.payload);
                handlers.onTranscriptionUpdate({
                  transcript: data.payload.transcript,
                  segments: data.payload.segments || [],
                  detected_keywords: data.payload.detected_keywords || []
                });
              }
              break;
              
            case 'keyword_detected':
              if (handlers.onKeywordDetected) {
                handlers.onKeywordDetected(data.payload);
              }
              break;
              
            case 'error':
              console.error('WebSocket error message:', data.payload);
              if (handlers.onError) {
                handlers.onError(data.payload);
              }
              break;
              
            default:
              console.log('Unknown message type:', data);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          if (handlers.onError) {
            handlers.onError({ message: 'Error parsing WebSocket message' });
          }
        }
      });
      
      // Connection closed
      ws.addEventListener('close', (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        if (handlers.onConnectionChange) {
          handlers.onConnectionChange('disconnected');
        }
      });
      
      // Connection error
      ws.addEventListener('error', (error) => {
        console.error('WebSocket error:', error);
        if (handlers.onError) {
          handlers.onError({ message: 'WebSocket connection error' });
        }
        if (handlers.onConnectionChange) {
          handlers.onConnectionChange('error');
        }
        reject(error);
      });
      
      // Add a ping function to keep the connection alive
      ws.ping = () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      };
      
      // Set up a ping interval
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.ping();
        } else if (ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
          clearInterval(pingInterval);
        }
      }, 30000); // Ping every 30 seconds
      
      // Add a clean close method
      ws.cleanClose = () => {
        clearInterval(pingInterval);
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
      
    } catch (err) {
      console.error('Error setting up WebSocket:', err);
      if (handlers.onError) {
        handlers.onError({ message: 'Error setting up WebSocket connection' });
      }
      if (handlers.onConnectionChange) {
        handlers.onConnectionChange('error');
      }
      reject(err);
    }
  });
};

/**
 * Send a message through the WebSocket connection
 * 
 * @param {WebSocket} ws - The WebSocket connection
 * @param {string} type - The type of message
 * @param {Object} payload - The message payload
 * @returns {boolean} Whether the message was sent successfully
 */
export const sendWebSocketMessage = (ws, type, payload) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type, payload }));
    return true;
  }
  return false;
};
