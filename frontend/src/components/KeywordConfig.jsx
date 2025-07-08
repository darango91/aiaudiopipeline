import React, { useState, useEffect } from 'react';
import { getKeywords, createKeyword, updateKeyword, deleteKeyword, 
         createTalkingPoint, updateTalkingPoint, deleteTalkingPoint } from '../services/api';

function KeywordConfig() {
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Form states
  const [newKeyword, setNewKeyword] = useState({ text: '', description: '', threshold: 0.7 });
  const [newTalkingPoint, setNewTalkingPoint] = useState({ title: '', content: '', priority: 1 });
  
  // Fetch keywords on component mount
  useEffect(() => {
    fetchKeywords();
  }, []);
  
  const fetchKeywords = async () => {
    try {
      setIsLoading(true);
      const data = await getKeywords();
      setKeywords(data);
      setIsLoading(false);
    } catch (err) {
      setError(`Error fetching keywords: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  const handleKeywordSelect = async (keywordId) => {
    try {
      setIsLoading(true);
      // In a real app, you'd fetch the full keyword with talking points
      const keyword = keywords.find(k => k.id === keywordId);
      setSelectedKeyword(keyword);
      setIsLoading(false);
    } catch (err) {
      setError(`Error fetching keyword details: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  const handleCreateKeyword = async (e) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      await createKeyword(newKeyword);
      setNewKeyword({ text: '', description: '', threshold: 0.7 });
      await fetchKeywords();
      setIsLoading(false);
    } catch (err) {
      setError(`Error creating keyword: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  const handleUpdateKeyword = async (e) => {
    e.preventDefault();
    if (!selectedKeyword) return;
    
    try {
      setIsLoading(true);
      await updateKeyword(selectedKeyword.id, selectedKeyword);
      await fetchKeywords();
      setIsLoading(false);
    } catch (err) {
      setError(`Error updating keyword: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  const handleDeleteKeyword = async (keywordId) => {
    try {
      setIsLoading(true);
      await deleteKeyword(keywordId);
      setSelectedKeyword(null);
      await fetchKeywords();
      setIsLoading(false);
    } catch (err) {
      setError(`Error deleting keyword: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  const handleCreateTalkingPoint = async (e) => {
    e.preventDefault();
    if (!selectedKeyword) return;
    
    try {
      setIsLoading(true);
      await createTalkingPoint(selectedKeyword.id, newTalkingPoint);
      // Refresh the selected keyword to show the new talking point
      await handleKeywordSelect(selectedKeyword.id);
      setNewTalkingPoint({ title: '', content: '', priority: 1 });
      setIsLoading(false);
    } catch (err) {
      setError(`Error creating talking point: ${err.message}`);
      setIsLoading(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Keyword Configuration</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Keywords List */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-700">Keywords</h3>
            
            <div className="border rounded-md overflow-hidden">
              {isLoading ? (
                <div className="p-4 text-center text-gray-500">Loading...</div>
              ) : keywords.length === 0 ? (
                <div className="p-4 text-center text-gray-500">No keywords found</div>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {keywords.map((keyword) => (
                    <li 
                      key={keyword.id}
                      className={`p-3 cursor-pointer hover:bg-gray-50 ${
                        selectedKeyword?.id === keyword.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleKeywordSelect(keyword.id)}
                    >
                      <div className="font-medium">{keyword.text}</div>
                      <div className="text-sm text-gray-500 truncate">{keyword.description}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            {/* New Keyword Form */}
            <div className="border rounded-md p-4">
              <h4 className="font-medium text-gray-700 mb-3">Add New Keyword</h4>
              <form onSubmit={handleCreateKeyword}>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Keyword Text</label>
                    <input
                      type="text"
                      value={newKeyword.text}
                      onChange={(e) => setNewKeyword({...newKeyword, text: e.target.value})}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <input
                      type="text"
                      value={newKeyword.description}
                      onChange={(e) => setNewKeyword({...newKeyword, description: e.target.value})}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Threshold ({newKeyword.threshold})
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={newKeyword.threshold}
                      onChange={(e) => setNewKeyword({...newKeyword, threshold: parseFloat(e.target.value)})}
                      className="mt-1 block w-full"
                    />
                  </div>
                  
                  <button
                    type="submit"
                    className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Adding...' : 'Add Keyword'}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          {/* Selected Keyword Details */}
          <div className="md:col-span-2">
            {selectedKeyword ? (
              <div className="space-y-6">
                <div className="border rounded-md p-4">
                  <h3 className="font-medium text-gray-700 mb-3">Edit Keyword</h3>
                  <form onSubmit={handleUpdateKeyword}>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Keyword Text</label>
                        <input
                          type="text"
                          value={selectedKeyword.text}
                          onChange={(e) => setSelectedKeyword({...selectedKeyword, text: e.target.value})}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Description</label>
                        <input
                          type="text"
                          value={selectedKeyword.description || ''}
                          onChange={(e) => setSelectedKeyword({...selectedKeyword, description: e.target.value})}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Threshold ({selectedKeyword.threshold})
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={selectedKeyword.threshold}
                          onChange={(e) => setSelectedKeyword({...selectedKeyword, threshold: parseFloat(e.target.value)})}
                          className="mt-1 block w-full"
                        />
                      </div>
                      
                      <div className="flex space-x-3">
                        <button
                          type="submit"
                          className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          disabled={isLoading}
                        >
                          {isLoading ? 'Saving...' : 'Save Changes'}
                        </button>
                        
                        <button
                          type="button"
                          onClick={() => handleDeleteKeyword(selectedKeyword.id)}
                          className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          disabled={isLoading}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
                
                {/* Talking Points */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-3">Talking Points</h3>
                  
                  <div className="space-y-3">
                    {selectedKeyword.talking_points?.length > 0 ? (
                      selectedKeyword.talking_points.map((point, index) => (
                        <div key={point.id} className="border rounded-md p-4 bg-gray-50">
                          <h4 className="font-medium">{point.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{point.content}</p>
                          <div className="mt-2 text-xs text-gray-500">Priority: {point.priority}</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 italic">No talking points for this keyword</div>
                    )}
                  </div>
                  
                  {/* Add Talking Point Form */}
                  <div className="border rounded-md p-4 mt-4">
                    <h4 className="font-medium text-gray-700 mb-3">Add Talking Point</h4>
                    <form onSubmit={handleCreateTalkingPoint}>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Title</label>
                          <input
                            type="text"
                            value={newTalkingPoint.title}
                            onChange={(e) => setNewTalkingPoint({...newTalkingPoint, title: e.target.value})}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Content</label>
                          <textarea
                            value={newTalkingPoint.content}
                            onChange={(e) => setNewTalkingPoint({...newTalkingPoint, content: e.target.value})}
                            rows={3}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            required
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Priority ({newTalkingPoint.priority})
                          </label>
                          <input
                            type="range"
                            min="1"
                            max="10"
                            step="1"
                            value={newTalkingPoint.priority}
                            onChange={(e) => setNewTalkingPoint({...newTalkingPoint, priority: parseInt(e.target.value)})}
                            className="mt-1 block w-full"
                          />
                        </div>
                        
                        <button
                          type="submit"
                          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          disabled={isLoading}
                        >
                          {isLoading ? 'Adding...' : 'Add Talking Point'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            ) : (
              <div className="border rounded-md p-8 text-center text-gray-500">
                Select a keyword from the list to view or edit its details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default KeywordConfig;
