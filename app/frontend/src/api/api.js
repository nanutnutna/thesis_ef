import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // ตรวจสอบให้แน่ใจว่า URL ถูกต้อง
});

// ตรวจสอบว่ามีการ export ฟังก์ชัน testAPI
export const testAPI = () => {
  return api.get('/');
};

//get create date
export const createDate = () => {
  return api.get('/creation-date');
};

//get all index
export const listDropdownOptions = () => {
  return api.get('/available-dates');
};

// upload files
export const uploadData = (formData) => {
  return api.post('/upload-data-with-image/', formData);
};

// CFP
export const searchDataCFP = (query) => {
  return api.get(`/search-data_cfp/?q=${query}`);
};
export const fetchAutocompleteCFP = async (query) => {
  return await api.get(`/autocomplete_cfp/?q=${query}`);
};

// CFO
export const searchDataCFO = (query) => {
  return api.get(`/search-data_cfo/?q=${query}`);
};
export const fetchAutocompleteCFO = async (query) => {
  return await api.get(`/autocomplete_cfo/?q=${query}`);
};


// CLP
export const searchDataCLP = (query) => {
  return api.get(`/search-data_clp/?q=${query}`);
};
export const fetchAutocompleteCLP = async (query) => {
  return await api.get(`/autocomplete_clp/?q=${query}`);
};



// CFO+CFP
export const searchDataCombine = async (query, date) => {
  const params = new URLSearchParams();
  if (query) params.append('q', query); // เพิ่ม query หากมี
  if (date) params.append('date', date); // เพิ่ม date หากมี

  try {
    const response = await api.get(`/search-data_combine/?${params.toString()}`);
    return response.data; // ส่งคืนข้อมูล
  } catch (error) {
    console.error('Error fetching search data:', error);
    throw error; // ส่งข้อผิดพลาดให้จัดการในส่วนที่เรียกใช้
  }
};

// ฟังก์ชัน autocomplete สำหรับ CFO + CFP
export const fetchAutocompleteCombine = async (query, date) => {
  const params = new URLSearchParams();
  if (query) params.append('q', query); // เพิ่ม query หากมี
  if (date) params.append('date', date); // เพิ่ม date หากมี

  try {
    const response = await api.get(`/autocomplete_combine/?${params.toString()}`);
    return response.data; // ส่งคืนข้อมูล autocomplete
  } catch (error) {
    console.error('Error fetching autocomplete data:', error);
    throw error; // ส่งข้อผิดพลาดให้จัดการในส่วนที่เรียกใช้
  }
};