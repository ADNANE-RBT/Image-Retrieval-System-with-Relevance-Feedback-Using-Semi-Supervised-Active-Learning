from sklearn.semi_supervised import LabelSpreading
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import json
from Descriptors_calcul import calculate_descriptors
from Global_distance_calcul import calculate_global_distance

class SemiSupervisedImageSearch:
    def __init__(self, dataset_path, descriptors_file='image_descriptors.json'):
        self.dataset_path = dataset_path
        self.descriptors_file = descriptors_file
        self.image_descriptors = {}
        self.image_paths = []
        self.weights = {
            "color": {"weight": 0.4, "histogram": 0.6, "dominant_colors": 0.4},
            "texture": {"weight": 0.3, "gabor_filters": 0.5, "glcm_features": 0.5},
            "shape": {"weight": 0.3, "hu_moments": 0.7, "shape_descriptors": 0.3},
        }
        self.scaler = StandardScaler()
        self.semi_supervised_model = LabelSpreading(kernel='rbf', alpha=0.8)
        self._load_or_precompute_descriptors()
        self._prepare_feature_matrix()
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
    def _prepare_feature_matrix(self):
        """Prepare feature matrix and initialize labels."""
        feature_matrix = []
        for path, descriptors in self.image_descriptors.items():
            features = []
            for desc_type in ['color', 'texture', 'shape']:
                for sub_desc, values in descriptors[desc_type].items():
                    if sub_desc != 'weight':
                        features.extend(values)
            feature_matrix.append(features)

        # Convert to numpy array and scale
        self.feature_matrix = np.array(feature_matrix)

        # Check for invalid values in the feature matrix
        if np.any(np.isnan(self.feature_matrix)):
            print("Feature matrix contains NaNs. Replacing with column means...")
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='mean')
            self.feature_matrix = imputer.fit_transform(self.feature_matrix)
            
        if np.any(np.isinf(self.feature_matrix)):
            print("Feature matrix contains infinite values. Replacing with column means...")
            self.feature_matrix = np.nan_to_num(self.feature_matrix)  # Replace inf with max float
        
        if np.all(self.feature_matrix == 0):
            print("Feature matrix is all zeros. Check descriptors.")
            raise ValueError("Feature matrix is all zeros. Ensure descriptors are calculated correctly.")

        # Scale the feature matrix
        self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)

        # Initialize labels
        self.labels = np.zeros(len(self.image_paths))  # Initial labels


    def _update_weights(self, feedback, Lc=0.5):
        """Update descriptor weights based on user feedback."""
        relevant_images = feedback.get("relevant", [])
        non_relevant_images = feedback.get("non_relevant", [])

        for descriptor, sub_weights in self.weights.items():
            for sub_desc, sub_weight in sub_weights.items():
                if sub_desc == "weight":
                    continue
                
                # Adjust weights for relevant images
                for img in relevant_images:
                    idx = self.image_paths.index(img)
                    rel_factor = 1 - min(1, Lc * self.labels[idx])
                    self.weights[descriptor][sub_desc] *= rel_factor

                # Adjust weights for non-relevant images
                for img in non_relevant_images:
                    idx = self.image_paths.index(img)
                    non_rel_factor = 1 + max(1, Lc * self.labels[idx])
                    self.weights[descriptor][sub_desc] *= non_rel_factor

    def find_similar_images(self, query_image_path, top_k=5, feedback=None):
        try:
            # If feedback is provided, update weights and model
            if feedback:
                relevant_images = feedback.get("relevant", [])
                non_relevant_images = feedback.get("non_relevant", [])
                
                # Update labels
                for img in relevant_images:
                    idx = self.image_paths.index(img)
                    self.labels[idx] = 1
                
                for img in non_relevant_images:
                    idx = self.image_paths.index(img)
                    self.labels[idx] = -1

                # Update weights
                self._update_weights(feedback, Lc=0.5)

                # Fit semi-supervised model
                self.semi_supervised_model.fit(self.feature_matrix, self.labels)
                
                # Get predicted probabilities
                predicted_probs = self.semi_supervised_model.predict_proba(self.feature_matrix)
            
            # Calculate descriptors for query image
            query_descriptors = calculate_descriptors(query_image_path)
            query_features = []
            for desc_type in ['color', 'texture', 'shape']:
                for sub_desc, values in query_descriptors[desc_type].items():
                    if sub_desc != 'weight':
                        query_features.extend(values)
            
            # Scale query features
            scaled_query_features = self.scaler.transform([query_features])
            
            # Calculate distances
            distances = []
            for idx, path in enumerate(self.image_paths):
                dataset_descriptors = self.image_descriptors[path]
                
                # Calculate global distance
                distance = calculate_global_distance(
                    query_descriptors, 
                    dataset_descriptors, 
                    self.weights
                )
                
                # Combine distance with label probability
                if feedback:
                    label_prob = predicted_probs[idx][1]  # Probability of positive class
                    combined_score = 0.7 * distance + 0.3 * label_prob
                    distances.append((path, combined_score))
                else:
                    distances.append((path, distance))
            
            # Sort and return top-k images
            distances.sort(key=lambda x: x[1])
            return [path for path, _ in distances[:top_k]]
        
        except Exception as e:
            print(f"Error finding similar images: {e}")
            return []

