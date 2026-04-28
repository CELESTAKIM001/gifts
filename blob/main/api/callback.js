module.exports = (req, res) => {
  console.log('Callback received:', JSON.stringify(req.body, null, 2));
  res.status(200).json({ ResultCode: 0, ResultDesc: 'Success' });
};
