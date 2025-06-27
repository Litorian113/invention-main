#!/usr/bin/env python3
"""
Logitech HD 1080p Webcam Test
Testet die optimale Konfiguration für die Logitech-Webcam
"""
import cv2
import time
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera_utils import get_logitech_camera_optimized

def test_logitech_webcam():
    """Teste die Logitech-Webcam mit Live-Preview"""
    print("=== Logitech HD 1080p Webcam Live-Test ===")
    print("Drücke 'q' zum Beenden")
    print("Drücke 's' für Screenshot")
    print("Drücke 'r' für Auflösungstest")
    
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("❌ Logitech-Webcam konnte nicht initialisiert werden!")
        return
    
    frame_count = 0
    start_time = time.time()
    screenshot_count = 0
    
    # FPS-Berechnung
    fps_start_time = time.time()
    fps_frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("⚠️ Frame-Fehler!")
            continue
        
        frame_count += 1
        fps_frame_count += 1
        
        # FPS berechnen (alle 30 Frames)
        if fps_frame_count >= 30:
            current_time = time.time()
            elapsed = current_time - fps_start_time
            fps = fps_frame_count / elapsed
            
            # FPS-Anzeige auf dem Frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            fps_start_time = current_time
            fps_frame_count = 0
        
        # Frame-Info anzeigen
        height, width = frame.shape[:2]
        cv2.putText(frame, f"Logitech HD: {width}x{height}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Zeige das Frame
        cv2.imshow('Logitech HD 1080p Webcam Test', frame)
        
        # Tastatureingabe verarbeiten
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Screenshot speichern
            screenshot_count += 1
            filename = f"logitech_screenshot_{screenshot_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot gespeichert: {filename}")
        elif key == ord('r'):
            # Auflösungstest
            print("\n🔍 Teste verschiedene Auflösungen...")
            test_resolutions(cap)
    
    # Statistiken
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print(f"\n📊 Test-Statistiken:")
    print(f"   Gesamte Frames: {frame_count}")
    print(f"   Laufzeit: {total_time:.1f}s")
    print(f"   Durchschnittliche FPS: {avg_fps:.1f}")
    print(f"   Screenshots: {screenshot_count}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test beendet")

def test_resolutions(cap):
    """Teste verschiedene Auflösungen"""
    resolutions = [
        (1920, 1080, "Full HD"),
        (1280, 720, "HD"),
        (1600, 1200, "UXGA"),
        (1024, 768, "XGA"),
        (800, 600, "SVGA"),
        (640, 480, "VGA")
    ]
    
    print("📋 Unterstützte Auflösungen:")
    
    for width, height, name in resolutions:
        # Setze Auflösung
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        time.sleep(0.2)  # Kurz warten
        
        # Prüfe tatsächliche Auflösung
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Teste Frame-Aufnahme
        ret, frame = cap.read()
        
        if ret and actual_width == width and actual_height == height:
            print(f"   ✅ {name}: {width}x{height}")
        else:
            print(f"   ❌ {name}: {width}x{height} (tatsächlich: {actual_width}x{actual_height})")
    
    # Zurück zu Full HD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("🔄 Zurück zu Full HD (1920x1080)")

if __name__ == "__main__":
    print("Logitech HD 1080p Webcam Test-Tool")
    print("=" * 50)
    test_logitech_webcam()
