var path = require("path");
var webpack = require('webpack');

module.exports = {
  context: __dirname,
  entry: './js/index',

  output: {
    path: path.resolve('./build/'),
    filename: "[name]-[hash].js"
  },

  plugins: [],

  module: {
    loaders: [],
  },

  resolve: {
    modulesDirectories: ['node_modules'],
    extensions: ['', '.js', '.jsx']
  }
}
