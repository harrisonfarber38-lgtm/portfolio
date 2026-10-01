import { useEffect, useState } from "react";

async function request(path, options) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(body.error || `Request failed (${res.status})`), { fields: body.fields });
  return body;
}

export const getProjects = () => request("/projects");
export const getProfile = () => request("/profile");
export const sendMessage = (data) => request("/messages", { method: "POST", body: JSON.stringify(data) });

/** Loads data once; returns { data, error, loading }. */
export function useApi(fetcher) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  useEffect(() => {
    let alive = true;
    fetcher()
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }));
    return () => { alive = false; };
  }, [fetcher]);
  return state;
}
