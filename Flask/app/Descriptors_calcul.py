import cv2
import numpy as np

def calculate_descriptors(image_path):
    """
    Calculate comprehensive image descriptors from an input image.
    
    Args:
        image_path (str): Path to the input image
    
    Returns:
        dict: Dictionary of image descriptors
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at {image_path} not found.")

    # Calculate descriptors
    color_features = calculate_color_features(image)
    texture_features = calculate_texture_features(image)
    shape_features = calculate_shape_features(image)

    return {
        "color": color_features,
        "texture": texture_features,
        "shape": shape_features
    }

def calculate_color_features(image):
    """
    Extract color-based features from an image.
    
    Args:
        image (numpy.ndarray): Input image
    
    Returns:
        dict: Color-based features
    """
    # Color histogram
    hist_b = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_g = cv2.calcHist([image], [1], None, [256], [0, 256]).flatten()
    hist_r = cv2.calcHist([image], [2], None, [256], [0, 256]).flatten()
    
    # Normalize histograms
    color_histogram = np.concatenate([
        hist_b / (np.sum(hist_b) + 1e-10),
        hist_g / (np.sum(hist_g) + 1e-10),
        hist_r / (np.sum(hist_r) + 1e-10)
    ])

    # Dominant colors using K-means
    reshaped_image = image.reshape((-1, 3)).astype(np.float32)
    k = 3  # Number of dominant colors
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(
        reshaped_image, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )
    
    # Prepare dominant colors feature
    dominant_colors = np.concatenate([
        centers.flatten(),  # Color centers
        np.array([np.sum(labels == i) / len(labels) for i in range(k)])  # Color percentages
    ])

    return {
        "histogram": color_histogram,
        "dominant_colors": dominant_colors
    }

def calculate_texture_features(image):
    """
    Extract texture-based features from an image.
    
    Args:
        image (numpy.ndarray): Input image
    
    Returns:
        dict: Texture-based features
    """
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Gabor filter features
    gabor_features = calculate_gabor_features(gray_image)

    # GLCM features
    glcm_features = calculate_glcm_features(gray_image)

    return {
        "gabor_filters": gabor_features,
        "glcm_features": glcm_features
    }

def calculate_gabor_features(gray_image):
    """
    Compute Gabor filter features.
    
    Args:
        gray_image (numpy.ndarray): Grayscale input image
    
    Returns:
        numpy.ndarray: Gabor filter responses
    """
    kernels = []
    responses = []
    
    for theta in range(4):
        theta_rad = theta / 4.0 * np.pi
        kernel = cv2.getGaborKernel(
            (21, 21), 8.0, theta_rad, 10.0, 0.5, 0, ktype=cv2.CV_32F
        )
        kernels.append(kernel)
        
        # Apply Gabor filter and compute mean response
        filtered = cv2.filter2D(gray_image, cv2.CV_8UC1, kernel)
        responses.append(np.mean(filtered))
    
    return np.array(responses)

def calculate_glcm_features(gray_image):
    """
    Compute Gray Level Co-occurrence Matrix (GLCM) features.
    
    Args:
        gray_image (numpy.ndarray): Grayscale input image
    
    Returns:
        numpy.ndarray: GLCM-based texture features
    """
    # Define GLCM parameters
    distances = [1]
    angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    
    all_features = []
    
    for angle in angles:
        # Compute GLCM
        glcm = np.zeros((256, 256), dtype=np.float32)
        offset_x = int(np.cos(angle))
        offset_y = int(np.sin(angle))
        
        for x in range(gray_image.shape[0] - abs(offset_y)):
            for y in range(gray_image.shape[1] - abs(offset_x)):
                i, j = gray_image[x, y], gray_image[x + offset_y, y + offset_x]
                glcm[i, j] += 1
        
        # Normalize GLCM
        glcm /= (np.sum(glcm) + 1e-10)
        
        # Compute texture features
        features = []
        
        # Contrast
        features.append(np.sum([(i - j)**2 * glcm[i, j] for i in range(256) for j in range(256)]))
        
        # Correlation
        features.append(np.sum([i * j * glcm[i, j] for i in range(256) for j in range(256)]))
        
        # Energy
        features.append(np.sum([glcm[i, j]**2 for i in range(256) for j in range(256)]))
        
        all_features.extend(features)
    
    return np.array(all_features)

def calculate_shape_features(image):
    """
    Extract shape-based features from an image.
    
    Args:
        image (numpy.ndarray): Input image
    
    Returns:
        dict: Shape-based features
    """
    # Convert to grayscale and threshold
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return {
            "hu_moments": np.zeros(7),
            "shape_descriptors": np.zeros(3)
        }
    
    # Use largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Hu Moments
    moments = cv2.moments(largest_contour)
    hu_moments = cv2.HuMoments(moments).flatten()
    
    # Additional shape descriptors
    x, y, w, h = cv2.boundingRect(largest_contour)
    aspect_ratio = w / h if h != 0 else 0
    extent = cv2.contourArea(largest_contour) / (w * h) if w * h != 0 else 0
    
    shape_descriptors = np.array([aspect_ratio, extent, cv2.contourArea(largest_contour)])
    
    return {
        "hu_moments": hu_moments,
        "shape_descriptors": shape_descriptors
    }