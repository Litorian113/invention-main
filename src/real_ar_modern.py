#!/usr/bin/env python3
"""
Modern AR Application mit echter Kamera - PyQt6 UI mit funktionierender Kamera
Nutzt die bereits optimierte Kamera-Funktionalität aus dem bestehenden System
"""
import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QProgressBar, 
                            QListWidget, QListWidgetItem, QCheckBox, QSlider, 
                            QGroupBox, QTextEdit)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush
import qdarktheme

# Import der bestehenden Kamera-Funktionen
from camera_utils import get_logitech_camera_optimized, get_fresh_frame


class RealARCameraThread(QThread):
    """Echter Kamera-Thread der die funktionierende Kamera verwendet"""
    
    frame_ready = pyqtSignal(np.ndarray, list, float, float)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.mutex = QMutex()
        self.settings = {
            'quality': 3,
            'show_markers': True,
            'show_ids': True,
            'target_fps': 30
        }
        
    def update_settings(self, new_settings):
        """Update processing settings"""
        with QMutex():
            self.settings.update(new_settings)
        
    def run(self):
        """Hauptschleife mit echter Kamera"""
        print("🎥 Initialisiere echte Kamera...")
        
        # Verwende die bereits optimierte Kamera-Initialisierung
        cap = get_logitech_camera_optimized()
        if cap is None:
            print("❌ Fehler: Kamera konnte nicht initialisiert werden")
            return
            
        print("✅ Kamera erfolgreich initialisiert!")
        
        # ArUco-Setup genau wie im funktionierenden System
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        aruco_params = cv2.aruco.DetectorParameters()
        
        # Verwende die bewährten Parameter aus main.py
        aruco_params.adaptiveThreshWinSizeMin = 3
        aruco_params.adaptiveThreshWinSizeMax = 23
        aruco_params.adaptiveThreshWinSizeStep = 4
        aruco_params.minMarkerPerimeterRate = 0.03
        aruco_params.maxMarkerPerimeterRate = 4.0
        aruco_params.polygonalApproxAccuracyRate = 0.05
        aruco_params.minCornerDistanceRate = 0.05
        aruco_params.minDistanceToBorder = 3
        
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Performance-Parameter wie im funktionierenden System
        detection_size = 960
        detect_every = 1
        frame_count = 0
        cached_markers = []
        
        # FPS-Tracking
        fps_count = 0
        fps_start = time.time()
        current_fps = 0.0
        
        # Komponenten-Labels (gleiche wie in main.py)
        component_labels = {
            0: "Arduino Leonardo",
            1: "Breadboard", 
            2: "LED",
            3: "220 Ohm Resistor",
            4: "Potentiometer",
            5: "Jumper Wires"
        }
        
        self.running = True
        print("🚀 Starte AR-Verarbeitung...")
        
        while self.running:
            frame_start = time.time()
            
            # Verwende get_fresh_frame wie im funktionierenden System
            ret, frame = get_fresh_frame(cap)
            
            if not ret or frame is None:
                print("⚠️ Frame konnte nicht gelesen werden, versuche direkten read...")
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    print("❌ Fehler beim Frame-Lesen")
                    continue
            
            # Validiere Frame-Dimensionen
            if frame.shape[0] == 0 or frame.shape[1] == 0:
                print("⚠️ Ungültige Frame-Dimensionen")
                continue
                
            frame_count += 1
            fps_count += 1
            h, w = frame.shape[:2]
            
            # ADAPTIVE DETECTION wie im funktionierenden System
            if frame_count % detect_every == 0:
                # Intelligente Skalierung
                scale = min(detection_size / max(w, h), 1.0)
                new_w, new_h = int(w * scale), int(h * scale)
                
                if scale < 1.0:
                    small_frame = cv2.resize(frame, (new_w, new_h))
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                else:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # ArUco Detection
                corners, ids, _ = detector.detectMarkers(gray)
                
                # Cache Marker-Daten (exakt wie in main.py)
                cached_markers = []
                if ids is not None:
                    for i, corner in enumerate(corners):
                        marker_id = ids[i][0]
                        if scale < 1.0:
                            # Skaliere Koordinaten zurück
                            scaled_corner = corner / scale
                            center_x = int(np.mean(scaled_corner[0][:, 0]))
                            center_y = int(np.mean(scaled_corner[0][:, 1]))
                            corners_2d = scaled_corner[0].astype(np.int32)
                        else:
                            # Verwende Original-Koordinaten
                            center_x = int(np.mean(corner[0][:, 0]))
                            center_y = int(np.mean(corner[0][:, 1]))
                            corners_2d = corner[0].astype(np.int32)
                        cached_markers.append((marker_id, center_x, center_y, corners_2d))
            
            # Marker-Visualisierung (nur wenn aktiviert)
            if self.settings['show_markers'] or self.settings['show_ids']:
                for marker_id, center_x, center_y, corners_2d in cached_markers:
                    component_name = component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
                    
                    # Komponentenspezifische Farbe (wie in main.py)
                    colors = {
                        0: (255, 0, 0),    # Arduino - Blau
                        1: (0, 255, 0),    # Breadboard - Grün  
                        2: (0, 0, 255),    # LED - Rot
                        3: (0, 255, 255),  # Resistor - Cyan
                        4: (255, 0, 255),  # Potentiometer - Magenta
                        5: (255, 255, 0)   # Jumper Wires - Gelb
                    }
                    box_color = colors.get(marker_id, (255, 255, 255))
                    
                    if self.settings['show_markers']:
                        # Perspektivische Box (vereinfacht)
                        center = np.mean(corners_2d, axis=0)
                        vectors = corners_2d - center
                        extended_vectors = vectors * 1.25  # 25% padding
                        extended_corners = center + extended_vectors
                        extended_corners = extended_corners.astype(np.int32)
                        
                        # Zeichne Box
                        cv2.polylines(frame, [extended_corners], True, box_color, 3)
                        cv2.polylines(frame, [corners_2d], True, (255, 255, 255), 2)
                        
                        # Center-Punkt
                        center_color = (255 - box_color[0], 255 - box_color[1], 255 - box_color[2])
                        cv2.circle(frame, (center_x, center_y), 8, center_color, -1)
                        cv2.circle(frame, (center_x, center_y), 10, box_color, 2)
                        
                        # Label unterhalb
                        text_size = cv2.getTextSize(component_name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        box_bottom = np.max(extended_corners[:, 1])
                        label_x = center_x - text_size[0] // 2
                        label_y = box_bottom + 25
                        
                        # Grenze prüfen
                        if label_y > h - 30:
                            box_top = np.min(extended_corners[:, 1])
                            label_y = box_top - 10
                        label_x = max(5, min(label_x, w - text_size[0] - 5))
                        
                        # Label-Hintergrund
                        label_bg_x1 = label_x - 8
                        label_bg_y1 = label_y - text_size[1] - 8
                        label_bg_x2 = label_x + text_size[0] + 8
                        label_bg_y2 = label_y + 8
                        
                        cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), (0, 0, 0), -1)
                        cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), box_color, 2)
                        cv2.putText(frame, component_name, (label_x, label_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
                    
                    if self.settings['show_ids']:
                        # Marker-ID
                        id_text = f"#{marker_id}"
                        cv2.putText(frame, id_text, (center_x - 20, center_y - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(frame, id_text, (center_x - 20, center_y - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 1)
            
            # Performance-Metriken
            frame_time = (time.time() - frame_start) * 1000
            
            # FPS-Berechnung
            if fps_count >= 30:
                elapsed = time.time() - fps_start
                current_fps = 30 / elapsed if elapsed > 0 else 0
                fps_start = time.time()
                fps_count = 0
            
            # Frame mit Daten senden
            self.frame_ready.emit(frame, cached_markers, current_fps, frame_time)
            
            # FPS-Begrenzung
            target_frame_time = 1000 / self.settings['target_fps']
            if frame_time < target_frame_time:
                sleep_time = int(target_frame_time - frame_time)
                self.msleep(max(1, sleep_time))
        
        # Aufräumen
        cap.release()
        print("📹 Kamera released")
        
    def stop(self):
        """Stop the camera thread"""
        print("🛑 Stoppe Kamera-Thread...")
        self.running = False
        self.wait()


class ModernComponentsPanel(QFrame):
    """Modernes Komponenten-Panel mit echter Erkennung"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.detected_components = set()
        
    def setup_ui(self):
        self.setFixedWidth(320)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C3E50, stop:1 #34495E);
                border: 1px solid #1ABC9C;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🔍 DETECTED COMPONENTS")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #1ABC9C;
                border: none;
                background: transparent;
                padding: 10px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Live-Status
        self.status_label = QLabel("🎥 Scanning with real camera...")
        self.status_label.setStyleSheet("color: #F39C12; font-size: 11px; border: none;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Komponenten-Liste
        self.components_list = QListWidget()
        self.components_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #ECF0F1;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 12px;
                margin: 4px;
                border-radius: 10px;
                background: rgba(26, 188, 156, 0.1);
                border: 1px solid rgba(26, 188, 156, 0.2);
            }
            QListWidget::item:hover {
                background: rgba(26, 188, 156, 0.2);
                border: 1px solid rgba(26, 188, 156, 0.4);
            }
        """)
        layout.addWidget(self.components_list)
        
        # Fortschritt
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        progress_layout = QVBoxLayout(progress_frame)
        
        self.progress_label = QLabel("Progress: 0/6 Components")
        self.progress_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.progress_label.setStyleSheet("color: #BDC3C7; border: none;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495E;
                border-radius: 10px;
                text-align: center;
                color: white;
                background: #2C3E50;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1ABC9C, stop:0.5 #16A085, stop:1 #1ABC9C);
                border-radius: 8px;
                margin: 1px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
        
    def update_components(self, markers):
        """Update mit echten Erkennungsdaten"""
        component_labels = {
            0: ("Arduino Leonardo", "#E74C3C"),
            1: ("Breadboard", "#3498DB"), 
            2: ("LED", "#F1C40F"),
            3: ("220Ω Resistor", "#E67E22"),
            4: ("Potentiometer", "#9B59B6"),
            5: ("Jumper Wires", "#2ECC71")
        }
        
        # Erkannte Komponenten sammeln
        current_components = set()
        for marker_id, _, _, _ in markers:
            if marker_id in component_labels:
                current_components.add(marker_id)
        
        # Nur aktualisieren wenn sich was geändert hat
        if current_components != self.detected_components:
            self.detected_components = current_components
            
            # Liste neu aufbauen
            self.components_list.clear()
            
            for component_id in sorted(current_components):
                name, color = component_labels[component_id]
                item = QListWidgetItem(f"✅ {name} (ID: {component_id})")
                self.components_list.addItem(item)
            
            # Fortschritt aktualisieren
            count = len(current_components)
            self.progress_bar.setValue(count)
            self.progress_label.setText(f"Progress: {count}/6 Components")
            
            # Status aktualisieren
            if count == 6:
                self.status_label.setText("🎉 All components detected!")
                self.status_label.setStyleSheet("color: #2ECC71; font-size: 12px; font-weight: bold; border: none;")
            elif count >= 4:
                self.status_label.setText("📋 Almost there! Keep going...")
                self.status_label.setStyleSheet("color: #F39C12; font-size: 11px; border: none;")
            elif count >= 2:
                self.status_label.setText("🔍 Good progress, scanning...")
                self.status_label.setStyleSheet("color: #3498DB; font-size: 11px; border: none;")
            else:
                self.status_label.setText("🎥 Scanning with real camera...")
                self.status_label.setStyleSheet("color: #95A5A6; font-size: 11px; border: none;")


class ModernControlPanel(QFrame):
    """Kontrollpanel für Kamera-Einstellungen"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A2E, stop:1 #16213E);
                border: 1px solid #0F4C75;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚙️ REAL CAMERA CONTROLS")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #3282B8;
                border: none;
                padding: 10px;
                background: transparent;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Display-Optionen
        display_group = QGroupBox("Display Options")
        display_group.setStyleSheet("""
            QGroupBox {
                color: #BBE1FA;
                font-weight: bold;
                border: 2px solid #0F4C75;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background: transparent;
            }
        """)
        
        display_layout = QVBoxLayout(display_group)
        
        checkbox_style = """
            QCheckBox {
                color: #BBE1FA;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #0F4C75;
                border-radius: 3px;
                background: #16213E;
            }
            QCheckBox::indicator:checked {
                background: #3282B8;
                border-color: #3282B8;
            }
        """
        
        self.show_markers_cb = QCheckBox("Show Marker Boundaries")
        self.show_markers_cb.setChecked(True)
        self.show_markers_cb.setStyleSheet(checkbox_style)
        self.show_markers_cb.stateChanged.connect(self.emit_settings)
        display_layout.addWidget(self.show_markers_cb)
        
        self.show_ids_cb = QCheckBox("Show Marker IDs")
        self.show_ids_cb.setChecked(True)
        self.show_ids_cb.setStyleSheet(checkbox_style)
        self.show_ids_cb.stateChanged.connect(self.emit_settings)
        display_layout.addWidget(self.show_ids_cb)
        
        layout.addWidget(display_group)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_group.setStyleSheet(display_group.styleSheet())
        
        perf_layout = QVBoxLayout(perf_group)
        
        fps_label = QLabel("Target FPS:")
        fps_label.setStyleSheet("color: #BBE1FA; font-size: 11px;")
        perf_layout.addWidget(fps_label)
        
        self.fps_slider = QSlider(Qt.Orientation.Horizontal)
        self.fps_slider.setRange(15, 60)
        self.fps_slider.setValue(30)
        self.fps_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #0F4C75;
                height: 8px;
                background: #16213E;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3282B8;
                border: 1px solid #0F4C75;
                width: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #3282B8;
                border-radius: 4px;
            }
        """)
        self.fps_slider.valueChanged.connect(self.emit_settings)
        perf_layout.addWidget(self.fps_slider)
        
        self.fps_value_label = QLabel("30 FPS")
        self.fps_value_label.setStyleSheet("color: #3282B8; font-size: 10px; text-align: center;")
        self.fps_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        perf_layout.addWidget(self.fps_value_label)
        
        self.fps_slider.valueChanged.connect(lambda v: self.fps_value_label.setText(f"{v} FPS"))
        
        layout.addWidget(perf_group)
        
        # Statistiken
        stats_group = QGroupBox("Live Statistics")
        stats_group.setStyleSheet(display_group.styleSheet())
        
        stats_layout = QVBoxLayout(stats_group)
        
        self.current_fps_label = QLabel("Current FPS: 0.0")
        self.marker_count_label = QLabel("Markers: 0")
        self.frame_time_label = QLabel("Frame Time: 0ms")
        self.camera_status_label = QLabel("Camera: Initializing...")
        
        for label in [self.current_fps_label, self.marker_count_label, self.frame_time_label, self.camera_status_label]:
            label.setStyleSheet("color: #BBE1FA; font-size: 10px;")
            stats_layout.addWidget(label)
            
        layout.addWidget(stats_group)
        
        # Info
        info_text = QTextEdit()
        info_text.setFixedHeight(100)
        info_text.setReadOnly(True)
        info_text.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #0F4C75;
                border-radius: 8px;
                color: #BBE1FA;
                font-size: 10px;
                padding: 8px;
            }
        """)
        info_text.setPlainText(
            "🎥 LIVE CAMERA MODE\n\n"
            "Using your real camera for AR detection! "
            "Place ArUco markers in front of the camera to see them detected in real-time."
        )
        layout.addWidget(info_text)
        
        layout.addStretch()
        
    def emit_settings(self):
        """Emit current settings"""
        settings = {
            'show_markers': self.show_markers_cb.isChecked(),
            'show_ids': self.show_ids_cb.isChecked(),
            'target_fps': self.fps_slider.value()
        }
        self.settings_changed.emit(settings)
        
    def update_stats(self, fps, marker_count, frame_time):
        """Update statistics display"""
        self.current_fps_label.setText(f"Current FPS: {fps:.1f}")
        self.marker_count_label.setText(f"Markers: {marker_count}")
        self.frame_time_label.setText(f"Frame Time: {frame_time:.1f}ms")
        
        # Kamera-Status basierend auf FPS
        if fps > 25:
            self.camera_status_label.setText("Camera: Excellent")
            self.camera_status_label.setStyleSheet("color: #2ECC71; font-size: 10px;")
        elif fps > 15:
            self.camera_status_label.setText("Camera: Good")
            self.camera_status_label.setStyleSheet("color: #F39C12; font-size: 10px;")
        else:
            self.camera_status_label.setText("Camera: Slow")
            self.camera_status_label.setStyleSheet("color: #E74C3C; font-size: 10px;")


class RealARMainWindow(QMainWindow):
    """Hauptfenster mit echter Kamera-Integration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle("🎥 Modern AR with Real Camera - PyQt6")
        self.setMinimumSize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        self.control_panel = ModernControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # Center-left panel - Components
        self.components_panel = ModernComponentsPanel()
        main_layout.addWidget(self.components_panel)
        
        # Center - AR Video display
        self.ar_label = QLabel()
        self.ar_label.setMinimumSize(640, 480)
        self.ar_label.setStyleSheet("""
            QLabel {
                border: 3px solid #1ABC9C;
                border-radius: 15px;
                background-color: #2C3E50;
                color: #1ABC9C;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.ar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ar_label.setText("🎥 Initializing Real Camera...")
        main_layout.addWidget(self.ar_label)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Control panel
        main_layout.setStretch(1, 1)  # Components panel
        main_layout.setStretch(2, 4)  # Video display
        
    def setup_camera(self):
        """Initialize real camera processing"""
        self.camera_thread = RealARCameraThread()
        self.camera_thread.frame_ready.connect(self.update_display)
        self.control_panel.settings_changed.connect(self.camera_thread.update_settings)
        
        # Starte Kamera-Thread
        self.camera_thread.start()
        
        print("🚀 Real AR Application mit echter Kamera gestartet!")
        
    def update_display(self, frame, markers, fps, frame_time):
        """Update all UI components with real camera data"""
        # Convert frame to Qt format and display
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        # Scale to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.ar_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ar_label.setPixmap(scaled_pixmap)
        
        # Update components panel with real detection data
        self.components_panel.update_components(markers)
        
        # Update control panel stats with real data
        self.control_panel.update_stats(fps, len(markers), frame_time)
        
    def closeEvent(self, event):
        """Handle application closing"""
        print("🛑 Schließe Anwendung...")
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Apply modern dark theme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("Modern AR with Real Camera")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = RealARMainWindow()
    window.show()
    
    print("🎥 Modern AR Application mit echter Kamera!")
    print("✨ PyQt6 UI mit funktionierender Logitech-Kamera")
    print("🔍 Echte ArUco-Marker-Erkennung in Echtzeit")
    print("⚙️ Konfigurierbare Anzeigeoptionen")
    print("📊 Live-Performance-Monitoring")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
