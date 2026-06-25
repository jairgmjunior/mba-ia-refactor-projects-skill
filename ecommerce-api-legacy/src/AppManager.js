const { createApp } = require('./app');

class AppManager {
  async setupRoutes(app) {
    const createdApp = await createApp();
    app._router = createdApp._router;
  }

  initDb() {}
}

module.exports = AppManager;
