const { config } = require('./config/settings');
const { hashPassword } = require('./utils/security');

function logAndCache(key, data) {
  console.log(`[LOG] ${key}: ${data}`);
}

module.exports = { config, logAndCache, hashPassword };
