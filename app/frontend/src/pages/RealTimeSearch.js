import React, { useState, useEffect } from 'react';
import SearchBar from '../components/SearchBar';
import DataTable from '../components/DataTable';

const RealTimeSearch = () => {
  const [query, setQuery] = useState(''); // ข้อความค้นหา
  const [results, setResults] = useState([]); // เก็บผลลัพธ์จาก API
  const [socket, setSocket] = useState(null); // WebSocket Instance
  const [loading, setLoading] = useState(false); // สถานะโหลด
  const [error, setError] = useState(null); // สถานะข้อผิดพลาด

  useEffect(() => {
    // สร้างการเชื่อมต่อ WebSocket
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/search');
    setSocket(ws);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setResults(data.results || []);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setError('WebSocket connection failed');
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
    };

    return () => {
      ws.close(); // ปิดการเชื่อมต่อเมื่อ Component ถูก unmount
    };
  }, []);

  /**
   * ส่งข้อความไปยัง WebSocket
   */
  const handleSearch = (e) => {
    const value = e.target.value;
    setQuery(value);

    if (socket && value.trim() !== '') {
      socket.send(value); // ส่งข้อความไปยัง Backend ผ่าน WebSocket
      setLoading(true);
    } else {
      setResults([]);
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '20px' }}>
      <h1>🔍 Real-Time Search with WebSocket</h1>
      <SearchBar query={query} setQuery={handleSearch} />
      {loading && <p>⏳ Loading...</p>}
      {error && <p style={{ color: 'red' }}>❌ {error}</p>}
      <DataTable results={results} />
    </div>
  );
};

export default RealTimeSearch;
