import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // ตรวจสอบให้แน่ใจว่า URL ถูกต้อง
});

// ตรวจสอบว่ามีการ export ฟังก์ชัน testAPI
export const testAPI = () => {
  return api.get('/');
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
