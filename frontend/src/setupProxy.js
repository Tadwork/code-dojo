/* eslint-env node */

const { createProxyMiddleware } = require("http-proxy-middleware");

const proxyTarget = process.env.REACT_APP_PROXY_TARGET || "http://localhost:8000";

module.exports = function setupProxy(app) {
  app.use(
    ["/api", "/ws"],
    createProxyMiddleware({
      target: proxyTarget,
      changeOrigin: true,
      ws: true,
    }),
  );
};
