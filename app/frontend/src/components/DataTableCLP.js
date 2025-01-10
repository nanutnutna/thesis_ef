import React from 'react';

const DataTableCLP = ({ data }) => {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.header}>ชื่อ</th>
            <th style={styles.header}>รายละเอียด</th>
            <th style={styles.header}>กลุ่ม</th>
            <th style={styles.header}>วันที่อนุมัติ</th>
            <th style={styles.header}>CF</th>
            <th style={styles.header}>หน่วยการทำงาน</th>
            <th style={styles.header}>ขอบเขต</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} style={styles.row}>
              <td style={styles.cell}>{item.ชื่อ || '-'}</td>
              <td style={styles.cell}>{item.รายละเอียด || '-'}</td>
              <td style={styles.cell}>{item.กลุ่ม || '-'}</td>
              <td style={styles.cell}>{item.วันที่อนุมัติ || '-'}</td>
              <td style={styles.cell}>{item['CF'] || '-'}</td>
              <td style={styles.cell}>{item.หน่วยการทำงาน || '-'}</td>
              <td style={styles.cell}>{item.ขอบเขต || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const styles = {
  tableContainer: {
    overflowX: 'auto',
    marginTop: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  header: {
    backgroundColor: '#f4f4f4',
    fontWeight: 'bold',
    textAlign: 'left',
    padding: '12px',
    borderBottom: '1px solid #ddd',
  },
  row: {
    borderBottom: '1px solid #eee',
  },
  cell: {
    padding: '12px',
    textAlign: 'left',
  },
};

export default DataTableCLP;
