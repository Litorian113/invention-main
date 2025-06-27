#!/usr/bin/env python3
"""
Performance-optimierte ArUco-Marker-Erkennung für flüssigen Video-Feed
"""
import cv2
import numpy as np
import time
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera_utils import get_logitech_camera_optimized

def optimized_marker_detection():
    """Optimierte ArUco-Marker-Erkennung ohne Lag"""
    print("🚀 Performance-Optimierte ArUco Marker Detection")
    print("Drücke 'q' zum Beenden")
    print("Drücke 'i' um Marker-Info ein/auszublenden")
    print("Drücke 'f' um FPS-Anzeige ein/auszublenden")
    
    # Logitech-Kamera initialisieren
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("❌ Fehler: Kamera konnte nicht initialisiert werden")
        return
    
    # ArUco-Setup
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # Performance-Optimierung: Reduziere Erkennungsgenauigkeit für Speed
    aruco_params.adaptiveThreshWinSizeMin = 5
    aruco_params.adaptiveThreshWinSizeMax = 15
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.05
    aruco_params.maxMarkerPerimeterRate = 0.5
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Komponenten-Labels (vereinfacht)
    component_labels = {
        0: "Arduino", 1: "Breadboard", 2: "LED", 3: "Resistor",
        4: "Potentiometer", 5: "Jumper Wires"
    }
    
    # Performance-Tracking
    frame_count = 0
    fps_start_time = time.time()
    show_info = True
    show_fps = True
    
    # Frame-Größe reduzieren für bessere Performance
    detection_scale = 0.5  # Erkenne auf halber Auflösung
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        
        frame_count += 1
        start_frame_time = time.time()
        
        # PERFORMANCE-TRICK 1: Kleineres Frame für Detektion
        height, width = frame.shape[:2]
        small_frame = cv2.resize(frame, (int(width * detection_scale), int(height * detection_scale)))
        gray_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # ArUco-Erkennung auf kleinerem Frame
        corners, ids, _ = detector.detectMarkers(gray_small)
        
        # Skaliere Koordinaten zurück auf Original-Frame
        if ids is not None and len(corners) > 0:
            # Skaliere Corners zurück
            scaled_corners = []
            for corner in corners:
                scaled_corner = corner * (1.0 / detection_scale)
                scaled_corners.append(scaled_corner)
            
            # PERFORMANCE-TRICK 2: Verwende OpenCV statt PIL für Text
            cv2.aruco.drawDetectedMarkers(frame, scaled_corners, ids)
            
            if show_info:
                for i, corner in enumerate(scaled_corners):
                    marker_id = ids[i][0]
                    
                    # Berechne Center (schnell)
                    center_x = int(np.mean(corner[0][:, 0]))
                    center_y = int(np.mean(corner[0][:, 1]))
                    
                    # Komponenten-Name
                    component_name = component_labels.get(marker_id, f"ID:{marker_id}")
                    
                    # PERFORMANCE-TRICK 3: Einfache OpenCV-Text-Anzeige
                    # Hintergrund für bessere Lesbarkeit
                    text_size = cv2.getTextSize(component_name, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    text_x = center_x - text_size[0] // 2
                    text_y = center_y + 40
                    
                    # Schwarzer Hintergrund für Text
                    cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5), 
                                (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
                    
                    # Gelber Text
                    cv2.putText(frame, component_name, (text_x, text_y), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Center-Punkt
                    cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), -1)
        
        # FPS-Anzeige
        if show_fps and frame_count % 10 == 0:  # Update alle 10 Frames
            current_time = time.time()
            elapsed = current_time - fps_start_time
            if elapsed > 0:
                fps = 10 / elapsed
                fps_start_time = current_time
                
                # FPS-Text mit Hintergrund
                fps_text = f"FPS: {fps:.1f}"
                cv2.rectangle(frame, (10, 10), (150, 40), (0, 0, 0), -1)
                cv2.putText(frame, fps_text, (15, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Frame-Zeit anzeigen
        frame_time = (time.time() - start_frame_time) * 1000
        if show_fps:
            time_text = f"Frame: {frame_time:.1f}ms"
            cv2.rectangle(frame, (10, 45), (200, 75), (0, 0, 0), -1)
            cv2.putText(frame, time_text, (15, 65), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Frame anzeigen
        cv2.imshow('Optimized ArUco Detection', frame)
        
        # Tastatur-Input (nicht-blockierend)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('i'):
            show_info = not show_info
            print(f"📋 Marker-Info: {'Ein' if show_info else 'Aus'}")
        elif key == ord('f'):
            show_fps = not show_fps
            print(f"📊 FPS-Anzeige: {'Ein' if show_fps else 'Aus'}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Optimierte Erkennung beendet")

if __name__ == "__main__":
    print("Performance-Optimierte ArUco-Erkennung")
    print("=" * 50)
    optimized_marker_detection()
