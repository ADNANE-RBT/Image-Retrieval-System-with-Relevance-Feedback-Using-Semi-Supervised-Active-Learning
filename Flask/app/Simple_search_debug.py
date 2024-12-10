import os
import json
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from Descriptors_calcul import calculate_descriptors
from Global_distance_calcul import calculate_global_distance

class ImageSimilaritySearch:
    def __init__(self, dataset_path, descriptors_file='image_descriptors.json'):
        """
        Initialize the image similarity search system.
        
        Args:
            dataset_path (str): Path to the directory containing images
            descriptors_file (str): Path to the JSON file storing precomputed descriptors
        """
        self.dataset_path = dataset_path
        self.descriptors_file = descriptors_file
        self.image_descriptors = {}
        self.image_paths = []
        
        # Load or precompute descriptors
        self._load_or_precompute_descriptors()
    
    def _load_or_precompute_descriptors(self):
        """
        Load descriptors from a file or precompute them if not available.
        """
        if os.path.exists(self.descriptors_file):
            print("Loading descriptors from disk...")
            with open(self.descriptors_file, 'r') as file:
                data = json.load(file)
                self.image_descriptors = {
                    k: {
                        descriptor_type: {
                            sub_k: np.array(sub_v) 
                            for sub_k, sub_v in descriptor_data.items()
                        }
                        for descriptor_type, descriptor_data in v.items()
                    }
                    for k, v in data.items()
                }
                self.image_paths = list(self.image_descriptors.keys())
            print(f"Loaded descriptors for {len(self.image_descriptors)} images")
        else:
            print("Descriptors file not found. Precomputing descriptors...")
            self._precompute_descriptors()
            self._save_descriptors()

    
    def _precompute_descriptors(self):
        """
        Precompute descriptors for all images in the dataset and save incrementally.
        """
        # Initialize or load existing descriptors
        if os.path.exists(self.descriptors_file):
            with open(self.descriptors_file, 'r') as file:
                self.image_descriptors = json.load(file)
        else:
            self.image_descriptors = {}

        # Process images and save descriptors incrementally
        for root, _, files in os.walk(self.dataset_path):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    full_path = os.path.join(root, filename)
                    
                    # Skip if already processed
                    if full_path in self.image_descriptors:
                        continue
                    
                    try:
                        print(f"Calculating descriptors for {full_path}...")
                        descriptors = calculate_descriptors(full_path)
                        
                        # Convert descriptors to JSON-serializable format
                        serializable_descriptors = {
                            descriptor_type: {
                                k: v.tolist() if hasattr(v, 'tolist') else v 
                                for k, v in descriptor_data.items()
                            }
                            for descriptor_type, descriptor_data in descriptors.items()
                        }
                        
                        # Add to image descriptors
                        self.image_descriptors[full_path] = serializable_descriptors
                        self.image_paths.append(full_path)
                        
                        # Save to file after each image
                        with open(self.descriptors_file, 'w') as file:
                            json.dump(self.image_descriptors, file)
                        
                        print(f"Saved descriptors for {full_path}")
                    
                    except Exception as e:
                        print(f"Error processing {full_path}: {e}")

        print(f"Precomputed descriptors for {len(self.image_descriptors)} images")
    
    def _save_descriptors(self):
        """
        Save descriptors to a JSON file to avoid recalculating them.
        """
        print("Saving descriptors to disk...")
        # Convert nested descriptors to a serializable format
        serializable_descriptors = {}
        for path, descriptors in self.image_descriptors.items():
            serializable_descriptors[path] = {
                descriptor_type: {
                    k: v.tolist() if hasattr(v, 'tolist') else v 
                    for k, v in descriptor_data.items()
                }
                for descriptor_type, descriptor_data in descriptors.items()
            }
        
        with open(self.descriptors_file, 'w') as file:
            json.dump(serializable_descriptors, file)
        print("Descriptors saved successfully")

    def find_similar_images(self, query_image_path, top_k=5):
        """
        Find the most similar images to the query image.
        
        Args:
            query_image_path (str): Path to the query image
            top_k (int): Number of similar images to return
        
        Returns:
            list: Detailed information about the most similar images
        """
        try:
            print(f"Calculating descriptors for query image: {query_image_path}...")
            query_descriptors = calculate_descriptors(query_image_path)
            
            print("Calculating distances to dataset images...")
            distances = []
            for path, dataset_descriptors in self.image_descriptors.items():
                try:
                    # Convert the nested dictionary back to a format compatible with calculate_global_distance
                    normalized_descriptors = {
                        descriptor_type: {
                            k: np.array(v) for k, v in descriptor_group.items()
                        }
                        for descriptor_type, descriptor_group in dataset_descriptors.items()
                    }
                    
                    distance = calculate_global_distance(query_descriptors, normalized_descriptors)
                    distances.append((path, distance))
                except Exception as e:
                    print(f"Error processing {path}: {e}")
            
            # Sort distances and get top k
            distances.sort(key=lambda x: x[1])
            print(f"Found {len(distances)} similar images. Returning top {top_k}.")
            
            # Return detailed results with file path and similarity score
            return [
                {
                    "image_path": path, 
                    "similarity_score": float(distance)  # Convert to float for JSON serialization
                } 
                for path, distance in distances[:top_k]
            ]
        
        except Exception as e:
            print(f"Error finding similar images: {e}")
            return []
# Flask Application
app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure dataset path (replace with your actual dataset path)
DATASET_PATH = '../../Dataset/RSSCN7-master'

# Initialize image search system
image_search = ImageSimilaritySearch(DATASET_PATH)

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/search', methods=['POST'])
def search_similar_images():
    """
    Endpoint to find similar images.
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
            similar_images = image_search.find_similar_images(filepath, top_k=5)
            os.remove(filepath)
            return jsonify({"similar_images": similar_images})
        except Exception as e:
            os.remove(filepath)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
