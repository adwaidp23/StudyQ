const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000/api";

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("studyq_token");
  
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  const json = await res.json();
  
  if (!res.ok) {
    throw new Error(json.error || "Something went wrong");
  }
  
  return json;
}
