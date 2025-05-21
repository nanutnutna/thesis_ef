import React, { useState, useEffect, useCallback } from 'react';
import { searchDataCFP } from '../api/api';
import DataTable from '../components/DataTableCFP';
import { Link } from 'react-router-dom';
import { debounce } from 'lodash'; // นำเข้า debounce จาก lodash

const RealTimeSearchCFP = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // สร้างฟังก์ชัน debounced search เพื่อไม่ให้ค้นหาบ่อยเกินไป
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      setIsLoading(true);
      try {
        const response = await searchDataCFP(searchQuery);
        setResults(response.data || []);
        setError(null);
      } catch (err) {
        console.error('Search Error:', err);
        setError('Failed to fetch search results');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300), // รอ 300ms หลังจากหยุดพิมพ์
    []
  );

  // โหลดข้อมูลเริ่มต้น
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        const response = await searchDataCFP('');
        setResults(response.data || []);
      } catch (err) {
        console.error('Initial Load Error:', err);
        setError('Failed to load initial data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // จัดการการเปลี่ยนแปลงใน Input และค้นหาแบบ Real-time
  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
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
            <span className="mr-2 text-4xl">🏷️</span>
            Emission Factor (CFP: Carbon Footprint for Product)
          </h1>
          
          <div className="relative w-full max-w-3xl mx-auto">
            <div className="flex items-center bg-white border border-teal-500 rounded-lg overflow-hidden shadow-md">
              <span className="pl-4 text-xl text-gray-500">🔍</span>
              <input
                type="text"
                placeholder="Start typing to search..."
                value={query}
                onChange={handleChange}
                className="w-full py-4 px-3 text-lg outline-none"
              />
              {isLoading && (
                <div className="pr-4">
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-r-2 border-teal-600"></div>
                </div>
              )}
            </div>
            <p className="text-sm text-gray-600 mt-2 ml-1">Results update automatically as you type</p>
          </div>
        </div>

        {/* แสดง Error */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* แสดงผลลัพธ์ในตาราง */}
        {results.length > 0 ? (
          <div className="w-full overflow-hidden">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xl font-semibold text-teal-800">
                {query.trim() ? `Search results for "${query}"` : 'All available data'}
                <span className="ml-2 text-gray-600 text-base">({results.length} items)</span>
              </h3>
            </div>
            <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg">
              <DataTable data={results} />
            </div>
          </div>
        ) : !isLoading && (
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-lg text-gray-600">No data available{query.trim() ? ` for "${query}"` : ''}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RealTimeSearchCFP;