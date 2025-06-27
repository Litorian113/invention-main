import cv2
import numpy as np
import time
from ar_test import ar_main
from ar_modern_ui import ar_main_modern
from ar_textured import ar_main_textured
from PIL import Image, ImageDraw, ImageFont
from camera_utils import get_camera_with_fallback, get_camera_super_fast, get_fresh_frame, get_logitech_camera_optimized

def pil_to_cv2(pil_image):
    """Convert PIL image to OpenCV format"""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_image):
    """Convert OpenCV image to PIL format"""
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

def create_modern_text_overlay(width, height, text, position, font_size=24, text_color=(0, 255, 255), center_text=False):
    """Create modern text overlay with custom fonts"""
    # Create transparent overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    try:
        # Try to use modern system fonts (same as ar_modern_ui)
        fonts_to_try = [
            "arial.ttf",
            "calibri.ttf", 
            "segoeui.ttf",
            "helvetica.ttf"
        ]
        
        font = None
        for font_name in fonts_to_try:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
        
        # Fallback to default font if no system fonts found
        if font is None:
            font = ImageFont.load_default()
            
    except Exception as e:
        print(f"Font loading error: {e}")
        font = ImageFont.load_default()
    
    # Get text dimensions
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Use provided position
    x, y = position
    
    # Center text horizontally if requested
    if center_text:
        x = x - text_width // 2
    
    # Convert BGR color to RGB for PIL
    r, g, b = text_color
    rgb_color = (b, g, r, 255)  # Convert BGR to RGB and add alpha
    
    # Draw text
    draw.text((x, y), text, font=font, fill=rgb_color)
    
    return overlay

def blend_overlay_with_frame(frame, overlay):
    """Blend PIL overlay with OpenCV frame"""
    # Convert frame to PIL
    frame_pil = cv2_to_pil(frame)
    
    # Composite overlay onto frame
    composite = Image.alpha_composite(frame_pil.convert('RGBA'), overlay)
    
    # Convert back to OpenCV
    return pil_to_cv2(composite.convert('RGB'))

def basic_marker_detection():
    """Optimierte ArUco marker detection function ohne Lag"""
    print("Detection of ArUco Markers")
    print("Press 'q' to quit the application")
    
    # Use Logitech-optimized camera initialization
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("Error: Could not initialize any camera")
        return
    
    # Load the predefined dictionary for ArUco markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # AUSGEWOGENE PARAMETER: Gute Erkennung + Performance
    aruco_params.adaptiveThreshWinSizeMin = 3
    aruco_params.adaptiveThreshWinSizeMax = 23
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.03
    aruco_params.maxMarkerPerimeterRate = 4.0
    aruco_params.polygonalApproxAccuracyRate = 0.05
    aruco_params.minCornerDistanceRate = 0.05
    aruco_params.minDistanceToBorder = 3
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Vereinfachte Labels für bessere Performance (ASCII-kompatibel)
    component_labels = {
        0: "Arduino Leonardo",
        1: "Breadboard", 
        2: "LED",
        3: "220 Ohm Resistor",  # ASCII-kompatibel statt Ω
        4: "Potentiometer",
        5: "Jumper Wires"
    }
    
    # Performance-Optimierung (weniger aggressiv)
    detection_size = 960  # Höhere Detection-Größe für bessere Qualität
    detect_every = 1      # Erkenne jeden Frame für bessere Reaktionszeit
    frame_count = 0
    cached_markers = []   # Cache für Marker-Daten
    
    # FPS-Tracking
    fps_count = 0
    fps_start = time.time()
    current_fps = 0
    
    while True:
        # Capture frame-by-frame with fresh frame guarantee
        ret, frame = get_fresh_frame(cap)
        
        if not ret or frame is None:
            print("Warning: Failed to grab fresh frame, trying direct read...")
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("Error: Failed to grab frame")
                break
        
        # Validate frame dimensions
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            print("Warning: Invalid frame dimensions")
            continue
        
        frame_count += 1
        fps_count += 1
        h, w = frame.shape[:2]
        
        # ADAPTIVE DETECTION: Qualität vs. Performance Balance
        if frame_count % detect_every == 0:
            # Intelligente Skalierung basierend auf Frame-Größe
            scale = min(detection_size / max(w, h), 1.0)  # Nie größer als Original
            new_w, new_h = int(w * scale), int(h * scale)
            
            if scale < 1.0:
                small_frame = cv2.resize(frame, (new_w, new_h))
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            else:
                # Verwende Original-Frame für beste Qualität
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ArUco Detection
            corners, ids, _ = detector.detectMarkers(gray)
            
            # Cache Marker-Daten (skaliert zurück falls nötig)
            cached_markers = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    if scale < 1.0:
                        # Skaliere Koordinaten zurück
                        scaled_corner = corner / scale
                        center_x = int(np.mean(scaled_corner[0][:, 0]))
                        center_y = int(np.mean(scaled_corner[0][:, 1]))
                        # Speichere auch die Corner-Punkte für perspektivische Boxen
                        corners_2d = scaled_corner[0].astype(np.int32)
                    else:
                        # Verwende Original-Koordinaten
                        center_x = int(np.mean(corner[0][:, 0]))
                        center_y = int(np.mean(corner[0][:, 1]))
                        corners_2d = corner[0].astype(np.int32)
                    cached_markers.append((marker_id, center_x, center_y, corners_2d))
        
        # Rendere Marker aus Cache mit perspektivischen Boxen
        for marker_id, center_x, center_y, corners_2d in cached_markers:
            component_name = component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
            
            # Komponentenspezifische Farbe
            box_color = get_component_color(marker_id)
            
            # NEUE FUNKTION: Zeichne perspektivische Box um Marker
            extended_corners = draw_perspective_box(frame, corners_2d, padding=25, 
                                                  color=box_color, thickness=3)
            
            # Zeichne auch die Original-Marker-Ecken (weiß)
            cv2.polylines(frame, [corners_2d], True, (255, 255, 255), 2)
            
            # Marker-Center mit kontrastierender Farbe
            center_color = (255 - box_color[0], 255 - box_color[1], 255 - box_color[2])
            cv2.circle(frame, (center_x, center_y), 8, center_color, -1)  # Gefüllter Kreis
            cv2.circle(frame, (center_x, center_y), 10, box_color, 2)    # Farbiger Ring
            
            # Label-Box unterhalb der perspektivischen Box
            label_text = component_name
            text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Position für Label-Box (unterhalb der erweiterten Box)
            box_bottom = np.max(extended_corners[:, 1])
            label_x = center_x - text_size[0] // 2
            label_y = box_bottom + 25
            
            # Stelle sicher, dass Label nicht außerhalb des Bildschirms ist
            if label_y > h - 30:
                # Oberhalb der Box wenn zu weit unten
                box_top = np.min(extended_corners[:, 1])
                label_y = box_top - 10
            
            label_x = max(5, min(label_x, w - text_size[0] - 5))  # Horizontale Grenzen
            
            # Label-Hintergrund mit Box-Farbe
            label_bg_x1 = label_x - 8
            label_bg_y1 = label_y - text_size[1] - 8
            label_bg_x2 = label_x + text_size[0] + 8
            label_bg_y2 = label_y + 8
            
            # Schwarzer Hintergrund mit farbigem Rand
            cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), (0, 0, 0), -1)
            cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), box_color, 2)
            
            # Label-Text in Box-Farbe
            cv2.putText(frame, label_text, (label_x, label_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
            
            # Marker-ID in der oberen linken Ecke der perspektivischen Box
            id_text = f"#{marker_id}"
            id_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Position an der oberen linken Ecke der erweiterten Box
            box_top_left = extended_corners[np.argmin(extended_corners[:, 0] + extended_corners[:, 1])]
            id_bg_x1 = box_top_left[0] - 5
            id_bg_y1 = box_top_left[1] - 5
            id_bg_x2 = id_bg_x1 + id_size[0] + 10
            id_bg_y2 = id_bg_y1 + id_size[1] + 10
            
            # ID-Hintergrund in Box-Farbe
            cv2.rectangle(frame, (id_bg_x1, id_bg_y1), (id_bg_x2, id_bg_y2), box_color, -1)
            cv2.putText(frame, id_text, (id_bg_x1 + 5, id_bg_y1 + id_size[1] + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)  # Weißer Text
            
            # Optional: Koordinaten in der unteren rechten Ecke der perspektivischen Box
            coord_text = f"({center_x},{center_y})"
            coord_size = cv2.getTextSize(coord_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            
            # Position an der unteren rechten Ecke der erweiterten Box
            box_bottom_right = extended_corners[np.argmax(extended_corners[:, 0] + extended_corners[:, 1])]
            coord_x = box_bottom_right[0] - coord_size[0] - 3
            coord_y = box_bottom_right[1] - 3
            
            # Koordinaten-Hintergrund
            cv2.rectangle(frame, (coord_x - 2, coord_y - coord_size[1] - 2), 
                         (coord_x + coord_size[0] + 2, coord_y + 2), (50, 50, 50), -1)  # Dunkelgrauer Hintergrund
            cv2.putText(frame, coord_text, (coord_x, coord_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)  # Hellgrauer Text
        
        # FPS-Anzeige (alle 30 Frames aktualisieren)
        if fps_count >= 30:
            elapsed = time.time() - fps_start
            current_fps = 30 / elapsed if elapsed > 0 else 0
            fps_start = time.time()
            fps_count = 0
        
        # FPS-Display
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Markers: {len(cached_markers)}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Display the frame
        cv2.imshow('ArUco Marker Detection - Optimized', frame)
        
        # Break the loop when 'q' key is pressed (minimal delay)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release everything
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed")

def draw_rotated_rectangle(frame, center, size, angle, color, thickness=2):
    """Draw a rotated rectangle around a marker"""
    # Convert angle to radians
    angle_rad = np.radians(angle)
    
    # Calculate half dimensions
    half_width = size[0] / 2
    half_height = size[1] / 2
    
    # Define rectangle corners relative to center
    corners = np.array([
        [-half_width, -half_height],  # top-left
        [half_width, -half_height],   # top-right
        [half_width, half_height],    # bottom-right
        [-half_width, half_height]    # bottom-left
    ])
    
    # Rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    # Rotate corners
    rotated_corners = corners @ rotation_matrix.T
    
    # Translate to center position
    rotated_corners += np.array(center)
    
    # Convert to integer coordinates
    rotated_corners = rotated_corners.astype(int)
    
    # Draw the rotated rectangle
    cv2.polylines(frame, [rotated_corners], True, color, thickness)
    
    return rotated_corners

def calculate_rotated_text_position_below(center, size, angle, offset_distance=50):
    """Calculate text position below a rotated rectangle, centered"""
    # Convert angle to radians
    angle_rad = np.radians(angle)
    
    # Calculate the bottom-center of the rotated rectangle
    half_height = size[1] / 2
    
    # Get the bottom-center point of the rotated rectangle
    bottom_center_local = np.array([0, half_height + offset_distance])
    
    # Rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    # Rotate the bottom-center point
    rotated_bottom = bottom_center_local @ rotation_matrix.T
    
    # Translate to actual center position
    text_position = rotated_bottom + np.array(center)
    
    return text_position.astype(int)

def get_text_dimensions(text, font_size=28):
    """Get approximate text dimensions for positioning"""
    # Rough estimation: each character is about 0.6 * font_size wide
    # and height is approximately font_size
    width = len(text) * int(font_size * 0.6)
    height = font_size
    return width, height

def calculate_rotated_text_position(center, size, angle, offset_distance=50):
    """Calculate text position above a rotated rectangle"""
    # Convert angle to radians
    angle_rad = np.radians(angle)
    
    # Calculate the top-center of the rotated rectangle
    half_height = size[1] / 2
    
    # Get the top-center point of the rotated rectangle
    top_center_local = np.array([0, -half_height - offset_distance])
    
    # Rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])
    
    # Rotate the top-center point
    rotated_top = top_center_local @ rotation_matrix.T
    
    # Translate to actual center position
    text_position = rotated_top + np.array(center)
    
    return text_position.astype(int)

def draw_perspective_box(frame, corners, padding=20, color=(0, 255, 255), thickness=3):
    """Zeichne eine perspektivische Box um einen ArUco-Marker basierend auf seinen Ecken"""
    # Berechne erweiterte Ecken mit Padding
    center = np.mean(corners, axis=0)
    
    # Berechne Vektoren von Center zu jeder Ecke
    vectors = corners - center
    
    # Erweitere die Vektoren um das Padding
    extended_vectors = vectors * (1 + padding / 100.0)
    
    # Berechne neue Ecken
    extended_corners = center + extended_vectors
    extended_corners = extended_corners.astype(np.int32)
    
    # Zeichne die perspektivische Box
    cv2.polylines(frame, [extended_corners], True, color, thickness)
    
    # Zeichne zusätzliche Ecken-Punkte für bessere Sichtbarkeit
    for corner in extended_corners:
        cv2.circle(frame, tuple(corner), 4, color, -1)
    
    return extended_corners

def get_component_color(marker_id):
    """Gib komponentenspezifische Farben zurück"""
    colors = {
        0: (255, 0, 0),    # Arduino - Blau
        1: (0, 255, 0),    # Breadboard - Grün  
        2: (0, 0, 255),    # LED - Rot
        3: (0, 255, 255),  # Resistor - Gelb/Cyan
        4: (255, 0, 255),  # Potentiometer - Magenta
        5: (255, 255, 0)   # Jumper Wires - Cyan/Gelb
    }
    return colors.get(marker_id, (255, 255, 255))  # Default: Weiß

def main():
    print("=== ArUco Marker Detection & AR Application ===")
    print("Choose an option:")
    print("1. Basic ArUco Marker Detection")
    print("2. AR 3D Visualization (Enhanced OpenCV)")
    print("3. AR Clean UI (Black Text, Custom Fonts)")
    print("4. AR Textured Model (UV Mapped Breadboard)")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\nStarting Basic ArUco Marker Detection...")
                basic_marker_detection()
                break
            elif choice == "2":
                print("\nStarting AR 3D Visualization...")
                ar_main()
                break
            elif choice == "3":
                print("\nStarting Clean AR with Black Text...")
                ar_main_modern()
                break
            elif choice == "4":
                print("\nStarting Textured AR with UV Mapping...")
                ar_main_textured()
                break
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()