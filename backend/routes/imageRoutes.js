const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const Image = require('../models/Image');
const router = express.Router();
const fs = require('fs').promises;
const path = require('path');

const BASE_URL = `http://localhost:5000`;


// Multer storage configuration
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const uploadFolder = path.join(__dirname, '..', 'uploads');
        await fs.mkdir(uploadFolder, { recursive: true });
        cb(null, uploadFolder);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    },
});

const upload = multer({ storage });

// Upload an image
router.post('/upload', upload.single('image'), async (req, res) => {
    try {
        console.log('API called: /upload');

        const { filename, path: tempFilePath, size } = req.file;
        const { category } = req.body;

        if (!category) {
            console.log('Error: Category is missing');
            return res.status(400).json({ message: 'Category is required.' });
        }

        console.log(`File received: ${filename}, Temp path: ${tempFilePath}, Size: ${size}`);

        const categoryFolder = path.join(__dirname, '..', '/../Dataset/RSSCN7-master', category);
        await fs.mkdir(categoryFolder, { recursive: true });
        console.log(`Category folder created or already exists: ${categoryFolder}`);

        const finalFilePath = path.join(categoryFolder, filename);
        await fs.rename(tempFilePath, finalFilePath);
        console.log(`File moved to final path: ${finalFilePath}`);

        const imageDimensions = await sharp(finalFilePath)
            .metadata()
            .then((metadata) => ({
                width: metadata.width,
                height: metadata.height,
            }));

        console.log(`Image dimensions: ${imageDimensions.width}x${imageDimensions.height}`);

        const dimensions = {
            width: imageDimensions.width || 0,
            height: imageDimensions.height || 0,
        };

        const relativeFilePath = path.join('Dataset', 'RSSCN7-master', category, filename);

        const image = new Image({
            filename,
            path: relativeFilePath,  
            size,
            category,
            dimensions,
        });
        await image.save();
        console.log('Image document saved successfully.');

        res.status(201).json({
            // message: 'Image uploaded successfully',
            // image: {
              _id: image._id,
              filename: image.filename,
              path: image.path,
              size: image.size,
              category: image.category,
              dimensions: image.dimensions,
              createdAt: image.createdAt,
              updatedAt: image.updatedAt,
            // },
          });
    } catch (error) {
        console.log('Error during image upload:', error.message);
        res.status(500).json({ message: 'Error uploading image', error: error.message });
    }
});



// Fetch all images
router.get('/', async (req, res) => {
    try {
        const images = await Image.find();
        const updatedImages = images.map(image => ({
            ...image.toObject(),
            path: `${BASE_URL}/${image.path.replace(/\\/g, '/')}`,
        }));
        res.json(updatedImages);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching images', error: error.message });
    }
});

// Get images by category
router.get('/category', async (req, res) => {
    try {
        const { categories } = req.query;

        const categoryArray = typeof categories === 'string' 
            ? categories.split(',').map(cat => cat.trim()) 
            : categories;

        const images = categoryArray 
            ? await Image.find({ category: { $in: categoryArray } })
            : await Image.find();

        const updatedImages = images.map(image => ({
            ...image.toObject(),
            path: `${BASE_URL}/${image.path.replace(/\\/g, '/')}`,
        }));

        res.json(updatedImages);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching images by category', error: error.message });
    }
});

// Get a single image by ID
router.get('/:id', async (req, res) => {
    try {
        console.log('GET /:id called with id:', req.params.id); 
        
        const image = await Image.findById(req.params.id);
        console.log('Image found in database:', image); 

        if (!image) {
            console.log('Image not found for id:', req.params.id); 
            return res.status(404).json({ message: 'Image not found' });
        }

        const updatedImage = {
            ...image.toObject(),
            path: `${BASE_URL}/${image.path.replace(/\\/g, '/')}`,
        };

        console.log('Updated image object to return:', updatedImage); 
        res.json(updatedImage);
    } catch (error) {
        console.error('Error fetching image:', error); 
        res.status(500).json({ message: 'Error fetching image', error: error.message });
    }
});


// Delete an image
router.delete('/:id', async (req, res) => {
    try {
        const image = await Image.findByIdAndDelete(req.params.id);
        
        if (!image) {
            return res.status(404).json({ message: 'Image not found' });
        }
        
        // Delete the physical file
        try {
            await fs.unlink(image.path);
        } catch (fileError) {
            console.warn(`Could not delete file: ${image.path}`, fileError);
        }
        
        res.json({ message: 'Image deleted successfully', image });
    } catch (error) {
        res.status(500).json({ message: 'Error deleting image', error: error.message });
    }
});

// Update image metadata
router.patch('/:id', async (req, res) => {
    try {
        const { category, filename } = req.body;
        
        // Validate input
        if (!category && !filename) {
            return res.status(400).json({ message: 'At least one field to update is required' });
        }

        const updateFields = {};
        if (category) updateFields.category = category;
        if (filename) updateFields.filename = filename;

        const image = await Image.findByIdAndUpdate(
            req.params.id, 
            updateFields, 
            { new: true, runValidators: true }
        );
        
        if (!image) {
            return res.status(404).json({ message: 'Image not found' });
        }
        
        res.json({ message: 'Image updated successfully', image });
    } catch (error) {
        res.status(500).json({ message: 'Error updating image', error: error.message });
    }
});


router.get('/search', async (req, res) => {
    try {
        const { query } = req.query;
        
        if (!query) {
            return res.status(400).json({ message: 'Search query is required' });
        }
        
        const images = await Image.find({ 
            filename: { $regex: query, $options: 'i' } 
        });
        
        res.json(images);
    } catch (error) {
        res.status(500).json({ message: 'Error searching images', error: error.message });
    }
});

// Get image count by category
router.get('/count/by-category', async (req, res) => {
    try {
        const categoryCounts = await Image.aggregate([
            { $group: { 
                _id: '$category', 
                count: { $sum: 1 } 
            }}
        ]);
        
        res.json(categoryCounts);
    } catch (error) {
        res.status(500).json({ message: 'Error counting images by category', error: error.message });
    }
});

module.exports = router;