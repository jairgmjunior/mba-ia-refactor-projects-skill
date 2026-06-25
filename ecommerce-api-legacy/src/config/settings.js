const config = {
  port: Number(process.env.PORT || 3000),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-payment-key',
};

module.exports = { config };
