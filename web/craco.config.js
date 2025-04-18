module.exports = {
    webpack: {
        configure: {
            module: {
                rules: [
                    {
                        test: /\.geojson$/,
                        type: 'json'
                    }
                ]
            }
        }
    }
};