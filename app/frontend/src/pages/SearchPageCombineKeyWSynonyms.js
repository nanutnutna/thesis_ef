import React, { useState, useEffect, useMemo } from 'react';
import { searchDataKeyWSynonyms } from "../api/api";
import DataTableCombine from '../components/DataTableCombine';
import { Link } from 'react-router-dom';
import { debounce } from 'lodash';

const SearchPageCombineKeyWSynonyms = () => {
  const [query, setQuery] = useState('');
  const [allResults, setAllResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [displayedResults, setDisplayedResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // การตั้งค่าสำหรับ pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(15);
  const [totalPages, setTotalPages] = useState(0);

  // State สำหรับ filter
  const [selectedCategories, setSelectedCategories] = useState([]);

  // State สำหรับ tooltip
  const [tooltip, setTooltip] = useState({
    show: false,
    content: '',
    x: 0,
    y: 0
  });

  // รายการหมวดหมู่
  const categories = [
    'กลุ่มปิโตรเคมี',
    'กลุ่มผลิตภัณฑ์จากก๊าซธรรมชาติ',
    'กลุ่มพลังงาน: เชื้อเพลิงเหลว และเชื้อเพลิงแข็ง',
    'กลุ่มไฟฟ้า',
    'กลุ่มน้ำประปาและน้ำอุตสาหกรรม (Tap water)',
    'กลุ่มการขนส่งโดยรถบรรทุก (Truck Transportations) และขนส่งประเภทอื่น ๆ (Others)',
    'สิ่งทอ',
    'กลุ่มอุตสาหกรรมยางธรรมชาติ (Natural rubber)',
    'กลุ่มอุตสาหกรรมโรงเลื่อยและโรงอบไม้ยางพารา (Wood Processing : Para-wood)',
    'ปาล์มน้ำมัน',
    'กลุ่มอาหารสัตว์',
    'กลุ่มผลิตภัณฑ์ทางการเกษตรและอาหาร',
    'กลุ่มปศุสัตว์',
    'กลุ่มผลิตภัณฑ์ที่ได้จากสัตว์และกลุ่มผลิตภัณฑ์ทางการเกษตร',
    'กลุ่มเครื่องจักรกลทางการเกษตร',
    'กลุ่มการจัดการมูลฝอยชุมชน และการปรับปรุงน้ำเสียชุมชน',
    'กลุ่มเยื่อและกระดาษ',
    'กลุ่มเคมีภัณฑ์ (Chemicals)',
    'กลุ่มการฝังกลบขยะ',
    'กลุ่มแก้วและกระจก',
    'กลุ่มไหมหัตถกรรม (Sericulture)',
    'Stationary Combustion',
    'Mobile Combustion (On road)',
    'Mobile Combustion (Off road), Diesel',
    'Mobile Combustion (On road), Motor Gasoline 4 stroke',
    'Mobile Combustion (On road), Motor Gasoline 2 stroke',
    'Electricity, grid mix (ไฟฟ้า)',
    'Refrigerants (สารทำความเย็น)',
    'อื่นๆ',
    'ปิโตรเคมี และเคมีภัณฑ์',
    'ปิโตรเลี่ยม',
    'ยานยนต์',
    'หัตถกรรม และเครื่องประดับ',
    'พลาสติก และบรรจุภัณฑ์',
    'อาหาร',
    'ก่อสร้าง',
    'อลูมิเนียม และกระป๋อง',
    'สิ่งพิมพ์',
    'กระดาษ และบรรจุภัณฑ์',
    'เครื่องใช้ไฟฟ้า และอิเล็กทรอนิกส์',
    'เครื่องดื่ม',
    'ยางพารา',
    'ยา และเวชภัณฑ์',
    'ภาคการบริการ และสำนักงาน',
    'ไม้',
    '-',
    'ผลิต และจำหน่ายไฟฟ้า',
    'แก้ว และกระจกและบรรจุภัณฑ์',
    'ของเล่น',
    'อาหารสัตว์'
  ];

  // 🆕 ฟังก์ชัน tooltip ที่แสดงเฉพาะใน Name column
  const showTooltip = (event, item) => {
    const rect = event.currentTarget.getBoundingClientRect();
    
    // แสดงข้อมูลทั้งหมดที่มีใน object (ยกเว้นข้อมูลที่แสดงในตารางแล้ว)
    const excludeKeys = ['Category', 'category', 'Name', 'name', 'Unit', 'unit', 'Factor', 'factor', 'Reference', 'reference', 'Last_Updated', 'score'];
    
    const infoLines = [];
    
    Object.keys(item).forEach(key => {
      if (!excludeKeys.includes(key) && item[key] !== null && item[key] !== undefined && item[key] !== '' && item[key] !== '-') {
        const value = item[key].toString();
        // เพิ่มความยาวที่แสดงได้
        const displayValue = value.length > 300 ? value.substring(0, 300) + '...' : value;
        // ใช้ชื่อ field ที่อ่านง่ายขึ้น
        const displayKey = key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
        infoLines.push(`${displayKey}: ${displayValue}`);
      }
    });

    // ถ้าไม่มีข้อมูลเพิ่มเติม ให้แสดงรายชื่อ fields ทั้งหมด
    const tooltipContent = infoLines.length > 0 
      ? infoLines.join('\n\n') // เพิ่มระยะห่างระหว่างบรรทัด
      : 'Available fields:\n' + Object.keys(item).join(', ');

    setTooltip({
      show: true,
      content: tooltipContent,
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    });
  };

  // ฟังก์ชันซ่อน tooltip
  const hideTooltip = () => {
    setTooltip({
      show: false,
      content: '',
      x: 0,
      y: 0
    });
  };

  // ฟังก์ชันกรองข้อมูลตามหมวดหมู่
  useEffect(() => {
    let filtered = allResults;
    
    if (selectedCategories.length > 0) {
      filtered = allResults.filter(item => 
        selectedCategories.some(category =>
          item.category === category || 
          item.หมวดหมู่ === category ||
          item.Category === category ||
          item.กลุ่ม === category
        )
      );
    }
    
    setFilteredResults(filtered);
    setCurrentPage(1);
  }, [allResults, selectedCategories]);

  // คำนวณจำนวนหน้าทั้งหมดและอัปเดตผลลัพธ์ที่แสดง
  useEffect(() => {
    if (filteredResults.length > 0) {
      setTotalPages(Math.ceil(filteredResults.length / itemsPerPage));
      
      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      
      setDisplayedResults(filteredResults.slice(startIndex, endIndex));
    } else {
      setDisplayedResults([]);
      setTotalPages(0);
    }
  }, [filteredResults, currentPage, itemsPerPage]);

  // สร้างฟังก์ชัน debounced search
  const debouncedSearch = useMemo(
    () => debounce(async (searchQuery) => {
      setIsLoading(true);
      try {
        const response = await searchDataKeyWSynonyms(searchQuery);
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
        setCurrentPage(1);
      } catch (err) {
        console.error('Search Error:', err);
        setError('Unable to search. Please try again.');
        setAllResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  // โหลดข้อมูลเริ่มต้น
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        const response = await searchDataKeyWSynonyms('');
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

  // จัดการการเปลี่ยนหมวดหมู่
  const handleCategoryChange = (category) => {
    setSelectedCategories(prev => {
      if (prev.includes(category)) {
        return prev.filter(cat => cat !== category);
      } else {
        return [...prev, category];
      }
    });
  };

  // ล้างตัวกรอง
  const clearAllFilters = () => {
    setSelectedCategories([]);
  };

  // ลบ filter เฉพาะหมวดหมู่
  const removeCategory = (categoryToRemove) => {
    setSelectedCategories(prev => prev.filter(cat => cat !== categoryToRemove));
  };
  
  // สร้างปุ่มสำหรับ pagination
  const renderPaginationButtons = () => {
    const buttons = [];
    
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
    
    const maxVisibleButtons = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisibleButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);
    
    if (endPage - startPage + 1 < maxVisibleButtons && startPage > 1) {
      startPage = Math.max(1, endPage - maxVisibleButtons + 1);
    }
    
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
      {/* Tooltip Component */}
      {tooltip.show && (
        <div
          className="fixed z-50 bg-gray-800 text-white text-sm p-4 rounded-lg shadow-lg pointer-events-none"
          style={{
            left: tooltip.x,
            top: tooltip.y,
            transform: 'translate(-50%, -100%)',
            maxWidth: '400px',
            minWidth: '300px',
            maxHeight: '300px',
          }}
        >
          <div 
            className="overflow-y-auto"
            style={{
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              lineHeight: '1.5',
              maxHeight: '280px'
            }}
          >
            {tooltip.content}
          </div>
          {/* Arrow */}
          <div
            className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0"
            style={{
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderTop: '8px solid #374151'
            }}
          />
        </div>
      )}

      {/* ปุ่มกลับหน้า Home */}
      <div className="fixed top-4 left-4 z-10">
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

      {/* Filter Section */}
      <div className="fixed top-20 left-4 z-10">
        <div className="w-72 bg-white rounded-lg shadow-md border border-gray-200">
          {selectedCategories.length > 0 && (
            <div className="p-4 border-b border-gray-200">
              <button
                onClick={clearAllFilters}
                className="flex items-center text-sm text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded-md transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Reset Filters
              </button>
            </div>
          )}

          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-800 uppercase tracking-wide mb-3">
              CATEGORY
            </h3>
            
            {selectedCategories.length > 0 && (
              <div className="mb-4">
                <div className="text-xs text-gray-600 mb-2">
                  Selected ({selectedCategories.length}):
                </div>
                <div className="space-y-1">
                  {selectedCategories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between bg-green-50 border-green-200 rounded px-2 py-1">
                      <span className="text-xs text-green-700 truncate">{category}</span>
                      <button
                        onClick={() => removeCategory(category)}
                        className="ml-1 text-green-700 hover:text-red-600 flex-shrink-0"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="relative">
              <select 
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 appearance-none bg-white"
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    handleCategoryChange(e.target.value);
                  }
                }}
              >
                <option value="">Select Category...</option>
                {categories.filter(cat => !selectedCategories.includes(cat)).map((category, index) => (
                  <option key={index} value={category}>
                    {category}
                  </option>
                ))}
              </select>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 absolute right-3 top-3 text-gray-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <div className="p-4 border-t border-gray-200">
            <div className="text-sm text-gray-600 mb-2">
              FILTER RESULTS
            </div>
            <div className="text-xs text-gray-500">
              {selectedCategories.length > 0 
                ? `${selectedCategories.length} filter(s) applied` 
                : 'No filters applied'
              }
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="max-w-7xl mx-auto bg-gray-100 rounded-xl shadow-lg p-6 mt-16 ml-80">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-teal-800 text-center mb-6 flex items-center justify-center">
            <span className="mr-2 text-4xl">🛍️</span>
            Emission Factor (CFO & CFP)
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

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6 max-w-3xl mx-auto">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {!isLoading && allResults.length > 0 ? (
          <div className="w-full">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                {filteredResults.length.toLocaleString()} results found
                {query.trim() && (
                  <span> for "{query}"</span>
                )}
              </h2>
              <div className="text-sm text-gray-600">
                {filteredResults.length.toLocaleString()} Activities, {filteredResults.length.toLocaleString()} Emission factors
              </div>
              {selectedCategories.length > 0 && (
                <div className="text-sm text-teal-600 mt-1">
                  Filtered by {selectedCategories.length} categories
                </div>
              )}
            </div>
            
            <div className="flex justify-between items-center mb-4">
              <div className="text-sm text-gray-600">
                Showing items {filteredResults.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} - {Math.min(currentPage * itemsPerPage, filteredResults.length)} of {filteredResults.length.toLocaleString()} total
              </div>
              <div className="flex items-center">
                <label htmlFor="itemsPerPage" className="text-sm text-gray-600 mr-2">Items per page:</label>
                <select 
                  id="itemsPerPage"
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500"
                >
                  <option value={10}>10</option>
                  <option value={15}>15</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
            
            {filteredResults.length > 0 ? (
              <>
                <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg mb-4">
                  <DataTableCombine 
                    data={displayedResults}
                    onMouseEnter={showTooltip}
                    onMouseLeave={hideTooltip}
                  />
                </div>
                
                {totalPages > 1 && (
                  <div className="flex justify-center my-6">
                    <div className="flex flex-wrap">
                      {renderPaginationButtons()}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-gray-400 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0118 12a8 8 0 01-8 8 8 8 0 01-8-8 8 8 0 018-8c2.027 0 3.9.757 5.321 2M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <p className="text-lg text-gray-600 mb-2">
                  No data found for the selected criteria
                </p>
                <p className="text-gray-500 mb-4">
                  Try adjusting your search terms or filters
                </p>
                {selectedCategories.length > 0 && (
                  <button
                    onClick={clearAllFilters}
                    className="text-teal-600 hover:text-teal-800 font-medium"
                  >
                    Clear all filters
                  </button>
                )}
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

export default SearchPageCombineKeyWSynonyms;