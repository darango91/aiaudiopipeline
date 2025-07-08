import axios from 'axios';

// Determine if we're running in a browser or server environment
const isBrowser = typeof window !== 'undefined';

// Get API base URL from environment or use default
// If running in browser, use localhost, otherwise use Docker service name
let API_URL = import.meta.env.VITE_API_URL || '/api';

// For debugging
console.log('API_URL from env:', import.meta.env.VITE_API_URL);
console.log('Final API_URL:', API_URL);

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(config => {
  console.log(`Making ${config.method.toUpperCase()} request to: ${config.baseURL}${config.url}`);
  return config;
});

// Audio session endpoints
export const createSession = async (sessionData) => {
  try {
    console.log('Creating session with data:', sessionData);
    const response = await api.post('/audio/sessions', sessionData);
    console.log('Session created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error creating session:', error);
    throw error;
  }
};

export const getSession = async (sessionId) => {
  const response = await api.get(`/audio/sessions/${sessionId}`);
  return response.data;
};

export const updateSession = async (sessionId, sessionData) => {
  const response = await api.put(`/audio/sessions/${sessionId}`, sessionData);
  return response.data;
};

export const uploadAudioFile = async (formData, config = {}) => {
  // Merge the provided config with default headers
  const mergedConfig = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...config
  };
  
  // Ensure headers are merged properly if provided in config
  if (config.headers) {
    mergedConfig.headers = {
      ...mergedConfig.headers,
      ...config.headers
    };
  }
  
  const response = await api.post('/audio/upload', formData, mergedConfig);
  return response.data;
};

export const uploadAudioChunk = async (formData) => {
  const response = await api.post('/audio/chunks', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getTranscript = async (sessionId) => {
  const response = await api.get(`/audio/sessions/${sessionId}/transcript`);
  return response.data;
};

// Keyword endpoints
export const getKeywords = async () => {
  const response = await api.get('/keywords');
  return response.data;
};

export const getKeyword = async (keywordId) => {
  const response = await api.get(`/keywords/${keywordId}`);
  return response.data;
};

export const createKeyword = async (keywordData) => {
  const response = await api.post('/keywords', keywordData);
  return response.data;
};

export const updateKeyword = async (keywordId, keywordData) => {
  const response = await api.put(`/keywords/${keywordId}`, keywordData);
  return response.data;
};

export const deleteKeyword = async (keywordId) => {
  const response = await api.delete(`/keywords/${keywordId}`);
  return response.data;
};

// Talking point endpoints
export const createTalkingPoint = async (keywordId, talkingPointData) => {
  const response = await api.post(`/keywords/${keywordId}/talking-points`, talkingPointData);
  return response.data;
};

export const updateTalkingPoint = async (keywordId, talkingPointId, talkingPointData) => {
  const response = await api.put(`/keywords/${keywordId}/talking-points/${talkingPointId}`, talkingPointData);
  return response.data;
};

export const deleteTalkingPoint = async (keywordId, talkingPointId) => {
  const response = await api.delete(`/keywords/${keywordId}/talking-points/${talkingPointId}`);
  return response.data;
};
