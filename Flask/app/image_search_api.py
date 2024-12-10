import os
import json
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Import descriptor calculation function
from Descriptors_calcul import calculate_descriptors

# Import search implementations
from Simple_search_debug import ImageSimilaritySearch
from contineous_SS_RF import SemiSupervisedImageSearch

# Create Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
DATASET_PATH = '../../Dataset/RSSCN7-master'

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize search systems
simple_search = ImageSimilaritySearch(DATASET_PATH)
semi_supervised_search = SemiSupervisedImageSearch(DATASET_PATH)

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_numpy_to_list(descriptors):
    """
    Convert numpy arrays to lists for JSON serialization.
    """
    converted_descriptors = {}
    for category, features in descriptors.items():
        converted_descriptors[category] = {}
        for feature_name, feature_value in features.items():
            # Convert numpy arrays to lists, leave other types as is
            converted_descriptors[category][feature_name] = feature_value.tolist() if hasattr(feature_value, 'tolist') else feature_value
    return converted_descriptors

# Descriptor Calculation Endpoints
@app.route('/calculate_descriptors', methods=['POST']) # tested
def calculate_image_descriptors():
    """
    Endpoint for calculating image descriptors.
    Supports single image upload and optional descriptor type filtering.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Get optional descriptor type filter
            descriptor_types = request.form.get('descriptor_types', 'all')
            
            # Calculate descriptors
            full_descriptors = calculate_descriptors(filepath)
            
            # Remove temporary file
            os.remove(filepath)
            
            # Filter descriptors if requested
            if descriptor_types != 'all':
                requested_types = descriptor_types.split(',')
                filtered_descriptors = {
                    dtype: full_descriptors.get(dtype, {}) 
                    for dtype in requested_types 
                    if dtype in full_descriptors
                }
                converted_descriptors = convert_numpy_to_list(filtered_descriptors)
            else:
                converted_descriptors = convert_numpy_to_list(full_descriptors)
            
            return jsonify({
                "descriptors": converted_descriptors,
                "image_filename": filename
            })
        
        except Exception as e:
            # Ensure file is removed even if an error occurs
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/descriptor_info', methods=['GET'])
def get_descriptor_info():
    """
    Provide information about available descriptor types and their sub-features.
    """
    descriptor_info = {
        "color": {
            "histogram": "Color distribution across RGB channels",
            "dominant_colors": "K-means clustered color centers and their percentages"
        },
        "texture": {
            "gabor_filters": "Texture responses using Gabor filters",
            "glcm_features": "Gray Level Co-occurrence Matrix texture features"
        },
        "shape": {
            "hu_moments": "Invariant shape moments",
            "shape_descriptors": "Aspect ratio, extent, and contour area"
        }
    }
    
    return jsonify(descriptor_info)

@app.route('/bulk_descriptors', methods=['POST'])
def calculate_bulk_descriptors():
    """
    Endpoint for calculating descriptors for multiple images.
    Expects a list of image files.
    """
    if 'images' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    uploaded_files = request.files.getlist('images')
    
    if len(uploaded_files) == 0:
        return jsonify({"error": "No files selected"}), 400
    
    bulk_descriptors = {}
    try:
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    descriptors = calculate_descriptors(filepath)
                    bulk_descriptors[filename] = convert_numpy_to_list(descriptors)
                except Exception as e:
                    bulk_descriptors[filename] = {"error": str(e)}
                
                # Remove temporary file
                os.remove(filepath)
        
        return jsonify({"bulk_descriptors": bulk_descriptors})
    
    except Exception as e:
        # Cleanup any remaining files
        for file in uploaded_files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({"error": str(e)}), 500

# Image Search Endpoints
@app.route('/simple_search', methods=['POST']) #tested should be modify to edit the k_top
def simple_image_search():
    """
    Endpoint for simple image similarity search.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Allow customizable top_k parameter
            top_k = int(request.form.get('top_k', 5))
            similar_images = simple_search.find_similar_images(filepath, top_k=top_k)
            os.remove(filepath)
            return jsonify({
                "search_type": "simple_similarity",
                "similar_images": similar_images
            })
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/semi_supervised_search', methods=['POST']) #tested 
def semi_supervised_image_search():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse feedback from the request
        feedback = request.form.get('feedback')
        parsed_feedback = None
        if feedback:
            try:
                # Try multiple possible JSON parsing methods
                try:
                    parsed_feedback = json.loads(feedback)
                except json.JSONDecodeError:
                    # If direct JSON parsing fails, try to parse from a string representation
                    parsed_feedback = eval(feedback)
            except Exception as e:
                return jsonify({"error": f"Invalid feedback format: {e}"}), 400

        try:
            # Perform image search
            similar_images = semi_supervised_search.find_similar_images(
                filepath, 
                top_k=10, 
                feedback=parsed_feedback
            )
            os.remove(filepath)
            return jsonify({
                "search_type": "semi_supervised",
                "similar_images": similar_images,
                "feedback_applied": bool(parsed_feedback)
            })
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

# Health Check Endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint.
    """
    return jsonify({
        "status": "healthy",
        "simple_search_initialized": bool(simple_search.image_descriptors),
        "semi_supervised_search_initialized": bool(semi_supervised_search.image_descriptors)
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)