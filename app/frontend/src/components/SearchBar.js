import React from 'react';

const SearchBar = ({ query, setQuery }) => {
  return (
    <input
      type="text"
      placeholder="Type to search..."
      value={query}
      onChange={setQuery}
      style={{ width: '300px', padding: '8px', marginBottom: '10px' }}
    />
  );
};

export default SearchBar;
