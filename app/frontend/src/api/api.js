import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // ตรวจสอบให้แน่ใจว่า URL ถูกต้อง
});

// ตรวจสอบว่ามีการ export ฟังก์ชัน testAPI
export const testAPI = () => {
  return api.get('/');
};

// ฟังก์ชันอื่นๆ
export const searchData = (query) => {
  return api.get(`/search-data/?q=${query}`);
};

export const uploadData = (formData) => {
  return api.post('/upload-data-with-image/', formData);
};


export const fetchAutocomplete = async (query) => {
  return await api.get(`/autocomplete/?q=${query}`);
};