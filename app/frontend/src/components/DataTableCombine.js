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
            <th style={styles.header}>เปลี่ยนแปลง</th>
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
              <td style={styles.cell}>{item.เปลี่ยนแปลง || '-'}</td>
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
