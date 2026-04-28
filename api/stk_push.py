const https = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { phone, amount } = req.body;
  if (!phone || !amount) return res.status(400).json({ error: 'Phone and amount required' });

  const CONSUMER_KEY = process.env.CONSUMER_KEY;
  const CONSUMER_SECRET = process.env.CONSUMER_SECRET;
  const SHORTCODE = process.env.SHORTCODE;
  const PASSKEY = process.env.PASSKEY;
  const CALLBACK_URL = process.env.CALLBACK_URL;

  try {
    // Get access token
    const credentials = Buffer.from(`${CONSUMER_KEY}:${CONSUMER_SECRET}`).toString('base64');
    const tokenRes = await fetch('https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', {
      headers: { 'Authorization': `Basic ${credentials}` }
    });
    const tokenData = await tokenRes.json();
    const token = tokenData.access_token;

    // Generate password
    const timestamp = new Date().toISOString().replace(/[^0-9]/g, '').slice(0, 14);
    const password = Buffer.from(`${SHORTCODE}${PASSKEY}${timestamp}`).toString('base64');

    // STK Push
    const stkRes = await fetch('https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        BusinessShortCode: SHORTCODE,
        Password: password,
        Timestamp: timestamp,
        TransactionType: 'CustomerPayBillOnline',
        Amount: amount,
        PartyA: phone,
        PartyB: SHORTCODE,
        PhoneNumber: phone,
        CallBackURL: CALLBACK_URL,
        AccountReference: 'GeopramGifts',
        TransactionDesc: 'Donation to Geopram Technologies Gifts'
      })
    });

    const stkData = await stkRes.json();
    return res.status(200).json(stkData);

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
