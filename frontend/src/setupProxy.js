/* eslint-env node */

const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function setupProxy(app) {
  app.use(
    ['/api', '/ws'],
    createProxyMiddleware({
      target: 'http://backend:8000',
      changeOrigin: true,
      ws: true,
    })
  );
};
