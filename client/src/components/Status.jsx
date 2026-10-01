/** Loading / error line for API-backed sections. */
export default function Status({ loading, error, what }) {
  if (loading) return <p className="state" role="status"><span className="dot" />Loading {what}…</p>;
  if (error) return <p className="state state--error" role="alert">Couldn't load {what}. Is the API running? ({error.message})</p>;
  return null;
}
