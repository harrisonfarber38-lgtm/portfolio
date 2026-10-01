import { useEffect, useState } from "react";
import { education, experience, projects } from "../../server/src/seed/data.js";

async function request(path, options) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  // Static hosts answer /api/* with the SPA's index.html (or a 404 page), not JSON.
  if (!(res.headers.get("content-type") || "").includes("application/json")) {
    throw Object.assign(new Error("API unavailable"), { offline: true });
  }
  const body = await res.json();
  if (!res.ok) throw Object.assign(new Error(body.error || `Request failed (${res.status})`), { fields: body.fields });
  return body;
}

// Portfolio content comes from the Express/MongoDB API when it is running, and from the
// same data bundled into the build when the site is deployed as static files.
const withFallback = (path, fallback) => () => request(path).catch((err) => {
  if (err.offline || err instanceof TypeError) return fallback;
  throw err;
});

export const getProjects = withFallback("/projects", projects);
export const getProfile = withFallback("/profile", { experience, education });

export const sendMessage = (data) => request("/messages", { method: "POST", body: JSON.stringify(data) }).catch((err) => {
  if (err.offline || err instanceof TypeError) {
    throw new Error("The message form isn't available on this version of the site. Please email harrisonfarber38@gmail.com.");
  }
  throw err;
});

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
