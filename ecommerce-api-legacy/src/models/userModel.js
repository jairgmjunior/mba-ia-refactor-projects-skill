const { get, run } = require('../config/database');

class UserModel {
  constructor(db) { this.db = db; }
  findByEmail(email) { return get(this.db, 'SELECT id FROM users WHERE email = ?', [email]); }
  create({ name, email, password }) { return run(this.db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, password]); }
  delete(userId) { return run(this.db, 'DELETE FROM users WHERE id = ?', [userId]); }
}

module.exports = UserModel;
