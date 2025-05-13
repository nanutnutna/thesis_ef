import React, { useState, useEffect, useCallback } from 'react';
import { searchDataCFPlabel } from "../api/api";
import DataTableCFPLabel from '../components/DataTableCFPLabel';
import { Link } from 'react-router-dom';
import { debounce } from 'lodash'; // นำเข้า debounce จาก lodash

const SearchPageCFPLabel = () => {
  const [query, setQuery] = useState('');
  const [allResults, setAllResults] = useState([]); // เก็บผลลัพธ์ทั้งหมด
  const [displayedResults, setDisplayedResults] = useState([]); // ผลลัพธ์ที่แสดงในหน้าปัจจุบัน
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // การตั้งค่าสำหรับ pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(15);
  const [totalPages, setTotalPages] = useState(0);

  // คำนวณจำนวนหน้าทั้งหมดและอัปเดตผลลัพธ์ที่แสดง
  useEffect(() => {
    if (allResults.length > 0) {
      setTotalPages(Math.ceil(allResults.length / itemsPerPage));
      
      // คำนวณ index ของรายการแรกและรายการสุดท้ายที่จะแสดงในหน้าปัจจุบัน
      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      
      // ตัดเฉพาะข้อมูลที่ต้องการแสดงในหน้าปัจจุบัน
      setDisplayedResults(allResults.slice(startIndex, endIndex));
    } else {
      setDisplayedResults([]);
      setTotalPages(0);
    }
  }, [allResults, currentPage, itemsPerPage]);

  // สร้างฟังก์ชัน debounced search เพื่อไม่ให้ค้นหาบ่อยเกินไป
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      setIsLoading(true);
      try {
        const response = await searchDataCFPlabel(searchQuery);
        console.log('Search Results:', response);
        
        const data = response.data || response;
        
        if (Array.isArray(data)) {
          setAllResults(data);
        } else if (data && typeof data === 'object' && data.results && Array.isArray(data.results)) {
          setAllResults(data.results);
        } else {
          console.error('Unexpected response format:', data);
          setAllResults([]);
          setError('The data format received is not correct');
        }
        setCurrentPage(1); // กลับไปที่หน้าแรกเมื่อผลลัพธ์การค้นหาเปลี่ยน
      } catch (err) {
        console.error('Search Error:', err);
        setError('Unable to search. Please try again.');
        setAllResults([]);
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
        const response = await searchDataCFPlabel('');
        console.log('Initial data load:', response);
        
        const data = response.data || response;
        
        if (Array.isArray(data)) {
          setAllResults(data);
        } else if (data && typeof data === 'object' && data.results && Array.isArray(data.results)) {
          setAllResults(data.results);
        } else {
          console.error('Unexpected response format:', data);
          setAllResults([]);
          setError('The data format received is not correct.');
        }
      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Failed to load initial data. Please try again.');
        setAllResults([]);
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
  
  // เปลี่ยนหน้า
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };
  
  // สร้างปุ่มสำหรับ pagination
  const renderPaginationButtons = () => {
    const buttons = [];
    
    // ปุ่มย้อนกลับหน้า
    buttons.push(
      <button
        key="prev"
        onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === 1 
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
            : 'bg-teal-100 text-teal-700 hover:bg-teal-200'
        }`}
      >
        &laquo; Previous
      </button>
    );
    
    // จำนวนปุ่มที่จะแสดง (แสดงสูงสุด 5 ปุ่ม)
    const maxVisibleButtons = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisibleButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);
    
    // ปรับค่า startPage ถ้า endPage เกินจำนวนหน้าทั้งหมด
    if (endPage - startPage + 1 < maxVisibleButtons && startPage > 1) {
      startPage = Math.max(1, endPage - maxVisibleButtons + 1);
    }
    
    // เพิ่มจุดไข่ปลาถ้ามีหน้าก่อนหน้า startPage
    if (startPage > 1) {
      buttons.push(
        <button
          key="start"
          onClick={() => handlePageChange(1)}
          className="mx-1 px-3 py-1 rounded bg-teal-100 text-teal-700 hover:bg-teal-200"
        >
          1
        </button>
      );
      
      if (startPage > 2) {
        buttons.push(
          <span key="ellipsis1" className="mx-1 px-2 py-1">
            ...
          </span>
        );
      }
    }
    
    // สร้างปุ่มหน้า
    for (let i = startPage; i <= endPage; i++) {
      buttons.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`mx-1 px-3 py-1 rounded ${
            currentPage === i 
              ? 'bg-teal-600 text-white' 
              : 'bg-teal-100 text-teal-700 hover:bg-teal-200'
          }`}
        >
          {i}
        </button>
      );
    }
    
    // เพิ่มจุดไข่ปลาถ้ามีหน้าหลัง endPage
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        buttons.push(
          <span key="ellipsis2" className="mx-1 px-2 py-1">
            ...
          </span>
        );
      }
      
      buttons.push(
        <button
          key="end"
          onClick={() => handlePageChange(totalPages)}
          className="mx-1 px-3 py-1 rounded bg-teal-100 text-teal-700 hover:bg-teal-200"
        >
          {totalPages}
        </button>
      );
    }
    
    // ปุ่มไปหน้าถัดไป
    buttons.push(
      <button
        key="next"
        onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages}
        className={`mx-1 px-3 py-1 rounded ${
          currentPage === totalPages 
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
            : 'bg-teal-100 text-teal-700 hover:bg-teal-200'
        }`}
      >
        Next &raquo;
      </button>
    );
    
    return buttons;
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
            <span className="mr-2 text-4xl">🛍️</span>
            Emission Factor (CFP Label: Carbon Footprint for Thailand Product)
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
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6 max-w-3xl mx-auto">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* แสดงผลลัพธ์ในตาราง */}
        {!isLoading && allResults.length > 0 ? (
          <div className="w-full">
            <h3 className="text-xl font-semibold text-teal-800 mb-4">
              {query.trim() ? `Search results for "${query}"` : 'All available data'}
              <span className="ml-2 text-gray-600 text-base">({allResults.length} items)</span>
            </h3>
            
            {/* Show information about currently displayed items */}
            <div className="flex justify-between items-center mb-3">
              <div className="text-sm text-gray-600">
                Showing items {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, allResults.length)} of {allResults.length} total
              </div>
              <div className="flex items-center">
                <label htmlFor="itemsPerPage" className="text-sm text-gray-600 mr-2">Items per page:</label>
                <select 
                  id="itemsPerPage"
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1); // Return to first page when changing items per page
                  }}
                  className="border border-gray-300 rounded px-2 py-1 text-sm"
                >
                  <option value={10}>10</option>
                  <option value={15}>15</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
            
            <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg mb-4">
              <DataTableCFPLabel data={displayedResults} />
            </div>
            
            {/* แสดง Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center my-6">
                <div className="flex flex-wrap">
                  {renderPaginationButtons()}
                </div>
              </div>
            )}
          </div>
        ) : !isLoading ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200 max-w-3xl mx-auto">
            <p className="text-lg text-gray-600">
              {query.trim() ? `No data found for "${query}"` : 'No data available'}
            </p>
          </div>
        ) : (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-600"></div>
            <span className="ml-3 text-lg text-teal-700">Loading data...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPageCFPLabel;