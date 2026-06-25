const UserModel = require('../models/userModel');

class UserController {
  constructor(db) { this.users = new UserModel(db); }

  async deleteUser(req, res, next) {
    try {
      await this.users.delete(req.params.id);
      return res.send('Usuário deletado. Operação executada pelo controller de usuários.');
    } catch (error) {
      return next(error);
    }
  }
}

module.exports = UserController;
