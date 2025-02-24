import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';

const SynonymsDictionary = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [fileError, setFileError] = useState(false);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const url = 'https://raw.githubusercontent.com/nanutnutna/synonyms/refs/heads/main/synonyms2.csv';
        
        const response = await fetch(url);
        const csvText = await response.text();
        
        // ใช้ Papaparse เพื่อแยกข้อมูล CSV
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            console.log('Complete results:', results);
            
            const processedData = results.data.map(row => {
              const synonyms = [];
              
              // เก็บค่าทุกคอลัมน์ที่ไม่ใช่ค่าว่าง
              Object.entries(row).forEach(([key, value]) => {
                if (value && value.trim()) {
                  synonyms.push(value.trim());
                }
              });
              
              return {
                ...row,
                allSynonyms: synonyms
              };
            });
            
            setData(processedData);
            setFilteredData(processedData);
            setLoading(false);
          },
          error: (error) => {
            console.error('Error parsing CSV:', error);
            setFileError(true);
            setLoading(false);
          }
        });
      } catch (error) {
        console.error('Error loading CSV data:', error);
        setFileError(true);
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // กรองข้อมูลตามคำค้นหา
  useEffect(() => {
    let result = data;
    
    // กรองตามคำค้นหา
    if (searchTerm) {
      result = result.filter(item => 
        item.allSynonyms.some(synonym => 
          synonym.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
    
    setFilteredData(result);
    setCurrentPage(1); // รีเซ็ตหน้าเมื่อเปลี่ยนการค้นหา
  }, [searchTerm, data]);
  
  // คำนวณข้อมูลสำหรับการแบ่งหน้า
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  
  // เปลี่ยนหน้า
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-500">กำลังโหลดข้อมูล...</div>
      </div>
    );
  }
  
  if (fileError) {
    return (
      <div className="flex flex-col justify-center items-center h-64 gap-4">
        <div className="text-xl text-red-500 font-medium">ไม่สามารถโหลดไฟล์ CSV ได้</div>
        <div className="text-gray-600 max-w-md text-center">
          โปรดตรวจสอบการเชื่อมต่ออินเทอร์เน็ตของคุณและลองใหม่อีกครั้ง
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-6">Synonyms Dictionary</h1>
      
      {/* ช่องค้นหา */}
      <div className="mb-6">
        <div className="flex-1">
          <input
            type="text"
            placeholder="ค้นหาคำศัพท์..."
            className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      {/* แสดงจำนวนผลลัพธ์ */}
      <div className="text-gray-600 mb-4">
        พบ {filteredData.length} รายการ
      </div>
      
      {/* แสดงรายการคำศัพท์ */}
      <div className="grid grid-cols-1 gap-4">
        {currentItems.length > 0 ? (
          currentItems.map((item, index) => (
            <div key={index} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-gray-50 p-4 border-b">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold">{item.Agriculture}</h2>
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-700 mb-2">คำเหมือน:</h3>
                <div className="flex flex-wrap gap-2">
                  {item.allSynonyms.map((synonym, idx) => (
                    <span 
                      key={idx} 
                      className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm"
                    >
                      {synonym}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center p-8 text-gray-500 border rounded">
            ไม่พบข้อมูลที่ตรงกับการค้นหา
          </div>
        )}
      </div>
      
      {/* ระบบแบ่งหน้า */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <nav className="flex items-center">
            <button 
              onClick={() => paginate(currentPage > 1 ? currentPage - 1 : 1)}
              disabled={currentPage === 1}
              className={`px-3 py-2 rounded-l border ${
                currentPage === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white hover:bg-gray-50'
              }`}
            >
              &laquo; ก่อนหน้า
            </button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              // แสดงปุ่มหน้า 5 ปุ่มรอบๆ หน้าปัจจุบัน
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => paginate(pageNum)}
                  className={`px-4 py-2 border-t border-b ${
                    currentPage === pageNum 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white hover:bg-gray-50'
                  } ${i === 0 ? '' : 'border-l'}`}
                >
                  {pageNum}
                </button>
              );
            })}
            
            <button 
              onClick={() => paginate(currentPage < totalPages ? currentPage + 1 : totalPages)}
              disabled={currentPage === totalPages}
              className={`px-3 py-2 rounded-r border ${
                currentPage === totalPages ? 'bg-gray-100 text-gray-400' : 'bg-white hover:bg-gray-50'
              }`}
            >
              ถัดไป &raquo;
            </button>
          </nav>
        </div>
      )}
      
      <div className="mt-6 text-sm text-center text-gray-500">
        ข้อมูลทั้งหมด {data.length} รายการ | แสดงหน้า {currentPage} จาก {totalPages} หน้า
      </div>
    </div>
  );
};

export default SynonymsDictionary;