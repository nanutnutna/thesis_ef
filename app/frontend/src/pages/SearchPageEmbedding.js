import React, { useState } from "react";
import { searchDataEmbedding } from "../api/api";

const SearchPageEmbedding = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a valid search query.");
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await searchDataEmbedding(query);
      console.log("Response Data:", response.data); 
      setResults(Array.isArray(response.data) ? response.data : []); 
    } catch (err) {
      console.error("Search Error:", err);
      setError("Failed to fetch search results. Please try again.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Search with Embedding</h1>
      <div style={styles.searchBoxContainer}>
        <input
          type="text"
          placeholder="Enter your query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={styles.searchBox}
        />
        <button onClick={handleSearch} style={styles.searchButton}>
          Search
        </button>
      </div>
      {loading && <p style={styles.loading}>Loading...</p>}
      {error && <p style={styles.error}>{error}</p>}
      <div style={styles.resultsContainer}>
        {results.length > 0 ? (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.headerCell}>กลุ่ม</th>
                <th style={styles.headerCell}>ชื่อ</th>
                <th style={styles.headerCell}>รายละเอียด</th>
                <th style={styles.headerCell}>หน่วย</th>
                <th style={styles.headerCell}>ค่าแฟคเตอร์ (kgCO2e)</th>
                <th style={styles.headerCell}>ข้อมูลอ้างอิง</th>
                <th style={styles.headerCell}>วันที่อัพเดท</th>
                <th style={styles.headerCell}>ประเภทแฟคเตอร์</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index}>
                  <td style={styles.cell}>{item.กลุ่ม || "-"}</td>
                  <td style={styles.cell}>{item.ชื่อ || "-"}</td>
                  <td style={styles.cell}>{item.รายละเอียด || "-"}</td>
                  <td style={styles.cell}>{item.หน่วย || "-"}</td>
                  <td style={styles.cell}>{item["ค่าแฟคเตอร์ (kgCO2e)"] || "-"}</td>
                  <td style={styles.cell}>{item.ข้อมูลอ้างอิง || "-"}</td>
                  <td style={styles.cell}>{item.วันที่อัพเดท || "-"}</td>
                  <td style={styles.cell}>{item.ประเภทแฟคเตอร์ || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !loading && <p>No results found.</p>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: "40px",
    maxWidth: "1000px",
    margin: "0 auto",
    backgroundColor: "#f9fafc",
    borderRadius: "8px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  },
  header: {
    textAlign: "center",
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "20px",
    color: "#333",
  },
  searchBoxContainer: {
    display: "flex",
    gap: "10px",
    marginBottom: "20px",
  },
  searchBox: {
    flex: 1,
    padding: "10px",
    fontSize: "16px",
    border: "1px solid #ccc",
    borderRadius: "5px",
  },
  searchButton: {
    padding: "10px 20px",
    backgroundColor: "#007BFF",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  loading: {
    textAlign: "center",
    color: "#007BFF",
  },
  error: {
    textAlign: "center",
    color: "red",
  },
  resultsContainer: {
    marginTop: "20px",
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    textAlign: "left",
  },
  headerCell: {
    backgroundColor: "#f4f4f4",
    fontWeight: "bold",
    padding: "12px",
    borderBottom: "1px solid #ccc",
  },
  cell: {
    padding: "12px",
    borderBottom: "1px solid #eee",
  },
};

export default SearchPageEmbedding;
