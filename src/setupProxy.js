const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      target: "https://super-voices-cloud.herokuapp.com/",
      changeOrigin: true,
    })
  );
};