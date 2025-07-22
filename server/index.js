const express = require("express");
const cors = require("cors");
const multer = require("multer");
const upload = multer();

const { Document } = require("./db");

const app = express();

app.use(express.json());
app.use(cors());

// Upload route
app.post("/upload", upload.single("document"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  try {
    const file = await Document.create({
      originalName: req.file.originalname,
      mimetype: req.file.mimetype,
      size: req.file.size,
    });

    res.status(201).json({
      message: "File uploaded successfully!",
      fileId: file._id,
    });
  } catch {
    res.status(500).json({
      message: "Could not upload file",
    });
  }
});
// Download a specific document by ID (for example: http://localhost:3000/documents/<fileId>)
app.get("/documents/:id", async (req, res) => {
  const fileId = req.params.id;
  try {
    const document = await Document.findOne({ _id: fileId });
    if (!document) {
      return res.status(404).json({
        message: "File not found",
      });
    }
    return res.json({ document });
  } catch {
    return res.status(500).json({
      message: "Could not fetch document",
    });
  }
});

// List all documents (for example: http://localhost:3000/documents)
app.get("/documents", async (req, res) => {
  const documents = await Document.find({});
  if (!documents.length)
    return res.status(404).json({
      message: "No file uploaded",
    });
  return res.json({ documents });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
