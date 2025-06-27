#!/usr/bin/env python3
"""
Kamera-Test-Script zur Diagnose von Kameraproblemen
"""
import cv2
import time

def test_all_cameras():
    """Teste alle verfügbaren Kameras und zeige detaillierte Informationen"""
    print("=== Kamera-Diagnose ===")
    print("Teste alle verfügbaren Kameras (0-4)...")
    
    working_cameras = []
    
    for camera_index in range(5):
        print(f"\n--- Teste Kamera {camera_index} ---")
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print(f"❌ Kamera {camera_index}: Kann nicht geöffnet werden")
                continue
            
            # Eigenschaften abrufen
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"📋 Kamera {camera_index}: {width}x{height} @ {fps}fps")
            
            # Versuche ein Frame zu lesen
            print("🔄 Teste Frame-Aufnahme...", end=" ")
            
            for attempt in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
                    print(f"✅ Erfolg (Versuch {attempt + 1})")
                    working_cameras.append({
                        'index': camera_index,
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'attempts': attempt + 1
                    })
                    break
                time.sleep(0.2)
            else:
                print("❌ Fehlgeschlagen nach 5 Versuchen")
            
            cap.release()
            
        except Exception as e:
            print(f"❌ Kamera {camera_index}: Fehler - {e}")
    
    print(f"\n=== Zusammenfassung ===")
    if working_cameras:
        print(f"✅ {len(working_cameras)} funktionierende Kamera(s) gefunden:")
        for cam in working_cameras:
            print(f"   Kamera {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']}fps (nach {cam['attempts']} Versuch(en))")
        
        # Empfehlung
        best_cam = max(working_cameras, key=lambda x: x['width'] * x['height'])
        print(f"\n💡 Empfehlung: Verwende Kamera {best_cam['index']} (höchste Auflösung)")
        
        return best_cam['index']
    else:
        print("❌ Keine funktionierende Kamera gefunden!")
        return None

def test_specific_camera(camera_index):
    """Teste eine spezifische Kamera ausführlich"""
    print(f"\n=== Ausführlicher Test für Kamera {camera_index} ===")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Kamera {camera_index} kann nicht geöffnet werden")
            return False
        
        # Buffer-Größe setzen
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Eigenschaften anzeigen
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"📋 Auflösung: {width}x{height}")
        print(f"📋 FPS: {fps}")
        
        # Mehrere Frames testen
        print("🔄 Teste 10 aufeinanderfolgende Frames...")
        successful_frames = 0
        
        for i in range(10):
            ret, frame = cap.read()
            if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
                successful_frames += 1
                print(f"   Frame {i+1}: ✅")
            else:
                print(f"   Frame {i+1}: ❌")
            time.sleep(0.1)
        
        print(f"📊 Erfolgreiche Frames: {successful_frames}/10")
        
        cap.release()
        
        if successful_frames >= 8:
            print("✅ Kamera funktioniert zuverlässig")
            return True
        else:
            print("⚠️ Kamera ist unzuverlässig")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    print("Kamera-Diagnosewerkzeug")
    print("=" * 50)
    
    # Teste alle Kameras
    best_camera = test_all_cameras()
    
    if best_camera is not None:
        # Teste die beste Kamera ausführlich
        test_specific_camera(best_camera)
    
    print("\n🏁 Diagnose abgeschlossen")
