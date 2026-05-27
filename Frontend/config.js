/** API base URL: same origin in Docker/Railway, separate port for legacy local dev. */
const API_BASE =
  window.location.port === "5500" ? "http://localhost:8000" : "";
