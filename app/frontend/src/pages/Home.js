import React, { useEffect, useState } from 'react';
import { testAPI } from '../api/api'; // ตรวจสอบให้แน่ใจว่า path ถูกต้อง

function Home() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await testAPI();
        setMessage(response.data.message || 'API connected successfully!');
      } catch (error) {
        console.error('Error fetching data:', error);
        setMessage('Failed to connect to API');
      }
    };
    fetchData();
  }, []);

  return (
    <div>
      <h1>🏠 Home Page</h1>
      <p>{message}</p>
    </div>
  );
}

export default Home;
