const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const cors = require('cors');
const path = require('path');


// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const BASE_URL = `http://localhost:${PORT}`;


// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// enable cors:
app.use(cors());

// Serve static files from the Dataset folder
app.use('/Dataset', express.static(path.join(__dirname, '../Dataset')));

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB connected'))
.catch((err) => console.error('MongoDB connection error:', err));

// Routes
app.get('/', (req, res) => {
  res.send('Welcome to the Image Editing App Backend!');
});

const imageRoutes = require('./routes/imageRoutes');
app.use('/api/images', imageRoutes);

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});


