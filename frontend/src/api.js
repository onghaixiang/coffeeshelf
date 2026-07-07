// Thin fetch wrappers around the FastAPI backend (proxied at /api in dev).

async function handle(res) {
  if (res.status === 204) return null;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = body?.detail || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

export function listBeans(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") qs.append(k, v);
  });
  const q = qs.toString();
  return fetch(`/api/beans${q ? `?${q}` : ""}`).then(handle);
}

export function createBean(data) {
  return fetch("/api/beans", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(handle);
}

export function updateBean(id, data) {
  return fetch(`/api/beans/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(handle);
}

export function deleteBean(id) {
  return fetch(`/api/beans/${id}`, { method: "DELETE" }).then(handle);
}

export function getSuggestions(request, useInventory) {
  return fetch("/api/suggestions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request, use_inventory: useInventory }),
  }).then(handle);
}
