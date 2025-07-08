import React, { useState, useEffect } from 'react';
import { getKeywords } from '../services/api';

function TalkingPointsPanel({ talkingPoints = [] }) {
  const [keywords, setKeywords] = useState([]);
  const [isLoadingKeywords, setIsLoadingKeywords] = useState(false);
  const [keywordError, setKeywordError] = useState(null);
  
  // Fetch keywords from the backend
  useEffect(() => {
    const fetchKeywords = async () => {
      try {
        setIsLoadingKeywords(true);
        setKeywordError(null);
        const data = await getKeywords();
        console.log('TalkingPointsPanel: Fetched keywords:', data);
        if (data && Array.isArray(data)) {
          setKeywords(data);
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
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Talking Points</h2>
      
      <div className="space-y-4 max-h-[500px] overflow-y-auto">
        {talkingPoints.length === 0 ? (
          <p className="text-gray-500 italic">No talking points detected yet.</p>
        ) : (
          talkingPoints.map((item) => {
            // Find matching keyword from database if available
            const matchingKeyword = keywords.find(k => 
              k.text?.toLowerCase() === item.keyword?.toLowerCase() || 
              k.keyword?.toLowerCase() === item.keyword?.toLowerCase()
            );
            
            return (
              <div key={item.id || `talking-point-${Math.random()}`} className="bg-blue-50 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium text-blue-800">
                    Keyword: <span className="keyword-highlight">{item.keyword}</span>
                  </h3>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {Math.round((item.confidence || 0.5) * 100)}% confidence
                  </span>
                </div>
                
                {matchingKeyword && matchingKeyword.description && (
                  <div className="text-sm text-gray-600 mb-3 bg-blue-100 p-2 rounded">
                    <strong>Description:</strong> {matchingKeyword.description}
                  </div>
                )}
              
                <div className="space-y-3 mt-3">
                  {item.talkingPoints && Array.isArray(item.talkingPoints) ? (
                    item.talkingPoints.map((point, index) => (
                      <div key={index} className="talking-point">
                        <h4 className="font-medium text-gray-800">{point?.title || 'No title'}</h4>
                        <p className="text-sm text-gray-600 mt-1">{point?.content || 'No content'}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 italic">No talking points available</p>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default TalkingPointsPanel;
