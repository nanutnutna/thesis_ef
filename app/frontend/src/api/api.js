import axios from 'axios';

// const api = axios.create({
//   baseURL: 'http://127.0.0.1:8000', // ตรวจสอบให้แน่ใจว่า URL ถูกต้อง
// });

const api = axios.create({
  baseURL: 'https://my-first-project-production-67dc.up.railway.app', // ตรวจสอบให้แน่ใจว่า URL ถูกต้อง
});


// const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://my-first-project-production-67dc.up.railway.app';

// const api = axios.create({
//   baseURL: VITE_API_URL,
// });

// console.log('API URL:', VITE_API_URL);

// ตรวจสอบว่ามีการ export ฟังก์ชัน testAPI
export const testAPI = () => {
  return api.get('/');
};

//get create date
export const createDate = () => {
  return api.get('/creation-date');
};

//get all index
export const listIndex = () => {
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
export const searchDataCombine = (query) => {
  return api.get(`/search-data_combine/?q=${query}`);
};
export const fetchAutocompleteCombine = async (query) => {
  return await api.get(`/autocomplete_combine/?q=${query}`);
};

// em
export const searchDataEmbedding = (query) => {
  return api.get(`/search-embedding/?q=${query}`);
};