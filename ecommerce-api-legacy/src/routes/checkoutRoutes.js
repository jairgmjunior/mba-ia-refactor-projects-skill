const express = require('express');
const CheckoutController = require('../controllers/checkoutController');

function checkoutRoutes(db) {
  const router = express.Router();
  const controller = new CheckoutController(db);
  router.post('/checkout', controller.checkout.bind(controller));
  return router;
}

module.exports = checkoutRoutes;
