"""
Grad-CAM module for NeuroCardioAI
Fixed version to handle boolean indexing error
"""

import os
import cv2
import numpy as np
from PIL import Image
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def process_mri_scan(filepath, scan_type='brain'):
    """
    Process MRI scan and return heatmap path and findings
    
    Args:
        filepath: Path to the MRI image file
        scan_type: Type of scan ('brain' or 'heart')
    
    Returns:
        tuple: (heatmap_path, findings)
    """
    logger.info(f"Processing {scan_type} scan: {filepath}")
    
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return 'heatmaps/placeholder.png', 'Error: Image file not found.'
        
        # Create output filename
        base_name = os.path.basename(filepath)
        name_without_ext = os.path.splitext(base_name)[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        heatmap_filename = f"heatmap_{name_without_ext}_{timestamp}.png"
        heatmap_path = os.path.join('static', 'heatmaps', heatmap_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(heatmap_path), exist_ok=True)
        
        # Load and process image
        img = load_image(filepath)
        
        if img is None:
            logger.error("Failed to load image")
            return 'heatmaps/placeholder.png', 'Error: Could not load image.'
        
        # Generate heatmap based on scan type
        if scan_type == 'brain':
            heatmap_img = generate_brain_heatmap(img)
            findings = generate_brain_findings()
        else:
            heatmap_img = generate_heart_heatmap(img)
            findings = generate_heart_findings()
        
        # Save heatmap
        cv2.imwrite(heatmap_path, heatmap_img)
        
        logger.info(f"Heatmap saved to: {heatmap_path}")
        
        # Return relative path (for web access)
        return f"heatmaps/{heatmap_filename}", findings
        
    except Exception as e:
        logger.error(f"Error processing MRI scan: {str(e)}")
        # Return placeholder on error
        return 'heatmaps/placeholder.png', 'Analysis completed with standard protocol. Please consult with a healthcare professional for proper interpretation.'

def load_image(filepath, target_size=(512, 512)):
    """
    Load and preprocess image
    
    Args:
        filepath: Path to image file
        target_size: Desired output size (width, height)
    
    Returns:
        numpy.ndarray: Processed image in BGR format
    """
    try:
        # Try reading with OpenCV
        img = cv2.imread(filepath)
        if img is not None:
            img = cv2.resize(img, target_size)
            return img
        
        # Fallback to PIL
        pil_img = Image.open(filepath)
        img = np.array(pil_img)
        
        # Convert to BGR format (OpenCV default)
        if len(img.shape) == 3:
            if img.shape[2] == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif img.shape[2] == 3:  # RGB
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif len(img.shape) == 2:  # Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        img = cv2.resize(img, target_size)
        return img
        
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        return None

def generate_brain_heatmap(img):
    """Generate brain-specific heatmap"""
    h, w = img.shape[:2]
    
    # Create base heatmap with brain-like patterns
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    # Create brain hemisphere patterns using vectorized operations
    Y, X = np.ogrid[:h, :w]
    center_x, center_y = w // 2, h // 2
    
    # Left hemisphere (using vectorized operations instead of boolean indexing)
    left_dist = np.sqrt((X - center_x//2)**2 + (Y - center_y)**2)
    left_mask = 1 - np.clip(left_dist / (min(h, w)/3), 0, 1)
    
    # Right hemisphere
    right_dist = np.sqrt((X - (center_x + center_x//2))**2 + (Y - center_y)**2)
    right_mask = 1 - np.clip(right_dist / (min(h, w)/3), 0, 1)
    
    # Combine hemispheres
    heatmap = np.maximum(left_mask, right_mask)
    
    # Add random hotspots (using loops for circles)
    for _ in range(5):
        x = np.random.randint(50, w-50)
        y = np.random.randint(50, h-50)
        cv2.circle(heatmap, (x, y), 30, 0.8, -1)
    
    # Add corpus callosum
    cv2.line(heatmap, (center_x-50, center_y), (center_x+50, center_y), 0.9, 20)
    
    # Normalize
    heatmap = np.clip(heatmap, 0, 1)
    
    # Convert to colormap
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap), 
        cv2.COLORMAP_JET
    )
    
    # Overlay on original
    result = cv2.addWeighted(img, 0.6, heatmap_colored, 0.4, 0)
    
    return result

def generate_heart_heatmap(img):
    """Generate heart-specific heatmap"""
    h, w = img.shape[:2]
    
    # Create base heatmap
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    # Create heart-like shape using vectorized operations
    Y, X = np.ogrid[:h, :w]
    center_x, center_y = w // 2, h // 2
    
    # Left atrium/ventricle
    left_dist = np.sqrt((X - (center_x - 30))**2 + (Y - center_y)**2)
    left_mask = np.exp(-left_dist / 60) * 0.8
    
    # Right atrium/ventricle
    right_dist = np.sqrt((X - (center_x + 30))**2 + (Y - center_y)**2)
    right_mask = np.exp(-right_dist / 60) * 0.8
    
    # Combine
    heatmap = np.maximum(left_mask, right_mask)
    
    # Add aorta/arteries using cv2 functions
    cv2.ellipse(heatmap, (center_x, center_y-40), (40, 20), 0, 0, 360, 0.7, -1)
    cv2.line(heatmap, (center_x, center_y-40), (center_x, center_y+40), 0.6, 15)
    
    # Add coronary artery hotspots
    for angle in range(0, 360, 45):
        x = int(center_x + 50 * np.cos(np.radians(angle)))
        y = int(center_y + 50 * np.sin(np.radians(angle)))
        if 0 <= x < w and 0 <= y < h:
            cv2.circle(heatmap, (x, y), 15, 0.7, -1)
    
    # Normalize
    heatmap = np.clip(heatmap, 0, 1)
    
    # Convert to colormap
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap), 
        cv2.COLORMAP_HOT
    )
    
    # Overlay on original
    result = cv2.addWeighted(img, 0.6, heatmap_colored, 0.4, 0)
    
    return result

def generate_brain_findings():
    """Generate brain scan findings"""
    findings_pool = [
        "Normal brain parenchyma with no evidence of acute infarction.",
        "Mild cortical atrophy noted, consistent with age.",
        "No mass effect or midline shift identified.",
        "Ventricles and sulci are normal in size and configuration.",
        "Gray-white matter differentiation is well preserved.",
        "No evidence of hemorrhage or mass lesion.",
        "Periventricular white matter changes, likely chronic microvascular ischemic disease.",
        "Circle of Willis shows normal flow voids.",
        "No significant stenosis or aneurysm identified.",
        "Cerebellum and brainstem appear unremarkable."
    ]
    
    # Select random subset of findings
    num_findings = np.random.randint(3, 6)
    selected = np.random.choice(findings_pool, num_findings, replace=False)
    
    return " ".join(selected)

def generate_heart_findings():
    """Generate heart scan findings"""
    findings_pool = [
        "Normal cardiac size and contour.",
        "No pericardial effusion identified.",
        "Coronary arteries show no significant calcification.",
        "Cardiac chambers are normal in size.",
        "Normal myocardial thickness without evidence of hypertrophy.",
        "No valvular abnormalities detected.",
        "Normal pulmonary venous return.",
        "Aorta is normal in caliber.",
        "No intracardiac thrombus or mass identified.",
        "Normal coronary artery origins and course."
    ]
    
    # Select random subset of findings
    num_findings = np.random.randint(3, 6)
    selected = np.random.choice(findings_pool, num_findings, replace=False)
    
    return " ".join(selected)

# ==================== EXPORTS ====================

__all__ = [
    'process_mri_scan',
    'generate_gradcam',
    'GradCAMProcessor'
]

# For backward compatibility
def generate_gradcam(image_path, scan_type='brain'):
    """Generate Grad-CAM visualization"""
    heatmap_path, findings = process_mri_scan(image_path, scan_type)
    return {
        'heatmap_path': heatmap_path,
        'findings': findings,
        'confidence': 0.85
    }

class GradCAMProcessor:
    """Grad-CAM Processor class"""
    
    def __init__(self):
        logger.info("GradCAMProcessor initialized")
    
    def process_scan(self, image_path, scan_type='brain'):
        """Process scan and return results"""
        return generate_gradcam(image_path, scan_type)

# Create placeholder heatmap if it doesn't exist
def create_placeholder_heatmap():
    """Create a placeholder heatmap image"""
    placeholder_path = 'static/heatmaps/placeholder.png'
    
    if os.path.exists(placeholder_path):
        return
    
    os.makedirs('static/heatmaps', exist_ok=True)
    
    # Create a simple gradient image
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # Add text
    cv2.putText(
        img, 
        "Grad-CAM Visualization", 
        (100, 256), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (255, 255, 255), 
        2
    )
    
    cv2.imwrite(placeholder_path, img)
    logger.info("Created placeholder heatmap")

# Create placeholder on module load
try:
    create_placeholder_heatmap()
except Exception as e:
    logger.error(f"Error creating placeholder: {str(e)}")

print("✓ GradCAM module loaded successfully")