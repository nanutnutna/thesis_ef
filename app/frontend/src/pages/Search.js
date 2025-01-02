import React, { useState } from 'react';
import { searchData } from '../api/api';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    try {
      const response = await searchData(query);
      console.log('Response:', response.data);
      setResults(response.data);
      setError(null);
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to fetch search results');
      setResults([]);
    }
  };

  return (
    <div>
      <h1>🔍 Search Data</h1>
      <input
        type="text"
        placeholder="Enter search query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {/* แสดงตารางผลลัพธ์ */}
      {results.length > 0 && (
        <table border="1" style={{ marginTop: '20px', width: '100%', textAlign: 'left' }}>
          <thead>
            <tr>
              <th>กลุ่ม</th>
              <th>ลำดับ</th>
              <th>ชื่อ</th>
              <th>รายละเอียด</th>
              <th>หน่วย</th>
              <th>ค่าแฟคเตอร์ (kgCO2e)</th>
              <th>ข้อมูลอ้างอิง</th>
              <th>วันที่อัพเดท</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item, index) => (
              <tr key={index}>
                <td>{item.กลุ่ม || 'N/A'}</td>
                <td>{item.ลำดับ || 'N/A'}</td>
                <td>{item.ชื่อ || 'N/A'}</td>
                <td>{item.รายละเอียด || 'N/A'}</td>
                <td>{item.หน่วย || 'N/A'}</td>
                <td>{item['ค่าแฟคเตอร์ (kgCO2e)'] || 'N/A'}</td>
                <td>{item['ข้อมูลอ้างอิง'] || 'N/A'}</td>
                <td>{item['วันที่อัพเดท'] || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Search;
