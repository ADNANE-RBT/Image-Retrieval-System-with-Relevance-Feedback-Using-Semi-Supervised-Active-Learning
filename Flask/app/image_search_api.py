import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Add CORS support

# Import descriptor calculation function
from Descriptors_calcul import calculate_descriptors

# Import search implementations
from Simple_search_debug import ImageSimilaritySearch
from contineous_SS_RF import SemiSupervisedImageSearch

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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



@app.route('/simple_search', methods=['POST'])
def simple_image_search():
    try:
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
                top_k = int(request.form.get('top_k', 10))
                similar_images = simple_search.find_similar_images(filepath, top_k=top_k)
                
                # Optional: you might want to process paths to remove absolute path prefixes
                processed_similar_images = [
                    {
                        "image_path": img_result['image_path'].replace(
                            f"{DATASET_PATH}\\", ""
                        ).replace("\\", "/"),
                        "similarity_score": img_result['similarity_score']
                    }
                    for img_result in similar_images
                ]
                
                os.remove(filepath)
                return jsonify({
                    "search_type": "simple_similarity",
                    "similar_images": processed_similar_images
                })
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": str(e)}), 500
        
        return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/semi_supervised_search', methods=['POST'])
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
@app.route('/image/<path:filename>', methods=['GET'])
def get_image(filename):
    """
    Serve an image from the dataset.
    """
    try:
        # Ensure the requested file exists in the dataset directory
        filepath = os.path.join(DATASET_PATH, filename)
        if os.path.exists(filepath):
            return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath))
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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