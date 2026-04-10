const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const app = express();
const PORT = 3000;

// Serve frontend
app.use(express.static(__dirname));

// 🔥 PROXY API REQUESTS TO FASTAPI
app.use("/api", createProxyMiddleware({
    target: "http://127.0.0.1:8000",
    changeOrigin: true,
    pathRewrite: {
        "^/api": ""   // remove /api prefix
    }
}));

// Default route
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "search.html"));
});

app.listen(PORT, () => {
    console.log(`Frontend running at http://localhost:${PORT}`);
});