import React from 'react';

const DataTableCFPLabel = ({ data }) => {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.header}>No</th>
            <th style={styles.header}>License</th>
            <th style={styles.header}>Name</th>
            <th style={styles.header}>Detail</th>
            <th style={styles.header}>Industrials</th>
            <th style={styles.header}>ApproveDate</th>
            <th style={styles.header}>EF</th>
            <th style={styles.header}>Unit</th>
            <th style={styles.header}>Scope</th>
            {/* <th style={styles.header}>Contract</th>
            <th style={styles.header}>Phone</th>
            <th style={styles.header}>Mail</th> */}
            <th style={styles.header}>Company_name</th>
            {/* <th style={styles.header}>เปลี่ยนแปลง</th> */}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} style={styles.row}>
              <td style={styles.cell}>{item.Seq || '-'}</td>
              <td style={styles.cell}>{item.License || '-'}</td>
              <td style={styles.cell}>{item.Name || '-'}</td>
              <td style={styles.cell}>{item.Detail || '-'}</td>
              <td style={styles.cell}>{item.Industrials || '-'}</td>
              <td style={styles.cell}>{item.ApproveDate || '-'}</td>
              <td style={styles.cell}>{item.EF || '-'}</td>
              <td style={styles.cell}>{item.Unit || '-'}</td>
              <td style={styles.cell}>{item.Scope || '-'}</td>
              {/* <td style={styles.cell}>{item.Contract || '-'}</td>
              <td style={styles.cell}>{item.Phone || '-'}</td>
              <td style={styles.cell}>{item.Mail || '-'}</td> */}
              <td style={styles.cell}>{item.Company_name || '-'}</td>
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

export default DataTableCFPLabel;
