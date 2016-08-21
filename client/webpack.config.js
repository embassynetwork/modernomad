var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config.js')

// Use webpack dev server
config.entry = [
  'webpack-dev-server/client?http://localhost:3000',
  'webpack/hot/only-dev-server',
  './js/index'
]

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:3000/build/'


// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(),
  new BundleTracker({filename: './webpack-stats.json'}),
])

module.exports = config
