const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const Image = require('../models/Image');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// Multer storage configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      // Temporarily store all uploads in a generic uploads folder
      const uploadFolder = path.join(__dirname, '..', 'uploads');
      fs.mkdir(uploadFolder, { recursive: true }, (err) => {
        if (err) {
          return cb(err);
        }
        cb(null, uploadFolder);
      });
    },
    filename: (req, file, cb) => {
      cb(null, `${Date.now()}-${file.originalname}`);
    },
  });
  
  const upload = multer({ storage });
  
  

// Upload an image
router.post('/upload', upload.single('image'), async (req, res) => {
    try {
      const { filename, path: tempFilePath, size } = req.file;
      const { category } = req.body; // Expect category in the request body.
  
      if (!category) {
        return res.status(400).json({ message: 'Category is required.' });
      }
  
      // Create the category folder in the dataset directory
      const categoryFolder = path.join(__dirname, '..', '/../Dataset/RSSCN7-master', category);
      if (!fs.existsSync(categoryFolder)) {
        fs.mkdirSync(categoryFolder, { recursive: true });
      }
  
      // Move the file to the category folder
      const finalFilePath = path.join(categoryFolder, filename);
      fs.renameSync(tempFilePath, finalFilePath);
  
      // Extract image dimensions using sharp
      const imageDimensions = await sharp(finalFilePath)
        .metadata()
        .then((metadata) => ({
          width: metadata.width,
          height: metadata.height,
        }));
  
      const dimensions = {
        width: imageDimensions.width || 0,
        height: imageDimensions.height || 0,
      };
  
      // Create new image document
      const image = new Image({
        filename,
        path: finalFilePath,
        size,
        category,
        dimensions,
      });
      await image.save();
  
      res.status(201).json({ message: 'Image uploaded successfully', image });
    } catch (error) {
      res.status(500).json({ message: 'Error uploading image', error });
    }
  });
  

// Fetch all images
router.get('/', async (req, res) => {
  try {
    const images = await Image.find();
    res.json(images);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching images', error });
  }
});

module.exports = router;
