const API_URL = "https://adwaidp08.pythonanywhere.com";

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

  // Ensure no double slashes when joining the API_URL and the endpoint path
  const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
  const endpoint = path.startsWith('/') ? path : `/${path}`;
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
