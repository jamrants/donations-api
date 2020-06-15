const functions = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({
  origin: [
    'https://donations.exposed',
    'http://localhost:8000',
    /donations-exposed\.netlify\.app$/,
  ],
});

admin.initializeApp();
let db = admin.firestore();

exports.donate = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    let donationId = req.body.id;
    let donationAmount = req.body.amount;
    let donationRef = db.collection('donations').doc(donationId);
    donationRef
      .get()
      .then((docSnapshot) => {
        if (docSnapshot.exists) {
          donationRef.update({
            amount: admin.firestore.FieldValue.increment(donationAmount),
          });
        } else {
          donationRef.set({
            amount: donationAmount,
          });
        }
        res.status(200).end();
        return;
      })
      .catch((err) => {
        res.status(500).json(err);
      });
  });
});

exports.income = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    const country = req.query.country;
    // implemented countries
    if (!['CA', 'US'].includes(country)) {
      res.status(404).json({ error: 'Country not supported.' });
    } else {
      // FSAs for Canada (first three digits of postal code)
      const postcode = country === 'CA' ? req.query.postcode.substring(0, 3) : res.query.postcode;
      db.collection(`postcode-income-${country.toLowerCase()}`)
        .doc(postcode)
        .get()
        .then((doc) => {
          if (doc.exists) {
            res.status(200).json(doc.data());
          } else {
            res.status(404).json({ error: 'Postcode not found.' });
          }
          return;
        })
        .catch((err) => {
          res.status(500).json(err);
        });
    }
  });
});
