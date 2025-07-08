import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import KeywordConfig from './components/KeywordConfig';
import Header from './components/Header';

function App() {
  const [sessionId, setSessionId] = useState('');

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard sessionId={sessionId} setSessionId={setSessionId} />} />
          <Route path="/keywords" element={<KeywordConfig />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
