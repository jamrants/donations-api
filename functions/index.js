const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");

admin.initializeApp();
let db = admin.firestore();

const app = express();

// setup cors
// TODO: only allow from correct origin
app.use(cors({ origin: true }));

// parse json
app.use(express.json());

app.post("/donate/:id", (req, res) => {
  let donationId = req.params.id;
  let donationAmount = req.body.amount;

  let donationRef = db.collection("donations").doc(donationId);
  let increment = donationRef.update({
    amount: admin.firestore.FieldValue.increment(donationAmount),
  });
});

// Expose Express API as a single Cloud Function:
exports.widgets = functions.https.onRequest(app);
