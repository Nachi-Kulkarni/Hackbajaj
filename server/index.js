const express = require("express");
const cors = require("cors");
const multer = require("multer");
const upload = multer({ dest: "lib/documents/" });
const fs = require("fs");
const path = require("path");

const app = express();

// Track uploaded files (in-memory for demo; use a DB in production)
const documents = [];

app.use(express.json());
app.use(cors());

// Upload route
app.post("/upload", upload.single("document"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  // Add metadata to our list
  documents.push({
    id: req.file.filename, // Use the generated filename as ID
    originalName: req.file.originalname,
    mimetype: req.file.mimetype,
    size: req.file.size,
    uploadDate: new Date().toISOString(),
  });

  res.status(201).json({
    message: "File uploaded successfully!",
    fileId: req.file.filename,
  });
});

// List all documents (for example: http://localhost:3000/documents)
app.get("/documents", (req, res) => {
  res.json(documents);
});

// Download a specific document by ID (for example: http://localhost:3000/documents/<fileId>)
app.get("/documents/:id", (req, res) => {
  const fileId = req.params.id;
  const doc = documents.find((d) => d.id === fileId);

  if (!doc) {
    return res.status(404).send("File not found.");
  }

  const filePath = path.join("lib/documents/", fileId);

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File no longer exists.");
  }

  res.download(filePath, doc.originalName);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
