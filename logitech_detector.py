#!/usr/bin/env python3
"""
Erweiterte Kamera-Diagnose zur Identifikation der Logitech-Webcam
"""
import cv2
import time

def identify_cameras():
    """Identifiziere Kameras mit detaillierten Informationen"""
    print("=== Erweiterte Kamera-Identifikation ===")
    print("Suche nach Logitech HD 1080p Webcam...")
    
    cameras_info = []
    
    for camera_index in range(5):
        print(f"\n--- Analysiere Kamera {camera_index} ---")
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print(f"❌ Kamera {camera_index}: Nicht verfügbar")
                continue
            
            # Alle verfügbaren Eigenschaften abrufen
            properties = {}
            
            # Standard-Eigenschaften
            properties['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            properties['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            properties['fps'] = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Erweiterte Eigenschaften (falls verfügbar)
            try:
                properties['fourcc'] = int(cap.get(cv2.CAP_PROP_FOURCC))
                properties['brightness'] = cap.get(cv2.CAP_PROP_BRIGHTNESS)
                properties['contrast'] = cap.get(cv2.CAP_PROP_CONTRAST)
                properties['saturation'] = cap.get(cv2.CAP_PROP_SATURATION)
                properties['hue'] = cap.get(cv2.CAP_PROP_HUE)
                properties['gain'] = cap.get(cv2.CAP_PROP_GAIN)
                properties['exposure'] = cap.get(cv2.CAP_PROP_EXPOSURE)
            except:
                pass
            
            print(f"📋 Grundeigenschaften:")
            print(f"   Auflösung: {properties['width']}x{properties['height']}")
            print(f"   FPS: {properties['fps']}")
            
            # Versuche verschiedene HD-Auflösungen zu setzen (typisch für Logitech)
            hd_resolutions = [
                (1920, 1080),  # Full HD
                (1280, 720),   # HD
                (1600, 1200),  # UXGA
                (1024, 768)    # XGA
            ]
            
            supported_resolutions = []
            for width, height in hd_resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                if actual_width == width and actual_height == height:
                    supported_resolutions.append(f"{width}x{height}")
            
            print(f"📋 Unterstützte HD-Auflösungen: {', '.join(supported_resolutions) if supported_resolutions else 'Keine'}")
            
            # Teste verschiedene FPS-Werte (Logitech unterstützt meist 30fps bei HD)
            original_fps = properties['fps']
            
            # Setze auf Full HD und teste FPS
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            time.sleep(0.5)  # Kurz warten bis Einstellungen angewendet sind
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Frame-Test bei Full HD
            print(f"🔄 Teste Full HD (1920x1080) @ 30fps...")
            successful_hd_frames = 0
            
            for i in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.shape[0] == 1080 and frame.shape[1] == 1920:
                    successful_hd_frames += 1
                time.sleep(0.1)
            
            print(f"   Ergebnis: {actual_width}x{actual_height} @ {actual_fps}fps ({successful_hd_frames}/5 HD-Frames erfolgreich)")
            
            # Kamera-Typ bestimmen
            camera_type = "Unbekannt"
            confidence = "Niedrig"
            
            if actual_width == 1920 and actual_height == 1080 and successful_hd_frames >= 4:
                if actual_fps >= 25:
                    camera_type = "Externe HD-Webcam (wahrscheinlich Logitech)"
                    confidence = "Hoch"
                else:
                    camera_type = "HD-Kamera (niedrige FPS)"
                    confidence = "Mittel"
            elif actual_width == 1280 and actual_height == 720 and successful_hd_frames >= 4:
                camera_type = "HD-Webcam (720p)"
                confidence = "Mittel"
            elif camera_index == 0 and actual_fps < 10:
                camera_type = "Integrierte Laptop-Kamera"
                confidence = "Hoch"
            
            cameras_info.append({
                'index': camera_index,
                'type': camera_type,
                'confidence': confidence,
                'width': actual_width,
                'height': actual_height,
                'fps': actual_fps,
                'hd_frames': successful_hd_frames,
                'supported_resolutions': supported_resolutions
            })
            
            print(f"🎯 Identifikation: {camera_type} (Vertrauen: {confidence})")
            
            cap.release()
            
        except Exception as e:
            print(f"❌ Fehler bei Kamera {camera_index}: {e}")
    
    return cameras_info

def recommend_best_camera(cameras_info):
    """Empfehle die beste Kamera für AR-Anwendungen"""
    print(f"\n=== Empfehlung für AR-Anwendung ===")
    
    if not cameras_info:
        print("❌ Keine funktionierenden Kameras gefunden!")
        return None
    
    # Priorisierung: Externe HD-Webcam > HD-Webcam > Andere
    logitech_cameras = [cam for cam in cameras_info if "Logitech" in cam['type']]
    hd_cameras = [cam for cam in cameras_info if cam['width'] >= 1280 and cam['fps'] >= 25]
    working_cameras = [cam for cam in cameras_info if cam['hd_frames'] >= 3]
    
    best_camera = None
    
    if logitech_cameras:
        best_camera = max(logitech_cameras, key=lambda x: (x['width'] * x['height'], x['fps']))
        print(f"🏆 BESTE WAHL: Kamera {best_camera['index']} - {best_camera['type']}")
        print(f"   Grund: Logitech-Webcam mit optimaler HD-Unterstützung")
    elif hd_cameras:
        best_camera = max(hd_cameras, key=lambda x: (x['width'] * x['height'], x['fps']))
        print(f"🥈 EMPFEHLUNG: Kamera {best_camera['index']} - {best_camera['type']}")
        print(f"   Grund: Beste HD-Performance verfügbar")
    elif working_cameras:
        best_camera = max(working_cameras, key=lambda x: (x['width'] * x['height'], x['fps']))
        print(f"🥉 FALLBACK: Kamera {best_camera['index']} - {best_camera['type']}")
        print(f"   Grund: Einzige funktionierende Option")
    
    if best_camera:
        print(f"📋 Spezifikationen: {best_camera['width']}x{best_camera['height']} @ {best_camera['fps']}fps")
        print(f"📋 HD-Frame-Erfolg: {best_camera['hd_frames']}/5")
        
    return best_camera['index'] if best_camera else None

if __name__ == "__main__":
    print("Logitech-Webcam-Identifikation")
    print("=" * 50)
    
    cameras_info = identify_cameras()
    best_camera_index = recommend_best_camera(cameras_info)
    
    if best_camera_index is not None:
        print(f"\n✅ Verwende Kamera {best_camera_index} für das AR-Projekt!")
    else:
        print(f"\n❌ Keine geeignete Kamera gefunden!")
