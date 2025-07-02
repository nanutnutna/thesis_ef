import React from 'react';

const DataTableCombine = ({ data, onMouseEnter, onMouseLeave }) => {
  // ฟังก์ชันสำหรับจัดการการแสดงค่า
  const formatValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return '-';
    }
    return value.toString();
  };

  // ฟังก์ชันสำหรับดึงข้อมูลจากหลาย field ที่เป็นไปได้
  const getFieldValue = (item, possibleFields) => {
    for (const field of possibleFields) {
      if (item[field] !== undefined && item[field] !== null && item[field] !== '') {
        return item[field];
      }
    }
    return '-';
  };

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
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} style={styles.row}>
              {/* Category Column */}
              <td style={styles.cell}>
                {formatValue(getFieldValue(item, ['Category', 'category', 'หมวดหมู่', 'กลุ่ม']))}
              </td>

              {/* Name Column - เพิ่ม tooltip events */}
              <td 
                style={{
                  ...styles.cell,
                  cursor: 'help',
                  transition: 'background-color 0.2s ease-in-out',
                }}
                onMouseEnter={(e) => {
                  // 🆕 แก้ไข: ใช้ currentTarget แทน target
                  e.currentTarget.style.backgroundColor = '#fef3c7';
                  if (onMouseEnter) {
                    onMouseEnter(e, item);
                  }
                }}
                onMouseLeave={(e) => {
                  // 🆕 แก้ไข: ใช้ currentTarget แทน target
                  e.currentTarget.style.backgroundColor = 'transparent';
                  if (onMouseLeave) {
                    onMouseLeave();
                  }
                }}
                title="Hover to see more details"
              >
                <div style={{ maxWidth: '200px' }}>
                  <div style={{ fontWeight: 'bold', color: '#111827' }}>
                    {formatValue(getFieldValue(item, ['Name', 'name', 'ชื่อ', 'activity', 'Activity']))}
                  </div>
                  {item.description && (
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#6b7280', 
                      marginTop: '4px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {item.description}
                    </div>
                  )}
                </div>
              </td>

              {/* Unit Column */}
              <td style={styles.cell}>
                {formatValue(getFieldValue(item, ['Unit', 'unit', 'หน่วย']))}
              </td>

              {/* Factor Column */}
              <td style={styles.cell}>
                <div>
                  <span style={{ fontWeight: 'bold' }}>
                    {formatValue(getFieldValue(item, ['Factor', 'factor', 'emission_factor', 'emissionFactor', 'ค่า']))}
                  </span>
                  {item.uncertainty && (
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                      ±{item.uncertainty}
                    </div>
                  )}
                </div>
              </td>

              {/* Reference Column - 🆕 ลบ tooltip events ออก */}
              <td style={styles.cell}>
                <div style={{ maxWidth: '250px' }}>
                  {(() => {
                    const reference = getFieldValue(item, ['Reference', 'reference', 'แหล่งอ้างอิง', 'source', 'Source']);
                    // แสดงข้อความเต็มหรือตัดสั้น (ไม่มี tooltip)
                    if (reference !== '-' && reference.length > 50) {
                      return (
                        <div>
                          {reference.substring(0, 50)}...
                        </div>
                      );
                    }
                    return reference;
                  })()}
                </div>
              </td>

              {/* Last Updated Column */}
              <td style={styles.cell}>
                {formatValue(getFieldValue(item, ['Last_Updated', 'lastUpdated', 'last_updated', 'updated_date', 'date', 'วันที่อัปเดต']))}
              </td>

              {/* Score Column - เพิ่มการแสดงผลแบบ badge */}
              <td style={styles.cell}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {(() => {
                    const score = getFieldValue(item, ['score', 'Score', 'quality', 'Quality', 'คะแนน']);
                    if (score === '-') return score;
                    
                    const numScore = parseFloat(score);
                    // 🆕 แก้ไข: เช็คว่า numScore เป็น valid number
                    if (isNaN(numScore)) return score;
                    
                    let badgeStyle = {
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '4px 8px',
                      fontSize: '12px',
                      fontWeight: '600',
                      borderRadius: '9999px',
                      color: '#6b7280',
                      backgroundColor: '#f3f4f6'
                    };
                    
                    if (numScore >= 4) {
                      badgeStyle = {
                        ...badgeStyle,
                        color: '#065f46',
                        backgroundColor: '#d1fae5'
                      };
                    } else if (numScore >= 3) {
                      badgeStyle = {
                        ...badgeStyle,
                        color: '#92400e',
                        backgroundColor: '#fef3c7'
                      };
                    } else if (numScore >= 2) {
                      badgeStyle = {
                        ...badgeStyle,
                        color: '#c2410c',
                        backgroundColor: '#fed7aa'
                      };
                    } else if (numScore >= 1) {
                      badgeStyle = {
                        ...badgeStyle,
                        color: '#991b1b',
                        backgroundColor: '#fecaca'
                      };
                    }
                    
                    return (
                      <span style={badgeStyle}>
                        {score}
                      </span>
                    );
                  })()}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* แสดงข้อความเมื่อไม่มีข้อมูล */}
      {data.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '32px',
          color: '#6b7280'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
          <div>No data to display</div>
        </div>
      )}
    </div>
  );
};

const styles = {
  tableContainer: {
    overflowX: 'auto',
    marginTop: '20px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    maxWidth: '100%',
    backgroundColor: 'white'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  header: {
    backgroundColor: '#f0fdfa', // teal-50
    fontWeight: '600',
    textAlign: 'left',
    padding: '12px 24px',
    borderBottom: '1px solid #e5e7eb',
    whiteSpace: 'nowrap',
    fontSize: '14px',
    color: '#0f766e', // teal-700
    textTransform: 'none',
    letterSpacing: '0.05em'
  },
  row: {
    borderBottom: '1px solid #f3f4f6',
  },
  cell: {
    padding: '16px 24px',
    textAlign: 'left',
    wordWrap: 'break-word',
    maxWidth: '200px',
    fontSize: '14px',
    color: '#111827',
    borderBottom: '1px solid #f3f4f6',
    verticalAlign: 'top'
  }
};

export default DataTableCombine;