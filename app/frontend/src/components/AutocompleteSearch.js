import React, { useState, useEffect, useCallback } from 'react';
import { fetchAutocomplete, searchData } from '../api/api';
import DataTable from './DataTable';

const AutocompleteSearch = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [isFocused, setIsFocused] = useState(false);

  const handleSearch = useCallback(async (searchQuery) => {
    try {
      const response = await searchData(searchQuery || query);
      setResults(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Search Error:', err);
      setError('Failed to fetch search results');
      setResults([]);
    }
  }, [query]); // ✅ Stable Dependency

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.trim() !== '') {
        handleSearch(query);
      } else {
        setResults([]);
      }
    }, 500); // 500ms delay

    return () => clearTimeout(delayDebounceFn);
  }, [query, handleSearch]); // ✅ handleSearch Stable

  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.trim() !== '') {
      try {
        const response = await fetchAutocomplete(value);
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        console.error('Autocomplete Error:', err);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      setResults([]);
    }
  };

  const handleSelectSuggestion = async (suggestion) => {
    setQuery(suggestion);
    setSuggestions([]);
    await handleSearch(suggestion);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>🔍 Autocomplete Search</h1>
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          placeholder="Type to search..."
          value={query}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setTimeout(() => setIsFocused(false), 200)}
          style={{
            width: '300px',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ccc'
          }}
        />
        {isFocused && suggestions.length > 0 && (
          <ul style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            width: '300px',
            backgroundColor: '#fff',
            border: '1px solid #ccc',
            listStyleType: 'none',
            margin: 0,
            padding: 0,
            maxHeight: '200px',
            overflowY: 'auto',
            zIndex: 1000
          }}>
            {suggestions.map((suggestion, index) => (
              <li
                key={index}
                style={{
                  padding: '8px',
                  cursor: 'pointer',
                  backgroundColor: '#f9f9f9'
                }}
                onMouseDown={() => handleSelectSuggestion(suggestion)}
              >
                {suggestion}
              </li>
            ))}
          </ul>
        )}
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {results.length > 0 && <DataTable data={results} />}
    </div>
  );
};

export default AutocompleteSearch;
