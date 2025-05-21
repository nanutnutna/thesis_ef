import React, { useState, useEffect, useCallback } from 'react';
import { fetchAutocompleteCFP, searchDataCFP } from '../api/api';
import DataTable from './DataTable';
import { Link } from 'react-router-dom';

const AutocompleteSearchCFP = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [isFocused, setIsFocused] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // โหลดข้อมูลเริ่มต้น
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const response = await searchDataCFP('');
        setResults(response.data || []);
      } catch (err) {
        console.error('Initial Load Error:', err);
        setError('Failed to load initial data');
      } finally {
        setIsInitialLoad(false);
      }
    };

    fetchInitialData();
  }, []);

  // จัดการการเปลี่ยนแปลงใน Input
  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.trim() !== '') {
      try {
        const response = await fetchAutocompleteCFP(value);
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        console.error('Autocomplete Error:', err);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      await handleSearch('');
    }
  };

  // เลือกคำแนะนำ
  const handleSelectSuggestion = async (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    await handleSearch(suggestion);
  };

  // ค้นหา
  const handleSearch = useCallback(async (searchQuery) => {
    try {
      const response = await searchDataCFP(searchQuery || query);
      setResults(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Search Error:', err);
      setError('Failed to fetch search results');
      setResults([]);
    }
  }, [query]);

  // โหลดข้อมูลทั้งหมดหาก Query ว่าง
  useEffect(() => {
    if (query.trim() === '') {
      handleSearch('');
    }
  }, [query, handleSearch]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-200 to-teal-600 p-4">
      {/* ปุ่มกลับหน้า Home ที่มุมซ้ายบน */}
      <div className="absolute top-4 left-4">
        <Link 
          to="/" 
          className="flex items-center bg-white text-teal-700 hover:bg-teal-50 font-medium py-2 px-4 rounded-lg shadow-md transition-all duration-300 border-2 border-teal-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Home
        </Link>
      </div>

      <div className="max-w-7xl mx-auto bg-gray-100 rounded-xl shadow-lg p-6 mt-16">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-teal-800 text-center mb-6 flex items-center justify-center">
            <span className="mr-2 text-4xl">🏷️</span>
            Emission Factor (CFP: Carbon Footprint for Product)
          </h1>
          
          <div className="relative w-full max-w-3xl mx-auto">
            <div className="flex items-center bg-white border border-teal-500 rounded-lg overflow-hidden shadow-md">
              <span className="pl-4 text-xl text-gray-500">🔍</span>
              <input
                type="text"
                placeholder="Type for search..."
                value={query}
                onChange={handleChange}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setTimeout(() => setIsFocused(false), 200)}
                className="w-full py-4 px-3 text-lg outline-none"
              />
            </div>
            
            {/* แสดงคำแนะนำ */}
            {isFocused && suggestions.length > 0 && (
              <div className="absolute z-50 left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                <ul className="divide-y divide-gray-200">
                  {suggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="px-4 py-3 hover:bg-teal-50 cursor-pointer"
                      onMouseDown={() => handleSelectSuggestion(suggestion)}
                    >
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* แสดง Error */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* แสดงสถานะการโหลดครั้งแรก */}
        {isInitialLoad && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-600"></div>
            <span className="ml-3 text-lg text-teal-700">Loading initial data...</span>
          </div>
        )}

        {/* แสดงผลลัพธ์ในตาราง */}
        {!isInitialLoad && results.length > 0 ? (
          <div className="w-full overflow-hidden">
            <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg">
              <DataTable data={results} />
            </div>
          </div>
        ) : !isInitialLoad && (
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-lg text-gray-600">No data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AutocompleteSearchCFP;