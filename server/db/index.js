const mongoose = require("mongoose");
require("dotenv/config");

mongoose
  .connect(process.env.MONGO_URL)
  .then(() => console.log("Connected to DB"));
