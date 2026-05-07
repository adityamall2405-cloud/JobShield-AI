import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const predictJob = async (payload) => {
  const { data } = await axios.post(`${API_BASE}/predict`, payload);
  return data;
};

export const trainModel = async () => {
  const { data } = await axios.post(`${API_BASE}/train`);
  return data;
};
