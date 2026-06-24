const API_URL = "https://your-backend.onrender.com"; // we'll fill this after Step 3

export default API_URL;

// NOTE: apiFetch removed; will be reintroduced in later steps if needed.

/* eslint-disable */
export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("studyq_token");
  
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Remove trailing slash from API_URL if present, and ensure path starts with a slash
  const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
  const endpoint = path.startsWith('/') ? path : `/${path}`;

  // Use base endpoint /api since all our flask routes are /api/*
  // Wait, the routes in main.py are like /api/questions.
  // The frontend Ask.jsx calls apiFetch('/questions').
  // Therefore the actual URL should be baseUrl + '/api' + endpoint
  
  const finalUrl = `${baseUrl}/api${endpoint}`;

  const res = await fetch(finalUrl, {
    ...options,
    headers,
  });

  const json = await res.json();
  
  if (!res.ok) {
    throw new Error(json.error || "Something went wrong");
  }
  
  return json;
}
