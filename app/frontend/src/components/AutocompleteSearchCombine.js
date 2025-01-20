import React, { useState, useEffect, useCallback } from 'react';
import { fetchAutocompleteCombine, searchDataCombine, createDate, listDropdownOptions } from '../api/api';
import DataTableCombine from './DataTableCombine';

const AutocompleteSearchCombine = () => {
  const [query, setQuery] = useState(''); // คำค้นหา
  const [suggestions, setSuggestions] = useState([]); // คำแนะนำ autocomplete
  const [results, setResults] = useState([]); // ผลลัพธ์การค้นหา
  const [error, setError] = useState(null); // ข้อผิดพลาด
  const [isFocused, setIsFocused] = useState(false); // สถานะ focus
  const [isInitialLoad, setIsInitialLoad] = useState(true); // โหลดข้อมูลเริ่มต้น
  const [creationDate, setCreationDate] = useState(''); // วันที่สร้างข้อมูล
  const [dropdownOptions, setDropdownOptions] = useState([]); // รายการวันที่
  const [selectedOption, setSelectedOption] = useState(''); // วันที่ที่เลือก

  // ดึงข้อมูล creation date
  useEffect(() => {
    const fetchCreationDate = async () => {
      try {
        const response = await createDate();
        setCreationDate(response.data.creation_date || 'Unknown');
      } catch (err) {
        console.error('Error fetching creation date:', err);
        setCreationDate('Unknown');
      }
    };

    fetchCreationDate();
  }, []);

  // ดึงรายการวันที่สำหรับ dropdown
  useEffect(() => {
    const fetchDropdownOptions = async () => {
      try {
        const response = await listDropdownOptions();
        if (response.data && Array.isArray(response.data.dates)) {
          setDropdownOptions(response.data.dates);
        } else {
          setDropdownOptions([]);
        }
      } catch (err) {
        console.error('Error fetching dropdown options:', err);
        setDropdownOptions([]);
      }
    };

    fetchDropdownOptions();
  }, []);

  // ฟังก์ชันดึงข้อมูลตาม query และ date
  const fetchData = useCallback(
    async (searchQuery = query, selectedDate = selectedOption) => {
      if (!selectedDate) {
        setError('Please select a date.');
        setResults([]);
        return;
      }

      try {
        const response = await searchDataCombine(searchQuery, selectedDate);
        setResults(response.results || []);
        setError(null);
      } catch (err) {
        console.error('Search Error:', err);
        setError('Failed to fetch search results');
        setResults([]);
      } finally {
        setIsInitialLoad(false);
      }
    },
    [query, selectedOption]
  );

  // เรียก fetchData เมื่อเปลี่ยน dropdown
  useEffect(() => {
    if (selectedOption) fetchData();
  }, [selectedOption, fetchData]);

  // จัดการเมื่อพิมพ์คำค้นหา
  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.trim() !== '') {
      try {
        const response = await fetchAutocompleteCombine(value, selectedOption);
        setSuggestions(response.suggestions || []);
      } catch (err) {
        console.error('Autocomplete Error:', err);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      fetchData('', selectedOption); // ค้นหาทั้งหมดเมื่อ query ว่าง
    }
  };

  // จัดการเมื่อเปลี่ยน dropdown
  const handleDropdownChange = (e) => {
    const selectedDate = e.target.value;
    setSelectedOption(selectedDate);
    setResults([]); // ล้างผลลัพธ์ก่อน
    setQuery(''); // ล้าง query
    fetchData('', selectedDate); // ดึงข้อมูลใหม่
  };

  // จัดการเมื่อเลือกคำแนะนำ
  const handleSelectSuggestion = async (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    await fetchData(suggestion);
  };

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
          <select
            value={selectedOption}
            onChange={handleDropdownChange}
            style={styles.dropdown}
          >
            <option value="">Select Date</option>
            {dropdownOptions.map((option, index) => {
              const formattedOption = `${option.slice(0, 4)}-${option.slice(4, 6)}-${option.slice(6)}`;
              return (
                <option key={index} value={option}>
                  {formattedOption}
                </option>
              );
            })}
          </select>
        </div>
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
      {error && <p style={styles.error}>{error}</p>}
      {isInitialLoad && <p>Loading initial data...</p>}
      <div style={styles.creationDate}>
        <p>Last Update: {creationDate}</p>
      </div>
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
    flex: 1,
    padding: '12px 15px',
    fontSize: '1rem',
    border: 'none',
    outline: 'none',
  },
  dropdown: {
    padding: '12px',
    fontSize: '1rem',
    border: 'none',
    outline: 'none',
    backgroundColor: '#fff',
    cursor: 'pointer',
    borderLeft: '1px solid #ccc',
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
    width: '100%',
    maxWidth: '1000px',
    marginTop: '20px',
    overflowX: 'auto',
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
