const { all, get } = require('../config/database');

class CourseModel {
  constructor(db) { this.db = db; }
  findActive(courseId) { return get(this.db, 'SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]); }
  financialReportRows() {
    return all(this.db, `
      SELECT c.id, c.title, u.name AS student, p.amount, p.status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u ON u.id = e.user_id
      LEFT JOIN payments p ON p.enrollment_id = e.id
      ORDER BY c.id
    `);
  }
}

module.exports = CourseModel;
