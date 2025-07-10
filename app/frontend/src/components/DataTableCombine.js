import React from 'react';

const DataTableCombine = ({ data }) => {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.header}>Category</th>
            <th style={styles.header}>Name</th>
            <th style={styles.header}>Unit</th>
            <th style={styles.header}>Factor (kgCO2e/Unit)</th>
            <th style={styles.header}>Reference</th>
            <th style={styles.header}>Last Updated</th>
            <th style={styles.header}>Score</th>
            {/* <th style={styles.header}>วันที่มีผล</th>
            <th style={styles.header}>ประเภทแฟกเตอร์</th> */}
            {/* <th style={styles.header}>เปลี่ยนแปลง</th> */}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} style={styles.row}>
              <td style={styles.cell}>{item.Category || '-'}</td>
              <td style={styles.cell}>{item.Name || '-'}</td>
              <td style={styles.cell}>{item.Unit || '-'}</td>
              <td style={styles.cell}>{item.Factor || '-'}</td>
              <td style={styles.cell}>{item.Reference || '-'}</td>
              <td style={styles.cell}>{item.Last_Updated || '-'}</td>
              <td style={styles.cell}>{item.score || '-'}</td>
              {/* <td style={styles.cell}>{item.วันที่อัพเดท || '-'}</td>
              <td style={styles.cell}>{item.ประเภทแฟคเตอร์ || '-'}</td> */}
              {/* <td style={styles.cell}>{item.เปลี่ยนแปลง || '-'}</td> */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const styles = {
  tableContainer: {
    overflowX: 'auto', // เพิ่ม scroll ถ้าหน้าจอเล็ก
    marginTop: '20px',
    border: '1px solid #ccc',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    maxWidth: '100%', // ปรับให้เต็มหน้าจอ
  },
  table: {
    width: '100%', // ใช้พื้นที่ทั้งหมดของ container
    borderCollapse: 'collapse',
  },
  header: {
    backgroundColor: '#f4f4f4',
    fontWeight: 'bold',
    textAlign: 'left',
    padding: '12px',
    borderBottom: '1px solid #ddd',
    whiteSpace: 'nowrap', // ป้องกันตัดคำ
  },
  row: {
    borderBottom: '1px solid #eee',
  },
  cell: {
    padding: '12px',
    textAlign: 'left',
    wordWrap: 'break-word', // ตัดคำอัตโนมัติ
    maxWidth: '200px', // จำกัดความกว้างใน cell
  },
  '@media (max-width: 768px)': {
    cell: {
      fontSize: '14px', // ลดขนาดฟอนต์เมื่อหน้าจอเล็ก
      padding: '8px', // ลด padding บนหน้าจอเล็ก
    },
  },
};

export default DataTableCombine;
