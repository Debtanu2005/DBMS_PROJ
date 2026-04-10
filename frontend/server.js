const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const app  = express();
const PORT = 3000;

// ── Serve the entire frontend folder as static files ──────────
app.use(express.static(__dirname));

// ── Proxy /api/* → FastAPI at http://127.0.0.1:8000 ──────────
// The ^/api prefix is stripped, so:
//   GET  /api/search_books  →  GET  /search_books
//   POST /api/login         →  POST /login
app.use("/api", createProxyMiddleware({
  target      : "http://127.0.0.1:8000",
  changeOrigin: true,
  pathRewrite : { "^/api": "" },
  on: {
    error: (err, req, res) => {
      console.error("[proxy error]", err.message);
      res.status(502).json({ detail: "Backend unavailable. Is FastAPI running on port 8000?" });
    },
  },
}));

// ── Default route → landing page ─────────────────────────────
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.listen(PORT, () => {
  console.log(`\n  Folio frontend  →  http://localhost:${PORT}`);
  console.log(`  FastAPI backend →  http://127.0.0.1:8000`);
  console.log(`  API proxy       →  /api/* strips prefix and forwards\n`);
});