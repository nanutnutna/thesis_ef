import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { testAPI } from '../api/api';

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

  const styles = {
    container: {
      textAlign: 'center',
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
    },
    buttonContainer: {
      marginTop: '20px',
      display: 'flex',
      flexWrap: 'wrap',
      gap: '15px',
      justifyContent: 'center',
    },
    button: {
      display: 'inline-block',
      padding: '15px 30px',
      fontSize: '18px', 
      color: 'white',
      backgroundColor: '#007bff',
      border: 'none',
      borderRadius: '8px',
      textDecoration: 'none',
      transition: 'background-color 0.3s ease, transform 0.2s ease', 
      cursor: 'pointer',
    },
    buttonHover: {
      backgroundColor: '#0056b3',
      transform: 'scale(1.05)',
    },
  };
  return (
    <div style={styles.container}>
      <h1>🏠 Home Page</h1>
      <p>{message}</p>
      <div style={styles.buttonContainer}>
        <Link
          to="/search"
          style={styles.button}
          onMouseEnter={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseLeave={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          Gen-Search
        </Link>
        <Link
          to="/cfp"
          style={styles.button}
          onMouseEnter={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseLeave={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          CFP
        </Link>
        <Link
          to="/cfo"
          style={styles.button}
          onMouseEnter={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseLeave={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          CFO
        </Link>
        <Link
          to="/clp"
          style={styles.button}
          onMouseEnter={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseLeave={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          CLP
        </Link>
        <Link
          to="/combine"
          style={styles.button}
          onMouseEnter={(e) => (e.target.style.backgroundColor = styles.buttonHover.backgroundColor)}
          onMouseLeave={(e) => (e.target.style.backgroundColor = styles.button.backgroundColor)}
        >
          Search
        </Link>
      </div>
    </div>
  );
}

export default Home;
