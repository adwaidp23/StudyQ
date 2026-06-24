const API = "https://studyq-8l8r.onrender.com";

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
