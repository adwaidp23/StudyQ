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

  const res = await fetch(`${API}${path}`, {
    ...options,
    headers,
  });

  const json = await res.json();
  
  if (!res.ok) {
    throw new Error(json.error || "Something went wrong");
  }
  
  return json;
}
