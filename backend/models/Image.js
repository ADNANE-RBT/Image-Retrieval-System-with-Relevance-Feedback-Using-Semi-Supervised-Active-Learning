const mongoose = require('mongoose');

const ImageSchema = new mongoose.Schema({
  filename: { type: String, required: true },
  path: { type: String, required: true },
  size: { type: Number, required: true },
  createdAt: { type: Date, default: Date.now },
  dimensions: {
    width: { type: Number, required: true },
    height: { type: Number, required: true },
  },
  category: { type: String, required: true },
},{ collection: 'Images' }); 

module.exports = mongoose.model('Images', ImageSchema);
