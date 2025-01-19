import React from 'react';

const DataTableCombine = ({ data }) => {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.header}>กลุ่ม</th>
            <th style={styles.header}>ชื่อ</th>
            <th style={styles.header}>รายละเอียด</th>
            <th style={styles.header}>หน่วย</th>
            <th style={styles.header}>ค่าแฟคเตอร์ (kgCO2e)</th>
            <th style={styles.header}>ข้อมูลอ้างอิง</th>
            <th style={styles.header}>ประเภทแฟคเตอร์</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} style={styles.row}>
              <td style={styles.cell}>{item.กลุ่ม || '-'}</td>
              <td style={styles.cell}>{item.ชื่อ || '-'}</td>
              <td style={styles.cell}>{item.รายละเอียด || '-'}</td>
              <td style={styles.cell}>{item.หน่วย || '-'}</td>
              <td style={styles.cell}>{item['ค่าแฟคเตอร์ (kgCO2e)'] || '-'}</td>
              <td style={styles.cell}>{item.ข้อมูลอ้างอิง || '-'}</td>
              <td style={styles.cell}>{item.ประเภทแฟคเตอร์ || '-'}</td>
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

export default DataTableCombine;
