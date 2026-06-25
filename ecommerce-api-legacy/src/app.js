const express = require('express');
const { config } = require('./config/settings');
const { createDatabase } = require('./config/database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middleware/errorHandler');

async function createApp() {
  const app = express();
  const db = await createDatabase();
  app.use(express.json());
  app.use('/api', checkoutRoutes(db));
  app.use('/api', reportRoutes(db));
  app.use('/api', userRoutes(db));
  app.use(errorHandler);
  return app;
}

if (require.main === module) {
  createApp().then((app) => {
    app.listen(config.port, () => console.log(`Frankenstein LMS rodando na porta ${config.port}...`));
  }).catch((error) => {
    console.error(error);
    process.exit(1);
  });
}

module.exports = { createApp };
