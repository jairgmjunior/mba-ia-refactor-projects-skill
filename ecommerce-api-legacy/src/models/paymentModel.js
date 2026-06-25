const { run } = require('../config/database');

class PaymentModel {
  constructor(db) { this.db = db; }
  create(enrollmentId, amount, status) { return run(this.db, 'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]); }
}

module.exports = PaymentModel;
