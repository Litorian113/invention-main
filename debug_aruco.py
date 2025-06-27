#!/usr/bin/env python3
"""
ArUco Detection Quality Test - Debug-Version
"""
import cv2
import numpy as np
import time
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera_utils import get_logitech_camera_optimized

def debug_aruco_quality():
    """Debug-Version zum Testen der Erkennungsqualität"""
    print("🔍 ArUco Quality Debug Tool")
    print("Drücke 'q' zum Beenden")
    print("Drücke '1' für Original Settings (beste Qualität)")
    print("Drücke '2' für Balanced Settings")
    print("Drücke '3' für Fast Settings")
    print("Drücke 's' für Screenshot mit Debug-Info")
    
    # Kamera initialisieren
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("❌ Kamera-Fehler")
        return
    
    # ArUco-Dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    
    # Verschiedene Parameter-Sets
    param_sets = {
        1: {
            'name': 'Original (Best Quality)',
            'adaptiveThreshWinSizeMin': 3,
            'adaptiveThreshWinSizeMax': 23,
            'adaptiveThreshWinSizeStep': 10,
            'minMarkerPerimeterRate': 0.03,
            'maxMarkerPerimeterRate': 4.0,
            'polygonalApproxAccuracyRate': 0.03,
            'minCornerDistanceRate': 0.05,
            'minDistanceToBorder': 3,
            'detection_size': None  # Full resolution
        },
        2: {
            'name': 'Balanced',
            'adaptiveThreshWinSizeMin': 3,
            'adaptiveThreshWinSizeMax': 23,
            'adaptiveThreshWinSizeStep': 4,
            'minMarkerPerimeterRate': 0.03,
            'maxMarkerPerimeterRate': 4.0,
            'polygonalApproxAccuracyRate': 0.05,
            'minCornerDistanceRate': 0.05,
            'minDistanceToBorder': 3,
            'detection_size': 960
        },
        3: {
            'name': 'Fast',
            'adaptiveThreshWinSizeMin': 7,
            'adaptiveThreshWinSizeMax': 13,
            'adaptiveThreshWinSizeStep': 5,
            'minMarkerPerimeterRate': 0.1,
            'maxMarkerPerimeterRate': 0.3,
            'polygonalApproxAccuracyRate': 0.1,
            'minCornerDistanceRate': 0.1,
            'minDistanceToBorder': 3,
            'detection_size': 640
        }
    }
    
    current_set = 1
    
    def create_detector(param_set):
        params = cv2.aruco.DetectorParameters()
        params.adaptiveThreshWinSizeMin = param_set['adaptiveThreshWinSizeMin']
        params.adaptiveThreshWinSizeMax = param_set['adaptiveThreshWinSizeMax']
        params.adaptiveThreshWinSizeStep = param_set['adaptiveThreshWinSizeStep']
        params.minMarkerPerimeterRate = param_set['minMarkerPerimeterRate']
        params.maxMarkerPerimeterRate = param_set['maxMarkerPerimeterRate']
        params.polygonalApproxAccuracyRate = param_set['polygonalApproxAccuracyRate']
        params.minCornerDistanceRate = param_set['minCornerDistanceRate']
        params.minDistanceToBorder = param_set['minDistanceToBorder']
        return cv2.aruco.ArucoDetector(aruco_dict, params)
    
    detector = create_detector(param_sets[current_set])
    
    # Labels
    component_labels = {
        0: "Arduino Leonardo", 1: "Breadboard", 2: "LED",
        3: "220Ω Resistor", 4: "Potentiometer", 5: "Jumper Wires"
    }
    
    # Performance-Tracking
    detection_times = []
    detection_counts = []
    frame_count = 0
    screenshot_count = 0
    
    print(f"🚀 Starting with {param_sets[current_set]['name']} settings")
    
    while True:
        frame_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        h, w = frame.shape[:2]
        
        # Bereite Frame für Detection vor
        detection_size = param_sets[current_set]['detection_size']
        
        if detection_size is None:
            # Full resolution
            detection_frame = frame
            scale = 1.0
        else:
            # Reduzierte Auflösung
            scale = detection_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            detection_frame = cv2.resize(frame, (new_w, new_h))
        
        gray = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2GRAY)
        
        # ArUco Detection mit Zeitmessung
        detection_start = time.time()
        corners, ids, rejected = detector.detectMarkers(gray)
        detection_time = time.time() - detection_start
        
        detection_times.append(detection_time * 1000)  # in ms
        if len(detection_times) > 30:
            detection_times.pop(0)
        
        markers_detected = len(ids) if ids is not None else 0
        detection_counts.append(markers_detected)
        if len(detection_counts) > 30:
            detection_counts.pop(0)
        
        # Zeige Ergebnisse
        if ids is not None:
            for i, corner in enumerate(corners):
                marker_id = ids[i][0]
                
                # Skaliere Koordinaten zurück
                if scale != 1.0:
                    scaled_corner = corner / scale
                else:
                    scaled_corner = corner
                
                center_x = int(np.mean(scaled_corner[0][:, 0]))
                center_y = int(np.mean(scaled_corner[0][:, 1]))
                
                # Zeichne Marker mit Debug-Info
                cv2.aruco.drawDetectedMarkers(frame, [scaled_corner])
                
                # Component-Label
                component_name = component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
                
                # Marker-Details
                marker_area = cv2.contourArea(scaled_corner[0])
                perimeter = cv2.arcLength(scaled_corner[0], True)
                
                # Text mit Debug-Info
                cv2.putText(frame, component_name, (center_x - 80, center_y + 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"ID:{marker_id} Area:{int(marker_area)}", (center_x - 60, center_y + 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                cv2.putText(frame, f"Perim:{int(perimeter)}", (center_x - 40, center_y + 85), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Zeige rejected candidates (potentielle Marker)
        if len(rejected) > 0:
            for reject in rejected:
                cv2.polylines(frame, [np.int32(reject)], True, (0, 0, 255), 1)
        
        # Performance-Info
        avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0
        avg_markers = sum(detection_counts) / len(detection_counts) if detection_counts else 0
        frame_time = (time.time() - frame_start) * 1000
        
        # Status-Anzeige
        cv2.putText(frame, f"Mode: {param_sets[current_set]['name']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Detection: {avg_detection_time:.1f}ms", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Frame: {frame_time:.1f}ms", (10, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Markers: {markers_detected} (avg: {avg_markers:.1f})", (10, 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Rejected: {len(rejected)}", (10, 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        if detection_size:
            cv2.putText(frame, f"Detection Size: {detection_size}px", (10, 135), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        else:
            cv2.putText(frame, f"Detection Size: Full ({w}x{h})", (10, 135), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Display
        cv2.imshow('ArUco Quality Debug', frame)
        
        # Input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key in [ord('1'), ord('2'), ord('3')]:
            current_set = int(chr(key))
            detector = create_detector(param_sets[current_set])
            print(f"🔄 Switched to {param_sets[current_set]['name']} settings")
            # Reset statistics
            detection_times.clear()
            detection_counts.clear()
        elif key == ord('s'):
            screenshot_count += 1
            filename = f"debug_screenshot_{screenshot_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Debug screenshot saved: {filename}")
    
    # Final statistics
    print(f"\n📊 Final Statistics:")
    print(f"   Average Detection Time: {avg_detection_time:.1f}ms")
    print(f"   Average Markers Detected: {avg_markers:.1f}")
    print(f"   Total Frames: {frame_count}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("🔍 Quality debug ended")

if __name__ == "__main__":
    debug_aruco_quality()
