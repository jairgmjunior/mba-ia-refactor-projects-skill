const express = require('express');
const UserController = require('../controllers/userController');

function userRoutes(db) {
  const router = express.Router();
  const controller = new UserController(db);
  router.delete('/users/:id', controller.deleteUser.bind(controller));
  return router;
}

module.exports = userRoutes;
