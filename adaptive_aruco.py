#!/usr/bin/env python3
"""
Adaptive ArUco Detection - Beste Balance zwischen Qualität und Performance
"""
import cv2
import numpy as np
import time
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera_utils import get_logitech_camera_optimized

def adaptive_aruco_detection():
    """Adaptive ArUco-Erkennung mit automatischer Qualitäts-/Performance-Balance"""
    print("🎯 Adaptive ArUco Detection - Auto-Balance")
    print("Drücke 'q' zum Beenden")
    print("Drücke 'h' für High-Quality Mode")
    print("Drücke 'f' für Fast Mode")
    print("Drücke 'a' für Auto Mode")
    
    # Kamera initialisieren
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("❌ Kamera-Fehler")
        return
    
    # ArUco-Setup mit ausgewogenen Parametern
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # OPTIMALE PARAMETER für gute Erkennung + Performance
    aruco_params.adaptiveThreshWinSizeMin = 3
    aruco_params.adaptiveThreshWinSizeMax = 23
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.03
    aruco_params.maxMarkerPerimeterRate = 4.0
    aruco_params.polygonalApproxAccuracyRate = 0.05
    aruco_params.minCornerDistanceRate = 0.05
    aruco_params.minDistanceToBorder = 3
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Labels
    component_labels = {
        0: "Arduino Leonardo",
        1: "Breadboard", 
        2: "LED",
        3: "220Ω Resistor",
        4: "Potentiometer",
        5: "Jumper Wires"
    }
    
    # Adaptive Performance-Variablen
    modes = {
        'auto': {'detection_size': 800, 'skip_frames': 1, 'name': 'Auto'},
        'high_quality': {'detection_size': 1280, 'skip_frames': 1, 'name': 'High Quality'},
        'fast': {'detection_size': 640, 'skip_frames': 2, 'name': 'Fast'}
    }
    
    current_mode = 'auto'
    frame_count = 0
    cached_markers = []
    
    # Performance-Tracking für automatische Anpassung
    fps_samples = []
    detection_history = []
    
    # FPS-Messung
    fps_count = 0
    fps_start = time.time()
    current_fps = 0
    target_fps = 20  # Ziel-FPS für adaptive Anpassung
    
    print(f"🚀 Starting in {modes[current_mode]['name']} mode...")
    
    while True:
        frame_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        fps_count += 1
        h, w = frame.shape[:2]
        
        # Aktuelle Mode-Parameter
        mode_config = modes[current_mode]
        detection_size = mode_config['detection_size']
        skip_frames = mode_config['skip_frames']
        
        # ADAPTIVE DETECTION: Erkenne basierend auf Mode
        if frame_count % skip_frames == 0:
            # Skaliere Frame für Detection
            scale = detection_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            small_frame = cv2.resize(frame, (new_w, new_h))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            # ArUco Detection
            detection_start = time.time()
            corners, ids, _ = detector.detectMarkers(gray)
            detection_time = time.time() - detection_start
            
            # Sammle Performance-Daten
            detection_history.append(detection_time)
            if len(detection_history) > 10:
                detection_history.pop(0)
            
            # Cache Marker-Daten (skaliert zurück)
            cached_markers = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    # Skaliere Koordinaten zurück
                    scaled_corner = corner / scale
                    center_x = int(np.mean(scaled_corner[0][:, 0]))
                    center_y = int(np.mean(scaled_corner[0][:, 1]))
                    
                    # Berechne Marker-Größe für Qualitätsbewertung
                    marker_area = cv2.contourArea(scaled_corner[0])
                    cached_markers.append((marker_id, center_x, center_y, marker_area))
        
        # Rendere Marker (immer, für flüssige Anzeige)
        markers_detected = len(cached_markers)
        for marker_id, center_x, center_y, area in cached_markers:
            component_name = component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
            
            # Adaptive Darstellung basierend auf Marker-Größe
            if area > 1000:  # Großer Marker
                circle_size = 8
                font_scale = 0.8
                thickness = 2
            else:  # Kleiner Marker
                circle_size = 5
                font_scale = 0.6
                thickness = 1
            
            # Marker-Center
            cv2.circle(frame, (center_x, center_y), circle_size, (0, 0, 255), -1)
            cv2.circle(frame, (center_x, center_y), circle_size + 3, (0, 255, 255), 2)
            
            # Component-Label mit adaptiver Größe
            text_size = cv2.getTextSize(component_name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = center_x - text_size[0] // 2
            text_y = center_y + 35
            
            # Schwarzer Hintergrund
            cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5), 
                         (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
            
            # Gelber Text
            cv2.putText(frame, component_name, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness)
            
            # Marker-ID (kompakt)
            cv2.putText(frame, f"ID:{marker_id}", (center_x - 20, center_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # FPS-Berechnung
        frame_time = time.time() - frame_start
        if fps_count >= 30:
            elapsed = time.time() - fps_start
            current_fps = 30 / elapsed if elapsed > 0 else 0
            fps_samples.append(current_fps)
            if len(fps_samples) > 5:
                fps_samples.pop(0)
            fps_start = time.time()
            fps_count = 0
        
        # AUTOMATISCHE MODE-ANPASSUNG
        if current_mode == 'auto' and len(fps_samples) >= 3:
            avg_fps = sum(fps_samples) / len(fps_samples)
            avg_detection_time = sum(detection_history) / len(detection_history) if detection_history else 0
            
            # Wechsle zu Fast Mode wenn FPS zu niedrig
            if avg_fps < target_fps * 0.8 and avg_detection_time > 0.02:
                current_mode = 'fast'
                print("🔄 Switched to Fast Mode (FPS too low)")
            # Wechsle zu High Quality wenn Performance gut ist
            elif avg_fps > target_fps * 1.2 and markers_detected > 0:
                current_mode = 'high_quality'
                print("🔄 Switched to High Quality Mode (good performance)")
        
        # Status-Anzeige
        status_color = (0, 255, 0) if current_fps >= target_fps else (0, 165, 255)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        cv2.putText(frame, f"Mode: {modes[current_mode]['name']}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Markers: {markers_detected}", (10, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Zeige Detection-Bereich (falls reduziert)
        if detection_size < max(w, h):
            scale = detection_size / max(w, h)
            rect_w, rect_h = int(w * scale), int(h * scale)
            start_x, start_y = (w - rect_w) // 2, (h - rect_h) // 2
            cv2.rectangle(frame, (start_x, start_y), (start_x + rect_w, start_y + rect_h), (255, 0, 0), 2)
            cv2.putText(frame, "Detection Area", (start_x + 5, start_y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Display
        cv2.imshow('Adaptive ArUco Detection', frame)
        
        # Input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('h'):
            current_mode = 'high_quality'
            print("🎯 Switched to High Quality Mode")
        elif key == ord('f'):
            current_mode = 'fast'
            print("⚡ Switched to Fast Mode")
        elif key == ord('a'):
            current_mode = 'auto'
            print("🤖 Switched to Auto Mode")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("🎯 Adaptive detection ended")

if __name__ == "__main__":
    adaptive_aruco_detection()
