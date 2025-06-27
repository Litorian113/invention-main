"""
Camera utility functions for automatic camera detection and selection
"""
import cv2
import time

def detect_best_camera_fast():
    """Fast camera detection - prioritizes external cameras without extensive testing"""
    print("Quick camera detection...")
    
    # First, try external cameras (index 1-3) which are usually USB cameras
    external_cameras = [1, 2, 3]
    for camera_index in external_cameras:
        print(f"Testing camera {camera_index}...", end=" ")
        cap = cv2.VideoCapture(camera_index)
        
        # Set a very short timeout for faster detection
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if cap.isOpened():
            # Quick test - just check if we can get basic properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if width > 0 and height > 0:  # Basic sanity check
                cap.release()
                print(f"✓ Found external camera {camera_index}: {width}x{height}")
                return camera_index
            
        cap.release()
        print("✗")
    
    # If no external camera found, use built-in camera (index 0)
    print("Testing built-in camera 0...", end=" ")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        if width > 0 and height > 0:
            print(f"✓ Using built-in camera: {width}x{height}")
            return 0
    
    cap.release()
    print("✗")
    print("No working cameras found!")
    return None

def detect_best_camera():
    """Detect and return the best available camera"""
    print("Detecting available cameras...")
    
    # List to store working cameras
    working_cameras = []
    
    # Test cameras from 0 to 4 (usually enough for most systems)
    for camera_index in range(5):
        print(f"Testing camera {camera_index}...", end=" ")
        cap = cv2.VideoCapture(camera_index)
        
        # Set shorter timeout for faster detection
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if cap.isOpened():
            # Quick property check instead of frame reading
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            if width > 0 and height > 0:  # Basic sanity check
                camera_info = {
                    'index': camera_index,
                    'width': width,
                    'height': height,
                    'fps': fps
                }
                working_cameras.append(camera_info)
                print(f"✓ {width}x{height} @ {fps}fps")
            else:
                print("✗ Invalid properties")
        else:
            print("✗ Cannot open")
        
        cap.release()
    
    if not working_cameras:
        print("No working cameras found!")
        return None
    
    # Priority logic: prefer external cameras (usually higher indices) over built-in (usually index 0)
    # Also prefer cameras with higher resolution
    best_camera = None
    
    # First, look for external cameras (typically index 1 or higher)
    external_cameras = [cam for cam in working_cameras if cam['index'] > 0]
    if external_cameras:
        # Among external cameras, pick the one with highest resolution
        best_camera = max(external_cameras, key=lambda x: x['width'] * x['height'])
        print(f"Selected external camera {best_camera['index']} (Priority: External camera)")
    else:
        # Fall back to built-in camera (usually index 0)
        best_camera = working_cameras[0]
        print(f"Selected built-in camera {best_camera['index']} (No external camera found)")
    
    print(f"Using Camera {best_camera['index']}: {best_camera['width']}x{best_camera['height']} @ {best_camera['fps']}fps")
    return best_camera['index']

def get_camera_with_fallback():
    """Get the best camera with fallback to default - FAST VERSION"""
    camera_index = detect_best_camera_fast()
    if camera_index is None:
        print("Warning: No cameras detected, trying default camera 0")
        camera_index = 0
    
    print(f"Opening camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}")
        return None
    
    # Optimize camera settings for faster startup
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
    cap.set(cv2.CAP_PROP_FPS, 30)        # Set desired FPS
    
    # Warm up the camera with multiple frame reads and validate
    print("Initializing camera...", end=" ")
    
    for attempt in range(5):  # Try up to 5 times to get a valid frame
        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
            print("✓ Ready!")
            return cap
        time.sleep(0.1)  # Small delay between attempts
    
    print("⚠ Warning: Camera initialization failed")
    cap.release()
    return None

def get_camera_super_fast():
    """Super fast camera initialization - prioritizes Logitech HD webcam"""
    print("Super fast camera detection...")
    
    # PRIORISIERUNG: Kamera 0 ist die Logitech HD 1080p Webcam!
    # Basierend auf der Analyse: Kamera 0 > Kamera 2 > Kamera 1
    camera_indices = [0, 2, 1, 3]  # Logitech zuerst!
    
    for camera_index in camera_indices:
        print(f"Trying camera {camera_index}...", end=" ")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            # Optimale Einstellungen für Logitech HD-Webcam
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimaler Buffer für Live-Feed
            
            # Für Logitech: Explizit Full HD und 30fps setzen
            if camera_index == 0:  # Unsere Logitech-Kamera
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 30)
                print("(Logitech HD optimiert)", end=" ")
            else:
                cap.set(cv2.CAP_PROP_FPS, 30)        # Hohe FPS für andere Kameras
            
            # Versuche Auto-Exposure und andere Einstellungen zu optimieren
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Auto-Exposure aktivieren
            
            # Test if we can actually read a frame - try multiple times
            print("testing frames...", end=" ")
            successful_reads = 0
            
            for attempt in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
                    successful_reads += 1
                time.sleep(0.05)  # Kurze Pause zwischen Tests
            
            if successful_reads >= 3:  # Mindestens 3 von 5 Frames erfolgreich
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                camera_type = "🎯 LOGITECH HD" if camera_index == 0 else "📷"
                print(f"✓ Using {camera_type} camera {camera_index} ({width}x{height}@{fps}fps, {successful_reads}/5 frames)")
                
                # Leere den Buffer komplett und wärme die Kamera auf
                for _ in range(10):
                    cap.read()
                
                return cap
            else:
                print(f"✗ Unreliable ({successful_reads}/5 frames)")
        else:
            print("✗ Cannot open")
        
        cap.release()
    
    print("✗ No working cameras found")
    return None

def clear_camera_buffer(cap, num_frames=5):
    """Leere den Kamera-Buffer um sicherzustellen, dass wir den neuesten Frame bekommen"""
    for _ in range(num_frames):
        cap.grab()  # Überspringe Frames ohne sie zu dekodieren (schneller)

def get_fresh_frame(cap, max_attempts=3):
    """Hole einen frischen Frame und leere vorher den Buffer"""
    clear_camera_buffer(cap, 2)  # Leere alte Frames
    
    for attempt in range(max_attempts):
        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
            return ret, frame
        time.sleep(0.01)  # Kurze Pause vor erneutem Versuch
    
    return False, None

def get_logitech_camera_optimized():
    """Spezielle Funktion für optimale Logitech HD 1080p Webcam Nutzung"""
    print("🎯 Initialisiere Logitech HD 1080p Webcam...")
    
    # Direkt Kamera 0 verwenden (identifiziert als Logitech)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Logitech-Kamera nicht verfügbar, verwende Fallback")
        return get_camera_super_fast()
    
    print("📷 Konfiguriere Logitech-optimierte Einstellungen...")
    
    # Optimale Logitech HD-Einstellungen
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)      # Full HD Breite
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)     # Full HD Höhe
    cap.set(cv2.CAP_PROP_FPS, 30)                # 30fps für flüssiges Video
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)          # Minimaler Buffer
    
    # Logitech-spezifische Optimierungen
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)    # Auto-Exposure
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)           # Auto-Focus
    
    # Optional: Bildqualität optimieren (falls unterstützt)
    try:
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)     # Helligkeit
        cap.set(cv2.CAP_PROP_CONTRAST, 0.5)       # Kontrast  
        cap.set(cv2.CAP_PROP_SATURATION, 0.5)     # Sättigung
    except:
        pass  # Nicht alle Eigenschaften werden von allen Kameras unterstützt
    
    # Warte kurz, damit die Einstellungen angewendet werden
    time.sleep(0.5)
    
    # Validiere die Einstellungen
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"✅ Logitech-Kamera konfiguriert: {actual_width}x{actual_height}@{actual_fps}fps")
    
    # Teste Frames
    print("🔄 Teste Logitech-Frame-Aufnahme...", end=" ")
    successful_frames = 0
    
    for _ in range(5):
        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
            successful_frames += 1
        time.sleep(0.05)
    
    if successful_frames >= 4:
        print(f"✅ Perfekt ({successful_frames}/5 Frames)")
        
        # Wärme die Kamera final auf
        for _ in range(5):
            cap.read()
            
        return cap
    else:
        print(f"⚠️ Unzuverlässig ({successful_frames}/5 Frames), verwende Fallback")
        cap.release()
        return get_camera_super_fast()
