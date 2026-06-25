const AuditLogModel = require('../models/auditLogModel');
const CourseModel = require('../models/courseModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const UserModel = require('../models/userModel');
const { processPayment } = require('../services/paymentService');
const { hashPassword } = require('../utils/security');

class CheckoutController {
  constructor(db) {
    this.auditLogs = new AuditLogModel(db);
    this.courses = new CourseModel(db);
    this.enrollments = new EnrollmentModel(db);
    this.payments = new PaymentModel(db);
    this.users = new UserModel(db);
  }

  async checkout(req, res, next) {
    try {
      const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
      if (!name || !email || !courseId || !cardNumber) return res.status(400).send('Bad Request');
      const course = await this.courses.findActive(courseId);
      if (!course) return res.status(404).send('Curso não encontrado');
      let user = await this.users.findByEmail(email);
      if (!user) {
        const created = await this.users.create({ name, email, password: hashPassword(password || '123456') });
        user = { id: created.lastID };
      }
      const payment = await processPayment(cardNumber, course.price);
      if (payment.status === 'DENIED') return res.status(400).send('Pagamento recusado');
      const enrollment = await this.enrollments.create(user.id, courseId);
      await this.payments.create(enrollment.lastID, payment.amount, payment.status);
      await this.auditLogs.create(`Checkout curso ${courseId} por ${user.id}`);
      return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollment.lastID });
    } catch (error) {
      return next(error);
    }
  }
}

module.exports = CheckoutController;
