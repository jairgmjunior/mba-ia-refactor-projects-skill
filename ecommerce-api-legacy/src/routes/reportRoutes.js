const express = require('express');
const ReportController = require('../controllers/reportController');

function reportRoutes(db) {
  const router = express.Router();
  const controller = new ReportController(db);
  router.get('/admin/financial-report', controller.financialReport.bind(controller));
  return router;
}

module.exports = reportRoutes;
