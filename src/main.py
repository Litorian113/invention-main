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
    """ArUco marker detection mit AR-Overlays - zeigt erkannte Komponenten und Schritt-für-Schritt-Anleitung"""
    print("AR Electronics Tutorial - Detection mit Overlay")
    print("Links: Erkannte Komponenten | Rechts: Schritt-für-Schritt-Anleitung")
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
        
        # AR-Overlay mit erkannten Komponenten und Schritt-für-Schritt-Anleitung
        detected_components_list = [(marker_id, corners_2d) for marker_id, _, _, corners_2d in cached_markers]
        draw_ar_overlay(frame, detected_components_list, w, h)
        
        # FPS-Display (kleinere Position, da Overlay-Panels mehr Platz brauchen)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (w//2 - 50, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Markers: {len(cached_markers)}", (w//2 - 50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Display the frame
        cv2.imshow('AR Electronics Tutorial - Schritt-für-Schritt Anleitung', frame)
        
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

def draw_ar_overlay(frame, detected_components, frame_width, frame_height):
    """Zeichne AR-Overlay mit erkannten Komponenten links und Schritt-für-Schritt-Anleitung rechts"""
    overlay_height = frame_height - 100
    overlay_start_y = 50
    
    # Linkes Panel: Erkannte Komponenten
    draw_components_panel(frame, detected_components, overlay_start_y, overlay_height)
    
    # Rechtes Panel: Schritt-für-Schritt-Anleitung
    draw_instructions_panel(frame, detected_components, frame_width, overlay_start_y, overlay_height)

def draw_components_panel(frame, detected_components, start_y, height):
    """Zeichne das linke Panel mit erkannten Komponenten"""
    panel_width = 280
    panel_x = 20
    
    # Berechne verfügbaren Platz für Komponenten
    header_height = 50  # Titel + Linie
    available_height = height - header_height - 20  # Etwas Padding unten
    
    component_labels = {
        0: "Arduino Leonardo",
        1: "Breadboard", 
        2: "LED",
        3: "220 Ohm Resistor",
        4: "Potentiometer",
        5: "Jumper Wires"
    }
    
    # Berechne optimale Zeilenhöhe basierend auf verfügbarem Platz
    num_components = len(component_labels)
    line_height = min(30, available_height // num_components) if num_components > 0 else 30
    
    # Berechne tatsächliche Panel-Höhe basierend auf Inhalt
    actual_panel_height = header_height + (num_components * line_height) + 20
    panel_height = min(actual_panel_height, height)
    
    # Panel-Hintergrund (semi-transparent)
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x - 10, start_y - 10), 
                 (panel_x + panel_width, start_y + panel_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Panel-Rahmen
    cv2.rectangle(frame, (panel_x - 10, start_y - 10), 
                 (panel_x + panel_width, start_y + panel_height), (0, 255, 255), 2)
    
    # Titel
    cv2.putText(frame, "KOMPONENTEN", (panel_x, start_y + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Linie unter Titel
    cv2.line(frame, (panel_x, start_y + 30), (panel_x + panel_width - 20, start_y + 30), 
             (0, 255, 255), 1)
    
    # Komponenten auflisten - kompakte Darstellung
    y_offset = start_y + 45
    
    # Zeige alle verfügbaren Komponenten mit Status
    for comp_id, comp_name in component_labels.items():
        # Prüfe ob wir noch Platz haben
        if y_offset + line_height > start_y + panel_height - 10:
            break
            
        is_detected = comp_id in [comp[0] for comp in detected_components]
        
        # Status-Icon (kleiner)
        icon_y = y_offset - 2
        if is_detected:
            cv2.circle(frame, (panel_x + 8, icon_y), 4, (0, 255, 0), -1)  # Grüner Kreis
            text_color = (0, 255, 0)  # Grüner Text
            status = "●"
        else:
            cv2.circle(frame, (panel_x + 8, icon_y), 4, (100, 100, 100), 1)  # Grauer Kreis
            text_color = (150, 150, 150)  # Grauer Text
            status = "○"
        
        # Kompakte Komponenten-Namen (gekürzt falls nötig)
        display_name = comp_name
        if len(comp_name) > 20:
            display_name = comp_name[:17] + "..."
        
        # Komponenten-Name (kleinere Schrift für kompakte Darstellung)
        cv2.putText(frame, f"{display_name}", (panel_x + 20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        # Anzahl der erkannten Marker dieser Komponente
        count = len([comp for comp in detected_components if comp[0] == comp_id])
        if count > 0:
            cv2.putText(frame, f"({count})", (panel_x + 200, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        y_offset += line_height

def draw_instructions_panel(frame, detected_components, frame_width, start_y, height):
    """Zeichne das rechte Panel mit Schritt-für-Schritt-Anleitung"""
    panel_width = 350
    panel_x = frame_width - panel_width - 20
    
    # Panel-Hintergrund (semi-transparent)
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x - 10, start_y - 10), 
                 (panel_x + panel_width, start_y + height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Panel-Rahmen
    cv2.rectangle(frame, (panel_x - 10, start_y - 10), 
                 (panel_x + panel_width, start_y + height), (255, 165, 0), 2)
    
    # Bestimme aktuellen Schritt basierend auf erkannten Komponenten
    current_step, step_info = get_current_step(detected_components)
    
    # Titel mit Schritt-Nummer
    cv2.putText(frame, f"SCHRITT {current_step}/6", (panel_x, start_y + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
    
    # Linie unter Titel
    cv2.line(frame, (panel_x, start_y + 30), (panel_x + panel_width - 20, start_y + 30), 
             (255, 165, 0), 1)
    
    # Schritt-Titel
    cv2.putText(frame, step_info["title"], (panel_x, start_y + 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Schritt-Beschreibung (mehrzeilig)
    y_offset = start_y + 90
    for line in step_info["description"]:
        cv2.putText(frame, line, (panel_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y_offset += 25
    
    # Benötigte Komponenten
    y_offset += 15
    cv2.putText(frame, "Benötigte Komponenten:", (panel_x, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
    y_offset += 25
    
    for component in step_info["required_components"]:
        is_available = component in [comp[0] for comp in detected_components]
        color = (0, 255, 0) if is_available else (100, 100, 100)
        status = "✓" if is_available else "○"
        
        component_labels = {
            0: "Arduino Leonardo", 1: "Breadboard", 2: "LED",
            3: "220 Ohm Resistor", 4: "Potentiometer", 5: "Jumper Wires"
        }
        comp_name = component_labels.get(component, f"ID: {component}")
        
        cv2.putText(frame, f"{status} {comp_name}", (panel_x + 10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        y_offset += 20
    
    # Fortschrittsbalken
    progress_y = start_y + height - 40
    progress_width = panel_width - 40
    progress_height = 8
    
    # Hintergrund der Fortschrittsleiste
    cv2.rectangle(frame, (panel_x + 10, progress_y), 
                 (panel_x + 10 + progress_width, progress_y + progress_height), 
                 (100, 100, 100), -1)
    
    # Fortschritt
    progress_fill = int((current_step / 6) * progress_width)
    cv2.rectangle(frame, (panel_x + 10, progress_y), 
                 (panel_x + 10 + progress_fill, progress_y + progress_height), 
                 (0, 255, 0), -1)
    
    # Fortschritts-Text
    cv2.putText(frame, f"Fortschritt: {int((current_step/6)*100)}%", 
               (panel_x + 10, progress_y + 25), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

def get_current_step(detected_components):
    """Bestimme den aktuellen Schritt basierend auf erkannten Komponenten"""
    detected_ids = [comp[0] for comp in detected_components]
    
    # Definiere Schritte für ein einfaches LED-Circuit
    steps = {
        1: {
            "title": "Vorbereitung",
            "description": [
                "Sammle alle benötigten Komponenten",
                "Stelle sicher, dass alle Teile",
                "verfügbar sind"
            ],
            "required_components": [0, 1, 2, 3, 5],  # Arduino, Breadboard, LED, Resistor, Wires
            "completion_check": lambda ids: len(set([0, 1, 2, 3, 5]) & set(ids)) >= 3
        },
        2: {
            "title": "Arduino & Breadboard",
            "description": [
                "Platziere Arduino und Breadboard",
                "vor der Kamera",
                "Beide sollten erkannt werden"
            ],
            "required_components": [0, 1],
            "completion_check": lambda ids: 0 in ids and 1 in ids
        },
        3: {
            "title": "LED hinzufügen",
            "description": [
                "Platziere die LED neben den",
                "anderen Komponenten",
                "Achte auf die Polarität"
            ],
            "required_components": [0, 1, 2],
            "completion_check": lambda ids: all(comp in ids for comp in [0, 1, 2])
        },
        4: {
            "title": "Widerstand einsetzen",
            "description": [
                "Füge den 220 Ohm Widerstand",
                "zu den Komponenten hinzu",
                "Er begrenzt den LED-Strom"
            ],
            "required_components": [0, 1, 2, 3],
            "completion_check": lambda ids: all(comp in ids for comp in [0, 1, 2, 3])
        },
        5: {
            "title": "Verkabelung",
            "description": [
                "Verbinde die Komponenten mit",
                "Jumper-Kabeln",
                "Folge dem Schaltplan"
            ],
            "required_components": [0, 1, 2, 3, 5],
            "completion_check": lambda ids: all(comp in ids for comp in [0, 1, 2, 3, 5])
        },
        6: {
            "title": "Test & Fertigstellung",
            "description": [
                "Schaltung ist vollständig!",
                "Teste die LED-Funktion",
                "Herzlichen Glückwunsch!"
            ],
            "required_components": [0, 1, 2, 3, 5],
            "completion_check": lambda ids: all(comp in ids for comp in [0, 1, 2, 3, 5])
        }
    }
    
    # Bestimme aktuellen Schritt
    for step_num in range(1, 7):
        if not steps[step_num]["completion_check"](detected_ids):
            return step_num, steps[step_num]
    
    # Alle Schritte abgeschlossen
    return 6, steps[6]

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

def add_ar_overlays(frame, detected_components, component_labels, tutorial_steps, current_step):
    """Fügt moderne AR-Overlays hinzu: Komponentenliste links, Anweisungen rechts"""
    h, w = frame.shape[:2]
    
    # Erstelle Semi-transparente Overlay-Bereiche
    overlay = frame.copy()
    
    # LINKER OVERLAY - Erkannte Komponenten
    add_components_overlay(overlay, detected_components, component_labels, w, h)
    
    # RECHTER OVERLAY - Schrittweise Anweisungen  
    add_instructions_overlay(overlay, tutorial_steps, current_step, w, h)
    
    # Mische Original und Overlay mit Transparenz
    alpha = 0.85  # Transparenz für Overlay-Bereiche
    result = cv2.addWeighted(frame, alpha, overlay, 1 - alpha, 0)
    
    return result

def add_components_overlay(frame, detected_components, component_labels, w, h):
    """Linker Overlay: Liste der erkannten Komponenten"""
    overlay_width = 280
    overlay_height = h - 40
    
    # Dunkler Hintergrund mit abgerundeten Ecken-Effekt
    cv2.rectangle(frame, (10, 20), (overlay_width, overlay_height), (20, 20, 20), -1)
    cv2.rectangle(frame, (10, 20), (overlay_width, overlay_height), (0, 150, 255), 3)
    
    # Header
    header_text = "ERKANNTE KOMPONENTEN"
    cv2.putText(frame, header_text, (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Linie unter Header
    cv2.line(frame, (20, 60), (overlay_width - 20, 60), (0, 150, 255), 2)
    
    # Komponenten auflisten
    y_offset = 90
    component_count = 0
    
    for component_id in sorted(detected_components):
        if component_id in component_labels:
            component_name = component_labels[component_id]
            component_count += 1
            
            # Status-Icon (grüner Kreis für erkannt)
            cv2.circle(frame, (30, y_offset - 5), 8, (0, 255, 0), -1)
            cv2.circle(frame, (30, y_offset - 5), 8, (255, 255, 255), 2)
            
            # Komponentenname
            cv2.putText(frame, f"{component_name}", (50, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # ID in Klammern
            cv2.putText(frame, f"(ID: {component_id})", (50, y_offset + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
            
            y_offset += 45
    
    # Wenn keine Komponenten erkannt
    if component_count == 0:
        cv2.putText(frame, "Keine Komponenten", (30, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        cv2.putText(frame, "erkannt...", (30, y_offset + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    # Footer mit Gesamtanzahl
    footer_y = overlay_height - 30
    cv2.line(frame, (20, footer_y - 20), (overlay_width - 20, footer_y - 20), (0, 150, 255), 1)
    cv2.putText(frame, f"Gesamt: {component_count}/6", (20, footer_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

def add_instructions_overlay(frame, tutorial_steps, current_step, w, h):
    """Rechter Overlay: Schrittweise Anweisungen"""
    overlay_width = 320
    overlay_x = w - overlay_width - 10
    overlay_height = h - 40
    
    # Dunkler Hintergrund
    cv2.rectangle(frame, (overlay_x, 20), (w - 10, overlay_height), (20, 20, 20), -1)
    cv2.rectangle(frame, (overlay_x, 20), (w - 10, overlay_height), (255, 150, 0), 3)
    
    # Header
    header_text = "AUFBAU-ANLEITUNG"
    cv2.putText(frame, header_text, (overlay_x + 15, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Linie unter Header
    cv2.line(frame, (overlay_x + 15, 60), (w - 25, 60), (255, 150, 0), 2)
    
    # Aktueller Schritt
    if current_step < len(tutorial_steps):
        step = tutorial_steps[current_step]
        y_offset = 100
        
        # Schritt-Titel
        title_lines = step["title"].split()
        for i, line in enumerate(title_lines):
            cv2.putText(frame, line, (overlay_x + 15, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += len(title_lines) * 25 + 15
        
        # Beschreibung
        desc_lines = step["description"].split('\n')
        for line in desc_lines:
            cv2.putText(frame, line, (overlay_x + 15, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y_offset += 22
        
        y_offset += 20
        
        # Fortschritt-Balken
        progress = (current_step + 1) / len(tutorial_steps)
        bar_width = overlay_width - 60
        bar_height = 15
        bar_x = overlay_x + 30
        bar_y = y_offset
        
        # Hintergrund-Balken
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Fortschritt-Balken
        progress_width = int(bar_width * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 100), -1)
        
        # Fortschritt-Text
        cv2.putText(frame, f"Schritt {current_step + 1}/{len(tutorial_steps)}", 
                   (bar_x, bar_y + bar_height + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        y_offset += 60
        
        # Benötigte Komponenten
        cv2.putText(frame, "Benoetigt:", (overlay_x + 15, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)
        y_offset += 25
        
        component_labels_map = {
            0: "Arduino Leonardo",
            1: "Breadboard", 
            2: "LED",
            3: "220 Ohm Resistor",
            4: "Potentiometer",
            5: "Jumper Wires"
        }
        
        for component_id in step["required_components"]:
            name = component_labels_map.get(component_id, f"ID {component_id}")
            # Kürze den Namen wenn nötig
            if len(name) > 18:
                name = name[:15] + "..."
            cv2.putText(frame, f"• {name}", (overlay_x + 25, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
            y_offset += 20

def check_step_progression(detected_components, tutorial_steps, current_step):
    """Überprüft ob zum nächsten Schritt gewechselt werden kann"""
    if current_step >= len(tutorial_steps):
        return current_step
    
    # Überprüfe ob alle benötigten Komponenten für den aktuellen Schritt erkannt wurden
    required = set(tutorial_steps[current_step]["required_components"])
    detected = set(detected_components)
    
    if required.issubset(detected):
        # Alle benötigten Komponenten erkannt - zum nächsten Schritt
        if current_step < len(tutorial_steps) - 1:
            print(f"✓ Schritt {current_step + 1} abgeschlossen! Weiter zu Schritt {current_step + 2}")
            return current_step + 1
        else:
            print("🎉 Alle Schritte abgeschlossen! Aufbau komplett!")
            return current_step
    
    return current_step

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