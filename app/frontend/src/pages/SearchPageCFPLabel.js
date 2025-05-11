import React, { useState } from 'react';
import { searchDataCFPlabel } from "../api/api";
import DataTableCFPLabel from '../components/DataTableCFPLabel';

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
    <div style={styles.searchPageContainer}>
      <div style={styles.searchHeader}>
        <h1 style={styles.headerTitle}>Hybrid Search</h1>
        <p style={styles.headerDescription}>ค้นหาข้อมูลด้วยระบบค้นหาแบบไฮบริด</p>
      </div>

      <div style={styles.searchInputContainer}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="พิมพ์คำค้นหา..."
          style={styles.searchInput}
        />
        <button onClick={handleSearch} style={styles.searchButton}>
          ค้นหา
        </button>
      </div>

      {error && <div style={styles.errorMessage}>{error}</div>}

      {loading ? (
        <div style={styles.loadingIndicator}>กำลังค้นหา...</div>
      ) : (
        results.length > 0 && (
          <div style={styles.resultsContainer}>
            <h3>ผลการค้นหา</h3>
            <DataTableCFPLabel data={results} />
          </div>
        )
      )}

      {!loading && query && results.length === 0 && (
        <div style={styles.noResultsMessage}>ไม่พบข้อมูลสำหรับ "{query}"</div>
      )}
    </div>
  );
};

// Inline styles
const styles = {
  searchPageContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  searchHeader: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  headerTitle: {
    color: '#333',
    marginBottom: '10px',
  },
  headerDescription: {
    color: '#666',
  },
  searchInputContainer: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '30px',
  },
  searchInput: {
    width: '70%',
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '4px 0 0 4px',
    outline: 'none',
  },
  searchButton: {
    padding: '12px 24px',
    backgroundColor: '#2196f3',
    color: 'white',
    border: 'none',
    borderRadius: '0 4px 4px 0',
    cursor: 'pointer',
    fontSize: '16px',
    transition: 'background-color 0.3s',
  },
  errorMessage: {
    backgroundColor: '#ffebee',
    color: '#c62828',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px',
    textAlign: 'center',
  },
  loadingIndicator: {
    textAlign: 'center',
    padding: '20px',
    fontSize: '16px',
    color: '#666',
  },
  resultsContainer: {
    marginTop: '20px',
  },
  noResultsMessage: {
    textAlign: 'center',
    padding: '20px',
    color: '#666',
    fontStyle: 'italic',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
  }
};

export default SearchPageCFPLabel;