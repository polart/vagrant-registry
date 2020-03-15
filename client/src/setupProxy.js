const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        [
            '/admin',
            '/api',
            '/box-metadata',
            '/downloads',
        ],
        createProxyMiddleware({
            target: 'http://api:8000',
            changeOrigin: false,
        }),
    );
    app.get('*', (req, res, next) => {
        if (req.get('User-Agent').includes('Vagrant')) {
            res.redirect(301, `http://localhost:8000/box-metadata${req.path}`);
            return;
        }
        next();
    });
};
