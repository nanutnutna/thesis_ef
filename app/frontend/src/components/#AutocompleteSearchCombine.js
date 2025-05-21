import React, { useState, useEffect, useCallback } from 'react';
import { fetchAutocompleteCombine, searchDataCombine, createDate} from '../api/api';
import DataTableCombine from './DataTableCombine';

const AutocompleteSearchCombine = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [isFocused, setIsFocused] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [creationDate, setCreationDate] = useState('');


  useEffect(() => {
    const fetchCreationDate = async () => {
      try {
        const response = await createDate(); // API Endpoint สำหรับ creationDate
        setCreationDate(response.data.creation_date || 'Unknown');
      } catch (err) {
        console.error('Error fetching creation date:', err);
        setCreationDate('Unknown');
      }
    };

    fetchCreationDate();
  }, []);



  // โหลดข้อมูลเริ่มต้น
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const response = await searchDataCombine('');
        setResults(response.data || []);
      } catch (err) {
        console.error('Initial Load Error:', err);
        setError('Failed to load initial data');
      } finally {
        setIsInitialLoad(false);
      }
    };

    fetchInitialData();
  }, []);

  // จัดการการเปลี่ยนแปลงใน Input
  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.trim() !== '') {
      try {
        const response = await fetchAutocompleteCombine(value);
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        console.error('Autocomplete Error:', err);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      await handleSearch('');
    }
  };

  // เลือกคำแนะนำ
  const handleSelectSuggestion = async (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    await handleSearch(suggestion);
  };

  // ค้นหา
  const handleSearch = useCallback(async (searchQuery) => {
    try {
      const response = await searchDataCombine(searchQuery || query);
      setResults(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Search Error:', err);
      setError('Failed to fetch search results');
      setResults([]);
    }
  }, [query]);

  // โหลดข้อมูลทั้งหมดหาก Query ว่าง
  useEffect(() => {
    if (query.trim() === '') {
      handleSearch('');
    }
  }, [query, handleSearch]);

  return (
    <div style={styles.container}>
      <div style={styles.searchBoxContainer}>
        <h1 style={styles.header}>Emission Factor</h1>
        <div style={styles.searchWrapper}>
          <span style={styles.searchIcon}>🔍</span>
          <input
            type="text"
            placeholder="Type for search..."
            value={query}
            onChange={handleChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setTimeout(() => setIsFocused(false), 200)}
            style={styles.searchBox}
          />
        </div>
        {/* แสดงคำแนะนำ */}
        {isFocused && suggestions.length > 0 && (
          <div style={styles.suggestionsBox}>
            <ul style={styles.suggestionsList}>
              {suggestions.map((suggestion, index) => (
                <li
                  key={index}
                  style={styles.suggestionItem}
                  onMouseDown={() => handleSelectSuggestion(suggestion)}
                >
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* แสดง Error */}
      {error && <p style={styles.error}>{error}</p>}

      {/* แสดงสถานะการโหลดครั้งแรก */}
      {isInitialLoad && <p>Loading initial data...</p>}

      {/* แสดง creationDate */}
      <div style={styles.creationDate}>
        <p>Last Update: {creationDate}</p>
      </div>

      {/* แสดงผลลัพธ์ในตาราง */}
      {results.length > 0 ? (
        <div style={styles.tableWrapper}>
          <DataTableCombine data={results} />
        </div>
      ) : (
        <p>No data available</p>
      )}
    </div>
  );
};

const styles = {
  header: {
    fontSize: '24px',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: '20px',
    color: '#333',
  },
  container: {
    padding: '40px 20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    backgroundColor: '#f9fafc',
    minHeight: '100vh', // ใช้พื้นที่เต็มหน้าจอแนวตั้ง
  },
  searchBoxContainer: {
    width: '80%',
    maxWidth: '800px',
    marginBottom: '20px',
    position: 'relative',
  },
  searchWrapper: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: '#fff',
    border: '1px solid #ccc',
    borderRadius: '8px',
    overflow: 'hidden',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  searchIcon: {
    padding: '0 10px',
    fontSize: '1.2rem',
    color: '#888',
  },
  searchBox: {
    width: '100%',
    padding: '12px 15px',
    fontSize: '1rem',
    border: 'none',
    outline: 'none',
  },
  suggestionsBox: {
    position: 'absolute',
    top: '100%',
    left: 0,
    width: '100%',
    backgroundColor: '#fff',
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    marginTop: '4px',
    maxHeight: '300px',
    overflowY: 'auto',
    zIndex: 1000,
  },
  suggestionsList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
  },
  suggestionItem: {
    padding: '12px',
    cursor: 'pointer',
    borderBottom: '1px solid #e0e0e0',
  },
  error: {
    color: 'red',
    marginTop: '10px',
  },
  tableWrapper: {
    width: '100%', // ขยายเต็มหน้าจอ
    marginTop: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    backgroundColor: '#fff',
  },
  creationDate: {
    position: 'absolute',
    top: '20px',
    right: '20px',
    fontSize: '14px',
    color: '#555',
  },
};


export default AutocompleteSearchCombine;
