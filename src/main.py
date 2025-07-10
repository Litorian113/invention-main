import cv2
import numpy as np
import time
from ar_test import ar_main
from ar_modern_ui import ar_main_modern
from ar_textured import ar_main_textured
from PIL import Image, ImageDraw, ImageFont
from camera_utils import get_camera_with_fallback, get_camera_super_fast, get_fresh_frame, get_logitech_camera_optimized

class ModernAROverlay:
    """Moderne AR-Overlay-Klasse mit JavaScript-ähnlichen UI-Effekten"""
    
    def __init__(self):
        self.component_colors = {
            0: (255, 87, 51),   # Arduino - Orange-Rot
            1: (46, 204, 113),  # Breadboard - Grün
            2: (52, 152, 219),  # LED - Blau
            3: (241, 196, 15),  # Resistor - Gelb
            4: (155, 89, 182),  # Potentiometer - Lila
            5: (26, 188, 156)   # Jumper Wires - Türkis
        }
        
        self.component_labels = {
            0: "Arduino",
            1: "Breadboard", 
            2: "LED",
            3: "Resistor",
            4: "Potentiometer",
            5: "Jumper"
        }
        
        # Animation-Zustand
        self.pulse_time = 0
        self.hover_effects = {}
        self.fade_in_progress = {}

    def draw_glassmorphism_box(self, frame, x, y, width, height, color, alpha=0.3):
        """Zeichne eine Glassmorphism-Box ähnlich wie CSS backdrop-filter"""
        overlay = frame.copy()
        
        # Hauptbox mit abgerundeten Ecken (simuliert)
        cv2.rectangle(overlay, (x, y), (x + width, y + height), color, -1)
        
        # Rahmen mit Gradient-Effekt
        border_color = tuple(min(255, c + 50) for c in color)
        cv2.rectangle(overlay, (x, y), (x + width, y + height), border_color, 2)
        
        # Innerer Highlight für Glanz-Effekt
        highlight_color = tuple(min(255, c + 80) for c in color)
        cv2.rectangle(overlay, (x + 2, y + 2), (x + width - 2, y + 8), highlight_color, -1)
        
        # Blend mit Original (Glassmorphism-Effekt)
        cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0, frame)
        
        return frame

    def draw_animated_marker_box(self, frame, corners, marker_id, pulse_intensity=1.0):
        """Zeichne animierte Marker-Box mit CSS-ähnlichen Pulse- und Glow-Effekten"""
        color = self.component_colors.get(marker_id, (255, 255, 255))
        
        # Pulse-Animation (CSS: animation: pulse 2s infinite)
        pulse_scale = 1.0 + 0.15 * np.sin(self.pulse_time * 2.5) * pulse_intensity
        
        # Glow-Effekt Intensität
        glow_intensity = 0.5 + 0.3 * np.sin(self.pulse_time * 3)
        
        # Berechne erweiterte Ecken
        center = np.mean(corners, axis=0)
        vectors = corners - center
        extended_vectors = vectors * pulse_scale * 1.3  # 30% größer + Pulse
        extended_corners = (center + extended_vectors).astype(np.int32)
        
        # Glow-Effekt (mehrere Schichten für Weichheit)
        for glow_level in range(3, 0, -1):
            glow_color = tuple(int(c * glow_intensity * (glow_level / 3)) for c in color)
            thickness = glow_level * 2
            cv2.polylines(frame, [extended_corners], True, glow_color, thickness)
        
        # Hauptbox
        cv2.polylines(frame, [extended_corners], True, color, 3)
        
        # Zeichne Ecken-Punkte mit CSS-ähnlichem Box-Shadow
        for corner in extended_corners:
            # Shadow
            shadow_offset = 2
            cv2.circle(frame, (corner[0] + shadow_offset, corner[1] + shadow_offset), 8, (0, 0, 0), -1)
            # Hauptpunkt
            cv2.circle(frame, tuple(corner), 8, color, -1)
            # Highlight
            cv2.circle(frame, tuple(corner), 12, color, 2)
        
        # Center-Punkt mit radialer Gradient-Simulation
        center_int = center.astype(np.int32)
        for radius in range(10, 4, -1):
            alpha = 1.0 - (radius - 4) / 6.0
            center_color = tuple(int(c * alpha) for c in color)
            cv2.circle(frame, tuple(center_int), radius, center_color, -1)
        
        return extended_corners

    def draw_modern_label(self, frame, text, position, marker_id, background_alpha=0.85):
        """Zeichne modernes Label mit CSS-ähnlichen Eigenschaften (gradient, shadow, etc.)"""
        x, y = position
        color = self.component_colors.get(marker_id, (255, 255, 255))
        
        # Text-Dimensionen (VERGRÖSSERT für bessere Lesbarkeit)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0    # Erhöht von 0.7
        thickness = 3       # Erhöht von 2
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Label-Dimensionen (angepasst für größeren Text)
        padding = 20        # Erhöht von 15
        border_radius = 8   # Simuliert border-radius
        label_width = text_width + padding * 2
        label_height = text_height + padding * 2
        
        # Drop Shadow (CSS: box-shadow)
        shadow_offset = 3
        shadow_color = (0, 0, 0)
        cv2.rectangle(frame, 
                     (x + shadow_offset, y + shadow_offset), 
                     (x + label_width + shadow_offset, y + label_height + shadow_offset), 
                     shadow_color, -1)
        
        # Gradient Background (CSS: linear-gradient)
        overlay = frame.copy()
        
        # Haupt-Gradient (von dunkel zu hell)
        for i in range(label_height):
            gradient_ratio = i / label_height
            bg_color = tuple(int(c * (0.2 + 0.3 * gradient_ratio)) for c in color)
            cv2.line(overlay, (x, y + i), (x + label_width, y + i), bg_color, 1)
        
        # Oberer Highlight-Streifen (CSS: linear-gradient top highlight)
        highlight_height = 6
        highlight_color = tuple(min(255, int(c * 0.8)) for c in color)
        cv2.rectangle(overlay, (x, y), (x + label_width, y + highlight_height), highlight_color, -1)
        
        # Border (CSS: border)
        cv2.rectangle(overlay, (x, y), (x + label_width, y + label_height), color, 2)
        
        # Blend (CSS: opacity)
        cv2.addWeighted(frame, 1 - background_alpha, overlay, background_alpha, 0, frame)
        
        # Text mit Text-Shadow
        text_x = x + padding
        text_y = y + padding + text_height
        
        # Text Shadow
        cv2.putText(frame, text, (text_x + 1, text_y + 1), font, font_scale, (0, 0, 0), thickness + 1)
        # Haupt-Text
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        
        return frame

    def draw_info_badge(self, frame, text, position, badge_type="info", animated=True):
        """Zeichne Info-Badge mit CSS-ähnlichen Hover- und Animation-Effekten"""
        x, y = position
        
        badge_colors = {
            "info": (52, 152, 219),    # Blau
            "success": (46, 204, 113), # Grün
            "warning": (241, 196, 15), # Gelb
            "error": (231, 76, 60)     # Rot
        }
        
        base_color = badge_colors.get(badge_type, badge_colors["info"])
        
        # Animation-Effekt
        if animated:
            scale_factor = 1.0 + 0.1 * np.sin(self.pulse_time * 4)
            color = tuple(int(c * (0.8 + 0.2 * scale_factor)) for c in base_color)
        else:
            color = base_color
        
        # Text-Dimensionen (VERGRÖSSERT für bessere Lesbarkeit)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7     # Erhöht von 0.5
        thickness = 2        # Erhöht von 1
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Badge-Dimensionen (größer)
        padding = 12         # Erhöht von 8
        badge_width = text_width + padding * 2
        badge_height = text_height + padding * 2
        
        # CSS-ähnlicher Box-Shadow
        shadow_offset = 2
        cv2.rectangle(frame, 
                     (x + shadow_offset, y + shadow_offset), 
                     (x + badge_width + shadow_offset, y + badge_height + shadow_offset), 
                     (0, 0, 0), -1)
        
        # Badge mit Gradient
        overlay = frame.copy()
        
        # Gradient von oben nach unten
        for i in range(badge_height):
            ratio = i / badge_height
            gradient_color = tuple(int(c * (1.0 - 0.3 * ratio)) for c in color)
            cv2.line(overlay, (x, y + i), (x + badge_width, y + i), gradient_color, 1)
        
        # Border
        cv2.rectangle(overlay, (x, y), (x + badge_width, y + badge_height), (255, 255, 255), 1)
        
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        # Text
        text_x = x + padding
        text_y = y + padding + text_height
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

    def draw_connection_lines(self, frame, markers):
        """Zeichne animierte Verbindungslinien mit CSS-ähnlichen Effekten"""
        arduino_marker = None
        other_markers = []
        
        for marker in markers:
            if marker[0] == 0:  # Arduino
                arduino_marker = marker
            else:
                other_markers.append(marker)
        
        if arduino_marker and len(other_markers) > 0:
            arduino_center = (arduino_marker[1], arduino_marker[2])
            
            for marker in other_markers:
                other_center = (marker[1], marker[2])
                
                # Animierte Farbe für Datenfluss-Simulation
                flow_color = tuple(int(100 + 100 * np.sin(self.pulse_time * 2 + marker[0])) for _ in range(3))
                
                # Zeichne animierte gestrichelte Linie
                self.draw_animated_dashed_line(frame, arduino_center, other_center, 
                                             flow_color, thickness=2, dash_length=15)

    def draw_animated_dashed_line(self, frame, pt1, pt2, color, thickness=1, dash_length=10):
        """Zeichne animierte gestrichelte Linie (CSS: border-style: dashed + animation)"""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Animation-Offset für bewegte Striche
        animation_offset = int(self.pulse_time * 20) % (dash_length * 2)
        
        # Berechne Linienlänge und -richtung
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        unit_x = (x2 - x1) / length
        unit_y = (y2 - y1) / length
        
        # Zeichne animierte Striche
        current_length = -animation_offset
        draw_dash = True
        
        while current_length < length:
            next_length = current_length + dash_length
            
            if current_length >= 0 and draw_dash:
                start_x = int(x1 + max(0, current_length) * unit_x)
                start_y = int(y1 + max(0, current_length) * unit_y)
                end_x = int(x1 + min(length, next_length) * unit_x)
                end_y = int(y1 + min(length, next_length) * unit_y)
                
                if start_x != end_x or start_y != end_y:
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)
            
            current_length = next_length
            draw_dash = not draw_dash

    def draw_floating_particles(self, frame, markers):
        """Zeichne schwebende Partikel um Marker (CSS-ähnlicher particle effect)"""
        for marker_id, center_x, center_y, corners_2d in markers:
            color = self.component_colors.get(marker_id, (255, 255, 255))
            
            # Erstelle 5-8 Partikel um jeden Marker
            num_particles = 6
            for i in range(num_particles):
                # Kreisförmige Bewegung um Marker
                angle = (i / num_particles) * 2 * np.pi + self.pulse_time
                radius = 40 + 10 * np.sin(self.pulse_time * 2 + i)
                
                particle_x = int(center_x + radius * np.cos(angle))
                particle_y = int(center_y + radius * np.sin(angle))
                
                # Partikel-Größe und Transparenz basierend auf Zeit
                size = int(3 + 2 * np.sin(self.pulse_time * 3 + i))
                alpha = 0.3 + 0.4 * np.sin(self.pulse_time * 2 + i)
                
                # Zeichne Partikel mit Glow
                particle_color = tuple(int(c * alpha) for c in color)
                cv2.circle(frame, (particle_x, particle_y), size, particle_color, -1)

    def update_animations(self, delta_time):
        """Update Animation-Zustand (ähnlich wie JavaScript requestAnimationFrame)"""
        self.pulse_time += delta_time * 2  # 2x Geschwindigkeit

    def render_modern_ui(self, frame, markers, show_particles=True, show_connections=True):
        """Hauptfunktion für modernes UI-Rendering mit allen CSS-ähnlichen Effekten"""
        self.update_animations(0.016)  # ~60 FPS
        
        # Schwebende Partikel (optional)
        if show_particles and len(markers) > 0:
            self.draw_floating_particles(frame, markers)
        
        # Verbindungslinien (optional)
        if show_connections and len(markers) > 1:
            self.draw_connection_lines(frame, markers)
        
        # Zeichne jeden Marker mit modernen Effekten
        for marker_id, center_x, center_y, corners_2d in markers:
            # Animierte Marker-Box mit Glow
            extended_corners = self.draw_animated_marker_box(
                frame, corners_2d, marker_id, pulse_intensity=0.8
            )
            
            # Modernes Label unterhalb
            component_name = self.component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
            label_x = center_x - 60  # Ungefähr zentriert
            label_y = np.max(extended_corners[:, 1]) + 20
            
            # Boundary-Check für Label
            h, w = frame.shape[:2]
            if label_y > h - 50:
                label_y = np.min(extended_corners[:, 1]) - 50
            label_x = max(10, min(label_x, w - 140))
            
            self.draw_modern_label(frame, component_name, (label_x, label_y), marker_id)
            
            # ID-Badge oben links (animiert)
            id_text = f"#{marker_id}"
            badge_x = np.min(extended_corners[:, 0]) - 5
            badge_y = np.min(extended_corners[:, 1]) - 30
            self.draw_info_badge(frame, id_text, (badge_x, badge_y), "info", animated=True)
            
            # Koordinaten-Badge unten rechts
            coord_text = f"{center_x},{center_y}"
            coord_x = np.max(extended_corners[:, 0]) - 70
            coord_y = np.max(extended_corners[:, 1]) + 5
            self.draw_info_badge(frame, coord_text, (coord_x, coord_y), "success", animated=False)

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
            
            # Label-Text in Box-Farbe (VERGRÖSSERT für bessere Lesbarkeit)
            cv2.putText(frame, label_text, (label_x, label_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
            
            # Marker-ID in der oberen linken Ecke der perspektivischen Box (VERGRÖSSERT)
            id_text = f"#{marker_id}"
            id_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Position an der oberen linken Ecke der erweiterten Box
            box_top_left = extended_corners[np.argmin(extended_corners[:, 0] + extended_corners[:, 1])]
            id_bg_x1 = box_top_left[0] - 5
            id_bg_y1 = box_top_left[1] - 5
            id_bg_x2 = id_bg_x1 + id_size[0] + 10
            id_bg_y2 = id_bg_y1 + id_size[1] + 10
            
            # ID-Hintergrund in Box-Farbe
            cv2.rectangle(frame, (id_bg_x1, id_bg_y1), (id_bg_x2, id_bg_y2), box_color, -1)
            cv2.putText(frame, id_text, (id_bg_x1 + 5, id_bg_y1 + id_size[1] + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # Vergrößerter Text
            
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
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)  # Vergrößerter Text
        
        # FPS-Anzeige (alle 30 Frames aktualisieren)
        if fps_count >= 30:
            elapsed = time.time() - fps_start
            current_fps = 30 / elapsed if elapsed > 0 else 0
            fps_start = time.time()
            fps_count = 0
        
        # FPS-Display (VERGRÖSSERT)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Markers: {len(cached_markers)}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the frame
        # Erstelle Fenster im Vollbild-Modus
        window_name = 'ArUco Marker Detection - Optimized'
        cv2.imshow(window_name, frame)
        
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

def basic_marker_detection_modern():
    """🎨 Moderne ArUco Marker Detection mit CSS-ähnlichen UI-Effekten"""
    print("🎨 Modern ArUco Marker Detection with Enhanced UI")
    print("Features: Glassmorphism, Animations, Particle Effects, Gradient Labels")
    print("Controls: 'q' = quit, 'p' = toggle particles, 'c' = toggle connections, 's' = screenshot")
    
    # Use Logitech-optimized camera initialization
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("Error: Could not initialize any camera")
        return
    
    # Load the predefined dictionary for ArUco markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # Optimierte Parameter für bessere Erkennung
    aruco_params.adaptiveThreshWinSizeMin = 3
    aruco_params.adaptiveThreshWinSizeMax = 23
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.03
    aruco_params.maxMarkerPerimeterRate = 4.0
    aruco_params.polygonalApproxAccuracyRate = 0.05
    aruco_params.minCornerDistanceRate = 0.05
    aruco_params.minDistanceToBorder = 3
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Erstelle moderne UI-Instanz
    modern_ui = ModernAROverlay()
    
    # Performance-Optimierung
    detection_size = 960
    detect_every = 1
    frame_count = 0
    cached_markers = []
    
    # UI-Kontrollen
    show_particles = True
    show_connections = True
    
    # FPS-Tracking
    fps_count = 0
    fps_start = time.time()
    current_fps = 0
    
    # Screenshot-Zähler
    screenshot_count = 0
    
    print("✨ Moderne UI aktiviert - Bereit für AR Magic!")
    
    while True:
        # Capture frame-by-frame
        ret, frame = get_fresh_frame(cap)
        
        if not ret or frame is None:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: Failed to grab frame")
                break
        
        # Validate frame dimensions
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            continue
        
        frame_count += 1
        fps_count += 1
        h, w = frame.shape[:2]
        
        # ArUco Detection (adaptive)
        if frame_count % detect_every == 0:
            scale = min(detection_size / max(w, h), 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            
            if scale < 1.0:
                small_frame = cv2.resize(frame, (new_w, new_h))
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ArUco Detection
            corners, ids, _ = detector.detectMarkers(gray)
            
            # Cache Marker-Daten
            cached_markers = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    if scale < 1.0:
                        scaled_corner = corner / scale
                        center_x = int(np.mean(scaled_corner[0][:, 0]))
                        center_y = int(np.mean(scaled_corner[0][:, 1]))
                        corners_2d = scaled_corner[0].astype(np.int32)
                    else:
                        center_x = int(np.mean(corner[0][:, 0]))
                        center_y = int(np.mean(corner[0][:, 1]))
                        corners_2d = corner[0].astype(np.int32)
                    cached_markers.append((marker_id, center_x, center_y, corners_2d))
        
        # 🎨 MODERNE UI RENDERING
        if len(cached_markers) > 0:
            modern_ui.render_modern_ui(frame, cached_markers, 
                                     show_particles=show_particles, 
                                     show_connections=show_connections)
        
        # FPS-Berechnung und moderne Anzeige
        if fps_count >= 30:
            elapsed = time.time() - fps_start
            current_fps = 30 / elapsed if elapsed > 0 else 0
            fps_start = time.time()
            fps_count = 0
        
        # 🎯 MODERNE STATUS-ANZEIGE (oben links)
        status_overlay = frame.copy()
        
        # Glassmorphism-Hintergrund für Status
        modern_ui.draw_glassmorphism_box(status_overlay, 10, 10, 250, 80, (20, 20, 20), alpha=0.7)
        
        # Status-Text mit modernen Farben (VERGRÖSSERT)
        status_color = (0, 255, 150)  # Neon-Grün
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, f"Markers: {len(cached_markers)}", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Mode: Modern UI", (20, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
        
        # 🎮 CONTROLS-ANZEIGE (unten rechts)
        controls = [
            "Q: Quit", 
            "P: Particles", 
            "C: Connections", 
            "S: Screenshot"
        ]
        
        for i, control in enumerate(controls):
            y_pos = h - 90 + i * 20
            cv2.putText(frame, control, (w - 150, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)  # Vergrößerte Kontroll-Anzeige
        
        # Display the frame
        # Erstelle Fenster im Vollbild-Modus  
        window_name = 'Modern ArUco Detection - Enhanced UI'
        cv2.imshow(window_name, frame)
        
        # Handle key presses for UI controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            show_particles = not show_particles
            print(f"🎆 Particles: {'ON' if show_particles else 'OFF'}")
        elif key == ord('c'):
            show_connections = not show_connections
            print(f"🔗 Connections: {'ON' if show_connections else 'OFF'}")
        elif key == ord('s'):
            screenshot_count += 1
            filename = f"modern_ar_screenshot_{screenshot_count:03d}.png"
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
    
    # Release everything
    cap.release()
    cv2.destroyAllWindows()
    print("🎨 Modern UI Application closed")

def main():
    print("=== ArUco Marker Detection & AR Application ===")
    print("Choose an option:")
    print("1. Basic ArUco Marker Detection")
    print("2. 🎨 Modern UI Detection (CSS-like Effects)")
    print("3. AR 3D Visualization (Enhanced OpenCV)")
    print("4. AR Clean UI (Black Text, Custom Fonts)")
    print("5. AR Textured Model (UV Mapped Breadboard)")
    print("6. 🎓 Arduino Tutorial System (Step-by-Step)")
    print("7. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                print("\nStarting Basic ArUco Marker Detection...")
                basic_marker_detection()
                break
            elif choice == "2":
                print("\n🎨 Starting Modern UI Detection with CSS-like Effects...")
                basic_marker_detection_modern()
                break
            elif choice == "3":
                print("\nStarting AR 3D Visualization...")
                ar_main()
                break
            elif choice == "4":
                print("\nStarting Clean AR with Black Text...")
                ar_main_modern()
                break
            elif choice == "5":
                print("\nStarting Textured AR with UV Mapping...")
                ar_main_textured()
                break
            elif choice == "6":
                print("\n🎓 Starting Arduino Tutorial System (Step-by-Step Guide)...")
                from arduino_tutorial import tutorial_mode_main
                tutorial_mode_main()
                break
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()