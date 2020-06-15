const functions = require("firebase-functions");
const admin = require("firebase-admin");
const cors = require("cors")({origin: "https://donations.exposed"});

admin.initializeApp();
let db = admin.firestore();

exports.donate = functions.https.onRequest((req, res) => {
  cors(req, res, () => {
    let donationId = req.body.id;
    let donationAmount = req.body.amount;
    let donationRef = db.collection("donations").doc(donationId);
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
