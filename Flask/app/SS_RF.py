from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import json

# Import the updated SemiSupervisedImageSearch class
from semi_supervised_search import SemiSupervisedImageSearch

# Flask App Configuration
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATASET_PATH = '../../Dataset/RSSCN7-master'

# Initialize Semi-Supervised Image Search System
image_search = SemiSupervisedImageSearch(DATASET_PATH)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Flask Route: Image Search Endpoint
@app.route('/search', methods=['POST'])
def search_similar_images():
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
                parsed_feedback = json.loads(feedback)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid feedback format"}), 400

        try:
            # Perform image search
            similar_images = image_search.find_similar_images(
                filepath, 
                top_k=5, 
                feedback=parsed_feedback
            )
            os.remove(filepath)
            return jsonify({"similar_images": similar_images})
        except Exception as e:
            os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
