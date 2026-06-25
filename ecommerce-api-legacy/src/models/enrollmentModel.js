const { run } = require('../config/database');

class EnrollmentModel {
  constructor(db) { this.db = db; }
  create(userId, courseId) { return run(this.db, 'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]); }
}

module.exports = EnrollmentModel;
