import numpy as np
from Descriptors_calcul import calculate_descriptors
def update_weights(weights, IR_t, INR_t, Lc):
    """
    Update descriptor weights based on user feedback.

    Args:
        weights (dict): Current weights for descriptors and sub-descriptors.
        IR_t (list of tuples): Relevant image pairs (e.g., [(img1, img2), ...]).
        INR_t (list of tuples): Non-relevant image pairs (e.g., [(img1, img2), ...]).
        Lc (float): Feedback adjustment parameter.

    Returns:
        dict: Updated weights.
    """
    print('updating')
    k = len(weights)  # Total number of descriptor types
    w_x = w_y = 1 - (1 / k)
    w_r = w_x * w_y

    for descriptor, descriptor_weights in weights.items():
        for sub_desc, sub_weight in descriptor_weights.items():
            if sub_desc == "weight":
                continue
            
            # Adjust weights for relevant pairs
            for img_x, img_y in IR_t:
                lambda_positive = 1 - min(1, Lc * w_r)
                weights[descriptor][sub_desc] *= lambda_positive
            
            # Adjust weights for non-relevant pairs
            for img_x, img_y in INR_t:
                lambda_negative = 1 + max(1, Lc * w_r)
                weights[descriptor][sub_desc] *= lambda_negative

    return weights
def calculate_distance(value1, value2):
    """Enhanced distance calculation with more robust normalization."""
    def normalize(x):
        x = np.array(x, dtype=float)
        return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-10)
    
    try:
        norm_value1 = normalize(value1)
        norm_value2 = normalize(value2)
        
        # Multiple distance metrics with adaptive weighting
        euclidean = np.linalg.norm(norm_value1 - norm_value2)
        cosine_distance = 1 - np.dot(norm_value1, norm_value2)
        manhattan_distance = np.sum(np.abs(norm_value1 - norm_value2))
        
        # Dynamically weighted distance
        return 0.4 * euclidean + 0.3 * cosine_distance + 0.3 * manhattan_distance
    
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return 1.0

def calculate_global_distance(desc1, desc2, weights=None):
    """
    Calculate the overall similarity between two image descriptors.
    """
    # Default weights if not provided
    if weights is None:
        weights = {
            "color": {
                "weight": 0.6,  # Highest priority for color
                "histogram": 0.8,  # Very strong emphasis on color distribution
                "dominant_colors": 0.2
            },
            "texture": {
                "weight": 0.3,
                "gabor_filters": 0.7,  # Strong texture feature extraction
                "glcm_features": 0.3
            },
            "shape": {
                "weight": 0.1,  # Minimal shape impact
                "hu_moments": 0.6,
                "shape_descriptors": 0.4
            }
        }
    
    global_distance = 0.0
    total_weight = 0.0
    
    for descriptor, descriptor_weights in weights.items():
        descriptor_weight = descriptor_weights.get("weight", 1.0)
        
        sub_distances = []
        for sub_desc, sub_weight in descriptor_weights.items():
            if sub_desc == "weight":
                continue
            
            # Convert to dictionary if numpy array
            value1 = desc1[descriptor][sub_desc] if isinstance(desc1[descriptor], dict) else desc1[descriptor]
            value2 = desc2[descriptor][sub_desc] if isinstance(desc2[descriptor], dict) else desc2[descriptor]
            
            if value1 is not None and value2 is not None:
                sub_distance = calculate_distance(value1, value2)
                sub_distances.append(sub_weight * sub_distance)
        
        # Combine sub-descriptor distances
        if sub_distances:
            descriptor_distance = np.mean(sub_distances)
            global_distance += descriptor_weight * descriptor_distance
            total_weight += descriptor_weight
    
    # Normalize by total weight
    return global_distance / (total_weight + 1e-10)

def test_image_similarity(image_paths=None):
    """
    Test image similarity calculation.
    
    Args:
        image_paths (list, optional): Paths to images to compare
    """
    # Default image paths if not provided
    if image_paths is None:
        image_paths = [
            '../../Dataset/RSSCN7-master/aGrass/a002.jpg',
            '../../Dataset/RSSCN7-master/aGrass/a001.jpg'
        ]
    
    # Calculate descriptors for each image
    image_descriptors = []
    for path in image_paths:
        try:
            descriptors = calculate_descriptors(path)
            image_descriptors.append(descriptors)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    # Calculate and print distances between images
    print("Image Distances:")
    for i in range(len(image_descriptors)):
        for j in range(i+1, len(image_descriptors)):
            distance = calculate_global_distance(
                image_descriptors[i], 
                image_descriptors[j]
            )
            print(f"Distance between image {i+1} and image {j+1}: {distance}")

# Run the test when script is executed directly
if __name__ == "__main__":
    test_image_similarity()