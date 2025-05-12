import React, { useState } from 'react';
import { searchDataCFPlabel } from "../api/api";
import DataTableCFPLabel from '../components/DataTableCFPLabel';
import { Link } from 'react-router-dom';

const SearchPageCFPLabel = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // เรียกใช้ searchDataCFPlabel ผ่าน api object
      const response = await searchDataCFPlabel(query);
      console.log('API Response:', response);
      
      const data = response.data || response;
      
      if (Array.isArray(data)) {
        setResults(data);
      } else if (data && typeof data === 'object' && data.results && Array.isArray(data.results)) {
        setResults(data.results);
      } else {
        console.error('Unexpected response format:', data);
        setResults([]);
        setError('รูปแบบข้อมูลที่ได้รับไม่ถูกต้อง');
      }
    } catch (err) {
      console.error('Error searching hybrid:', err);
      setError('ไม่สามารถค้นหาข้อมูลได้ กรุณาลองใหม่อีกครั้ง');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

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
            <span className="mr-2 text-4xl">🌿</span>
            Emission Factor (CFP Label: Carbon Footprint for Thailand Product)
          </h1>
          
          <div className="flex justify-center mb-8">
            <div className="relative w-full max-w-3xl">
              <div className="flex items-center">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="พิมพ์คำค้นหา..."
                  className="w-full py-4 px-6 text-lg border border-teal-500 rounded-l-lg shadow-md outline-none"
                />
                <button 
                  onClick={handleSearch} 
                  className="bg-teal-600 hover:bg-teal-700 text-white py-4 px-8 text-lg font-medium rounded-r-lg shadow-md transition-colors duration-300"
                >
                  ค้นหา
                </button>
              </div>
            </div>
          </div>

          {/* แสดง Error */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6 max-w-3xl mx-auto">
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {/* แสดงสถานะการโหลด */}
          {loading && (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-600"></div>
              <span className="ml-3 text-lg text-teal-700">กำลังค้นหา...</span>
            </div>
          )}

          {/* แสดงผลลัพธ์ในตาราง */}
          {!loading && results.length > 0 && (
            <div className="w-full">
              <h3 className="text-xl font-semibold text-teal-800 mb-4">ผลการค้นหา</h3>
              <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg">
                <DataTableCFPLabel data={results} />
              </div>
            </div>
          )}

          {/* แสดงข้อความเมื่อไม่พบผลลัพธ์ */}
          {!loading && query && results.length === 0 && (
            <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200 max-w-3xl mx-auto">
              <p className="text-lg text-gray-600">ไม่พบข้อมูลสำหรับ "{query}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchPageCFPLabel;