const mongoose = require("mongoose");
const { Schema } = mongoose;
require("dotenv/config");

mongoose
  .connect(process.env.MONGO_URL)
  .then(() => console.log("Connected to DB"));

const documentSchema = new Schema({
  originalName: String,
  mimetype: String,
  uploadDate: { type: Date, Default: Date.now() },
});

const Document = mongoose.model("Document", documentSchema);

module.exports = { Document };
