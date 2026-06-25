const CourseModel = require('../models/courseModel');

class ReportController {
  constructor(db) { this.courses = new CourseModel(db); }

  async financialReport(req, res, next) {
    try {
      const rows = await this.courses.financialReportRows();
      const reportByCourse = new Map();
      rows.forEach((row) => {
        if (!reportByCourse.has(row.id)) reportByCourse.set(row.id, { course: row.title, revenue: 0, students: [] });
        const course = reportByCourse.get(row.id);
        if (row.student) course.students.push({ student: row.student, paid: row.amount || 0 });
        if (row.status === 'PAID') course.revenue += row.amount || 0;
      });
      return res.json(Array.from(reportByCourse.values()));
    } catch (error) {
      return next(error);
    }
  }
}

module.exports = ReportController;
