import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def create_descriptor_visualization(descriptors):
    """
    Create a visualization of image descriptors across 6 subplots with suitable visualization methods.
    
    Expected descriptors dictionary structure:
    {
        "color": {
            "histogram": numpy.ndarray,  # Histogram with RGB values
            "dominant_colors": numpy.ndarray  # Dominant colors as RGB triplets
        },
        "texture": {
            "gabor_filters": numpy.ndarray,  # Gabor filter responses
            "glcm_features": numpy.ndarray   # GLCM features
        },
        "shape": {
            "hu_moments": numpy.ndarray,     # Hu moments
            "shape_descriptors": numpy.ndarray  # Other shape descriptors
        }
    }
    """
    color_hist = descriptors["color"]["histogram"]
    red_hist = color_hist[:256]
    green_hist = color_hist[256:512]
    blue_hist = color_hist[512:]
    # Create figure with 2x3 subplots
    fig, axs = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Image Descriptors Visualization', fontsize=16)
    
    # 1. Color Histogram (line plot)
    axs[0, 0].plot(range(256), red_hist, label='Red', color='red')
    axs[0, 0].plot(range(256), green_hist, label='Green', color='green')
    axs[0, 0].plot(range(256), blue_hist, label='Blue', color='blue')
    axs[0, 0].set_title('Color Histogram')
    axs[0, 0].set_xlabel('Bin Index')
    axs[0, 0].set_ylabel('Frequency')
    axs[0, 0].legend()

    # 2. Dominant Colors (Image visualization)
    dominant_colors = descriptors["color"]["dominant_colors"]
    # Ensure dominant colors are in the valid RGBA range [0, 1]
    dominant_colors = np.clip(dominant_colors / 255.0, 0, 1)  # Normalize RGB values
    # Reshape the colors into a 1xN image
    axs[0, 1].imshow([dominant_colors], aspect='auto')
    axs[0, 1].set_title('Dominant Colors')
    axs[0, 1].axis('off')  # Hide axes for better visual presentation

    # 3. Gabor Features (bar plot)
    axs[0, 2].bar(range(len(descriptors["texture"]["gabor_filters"])), descriptors["texture"]["gabor_filters"], color='orange')
    axs[0, 2].set_title('Gabor Features')
    axs[0, 2].set_xlabel('Feature Index')
    axs[0, 2].set_ylabel('Feature Value')

    # 4. GLCM Features (bar plot)
    axs[1, 0].bar(range(len(descriptors["texture"]["glcm_features"])), descriptors["texture"]["glcm_features"], color='purple')
    axs[1, 0].set_title('GLCM Features')
    axs[1, 0].set_xlabel('Feature Index')
    axs[1, 0].set_ylabel('Feature Value')

    # 5. Hu Moments (bar plot)
    axs[1, 1].bar(range(len(descriptors["shape"]["hu_moments"])), descriptors["shape"]["hu_moments"], color='green')
    axs[1, 1].set_title('Hu Moments')
    axs[1, 1].set_xlabel('Moment Index')
    axs[1, 1].set_ylabel('Moment Value')

    # 6. Shape Descriptors (bar plot)
    axs[1, 2].bar(range(len(descriptors["shape"]["shape_descriptors"])), descriptors["shape"]["shape_descriptors"], color='blue')
    axs[1, 2].set_title('Shape Descriptors')
    axs[1, 2].set_xlabel('Descriptor Index')
    axs[1, 2].set_ylabel('Descriptor Value')

    plt.tight_layout()
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close('all')
    
    return buf
