#!/usr/bin/env python3
"""
Ultra-Performance ArUco Detection - Kein Lag mehr!
"""
import cv2
import numpy as np
import time
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera_utils import get_logitech_camera_optimized

def ultra_fast_aruco():
    """Ultra-schnelle ArUco-Erkennung ohne jegliches Lag"""
    print("⚡ ULTRA-FAST ArUco Detection - Zero Lag!")
    print("Drücke 'q' zum Beenden, 'SPACE' für Debug-Info")
    
    # Kamera initialisieren
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("❌ Kamera-Fehler")
        return
    
    # ArUco-Setup (minimal für maximale Performance)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # ULTRA-PERFORMANCE-SETTINGS
    aruco_params.adaptiveThreshWinSizeMin = 7
    aruco_params.adaptiveThreshWinSizeMax = 13
    aruco_params.adaptiveThreshWinSizeStep = 5
    aruco_params.minMarkerPerimeterRate = 0.1
    aruco_params.maxMarkerPerimeterRate = 0.3
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Labels (ultra-kurz)
    labels = {0: "ARD", 1: "BRD", 2: "LED", 3: "RES", 4: "POT", 5: "JMP"}
    
    # Performance-Variablen
    detection_size = 480  # Feste kleine Größe für Detection
    detect_every = 3      # Erkenne nur jeden 3. Frame
    frame_count = 0
    cached_data = []
    
    # FPS-Messung
    fps_count = 0
    fps_start = time.time()
    current_fps = 0
    
    print("🚀 Starting ultra-fast detection...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        fps_count += 1
        
        # TRICK 1: Erkenne nicht jeden Frame
        if frame_count % detect_every == 0:
            # TRICK 2: Extrem kleine Detection-Größe
            h, w = frame.shape[:2]
            scale = detection_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            small = cv2.resize(frame, (new_w, new_h))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            
            # Detection
            corners, ids, _ = detector.detectMarkers(gray)
            
            # Cache Results (skaliert zurück)
            cached_data = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    # Skaliere zurück zum Original
                    scaled_corner = corner / scale
                    cx = int(np.mean(scaled_corner[0][:, 0]))
                    cy = int(np.mean(scaled_corner[0][:, 1]))
                    cached_data.append((marker_id, cx, cy))
        
        # TRICK 3: Verwende cached Daten für Rendering
        for marker_id, cx, cy in cached_data:
            label = labels.get(marker_id, f"{marker_id}")
            
            # Minimales Rendering - nur Circle und Text
            cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)  # Gelber Punkt
            cv2.circle(frame, (cx, cy), 12, (0, 0, 255), 2)    # Roter Ring
            
            # Text (ohne Hintergrund für Speed)
            cv2.putText(frame, label, (cx - 20, cy - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # FPS-Anzeige (alle 30 Frames)
        if fps_count >= 30:
            elapsed = time.time() - fps_start
            current_fps = 30 / elapsed if elapsed > 0 else 0
            fps_start = time.time()
            fps_count = 0
        
        # FPS-Text (minimal)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Markers: {len(cached_data)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Display (mit minimal delay)
        cv2.imshow('ULTRA-FAST ArUco', frame)
        
        # Input check (non-blocking)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            print(f"📊 Current: {current_fps:.1f} FPS, {len(cached_data)} markers")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("⚡ Ultra-fast detection ended")

if __name__ == "__main__":
    ultra_fast_aruco()
