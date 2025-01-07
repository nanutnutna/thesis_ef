// CFO
import React from 'react';

const DataTable = ({ data }) => (
  <div style={{ marginTop: '20px' }}>
    <table border="1" style={{ width: '100%', textAlign: 'left' }}>
      <thead>
        <tr>
          <th>ลำดับ</th>
          <th>ชื่อ</th>
          <th>หน่วย</th>
          <th>Total [kg CO2eq/unit]</th>
          <th>ข้อมูลอ้างอิง</th>
          <th>รายละเอียด</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item, index) => (
          <tr key={index}>
            <td>{item.ลำดับ || 'N/A'}</td>
            <td>{item.ชื่อ || 'N/A'}</td>
            <td>{item.หน่วย || 'N/A'}</td>
            <td>{item['Total [kg CO2eq/unit]'] || 'N/A'}</td>
            <td>{item['ข้อมูลอ้างอิง'] || 'N/A'}</td>
            <td>{item.รายละเอียด || 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default DataTable;






// CFP
// import React from 'react';

// const DataTable = ({ results }) => {
//   return (
//     <table border="1" style={{ width: '100%', marginTop: '20px', textAlign: 'left' }}>
//       <thead>
//         <tr>
//           <th>กลุ่ม</th>
//           <th>ลำดับ</th>
//           <th>ชื่อ</th>
//           <th>รายละเอียด</th>
//           <th>หน่วย</th>
//           <th>ค่าแฟคเตอร์ (kgCO2e)</th>
//           <th>ข้อมูลอ้างอิง</th>
//           <th>วันที่อัพเดท</th>
//         </tr>
//       </thead>
//       <tbody>
//         {results.length > 0 ? (
//           results.map((item, index) => (
//             <tr key={index}>
//               <td>{item.กลุ่ม || 'N/A'}</td>
//               <td>{item.ลำดับ || 'N/A'}</td>
//               <td>{item.ชื่อ || 'N/A'}</td>
//               <td>{item.รายละเอียด || 'N/A'}</td>
//               <td>{item.หน่วย || 'N/A'}</td>
//               <td>{item['ค่าแฟคเตอร์ (kgCO2e)'] || 'N/A'}</td>
//               <td>{item['ข้อมูลอ้างอิง'] || 'N/A'}</td>
//               <td>{item['วันที่อัพเดท'] || 'N/A'}</td>
//             </tr>
//           ))
//         ) : (
//           <tr>
//             <td colSpan="8" style={{ textAlign: 'center' }}>🔍 No results found</td>
//           </tr>
//         )}
//       </tbody>
//     </table>
//   );
// };

// export default DataTable;
