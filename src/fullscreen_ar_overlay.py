#!/usr/bin/env python3
"""
Fullscreen AR mit transparenten Overlays - PyQt6 UI
Der Kamera-Feed füllt das gesamte Fenster, UI-Elemente erscheinen als transparente Overlays
"""
import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QProgressBar, 
                            QListWidget, QListWidgetItem, QCheckBox, QSlider, 
                            QGroupBox, QTextEdit, QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush, QPalette
import qdarktheme

# Import der bestehenden Kamera-Funktionen
from camera_utils import get_logitech_camera_optimized, get_fresh_frame


class AROverlayCameraThread(QThread):
    """Kamera-Thread für Fullscreen AR mit Overlays"""
    
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
        print("🎥 Initialisiere Fullscreen AR Kamera...")
        
        # Verwende die bereits optimierte Kamera-Initialisierung
        cap = get_logitech_camera_optimized()
        if cap is None:
            print("❌ Fehler: Kamera konnte nicht initialisiert werden")
            return
            
        print("✅ Kamera erfolgreich initialisiert!")
        
        # ArUco-Setup genau wie im funktionierenden System
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        aruco_params = cv2.aruco.DetectorParameters()
        
        # Verwende die bewährten Parameter
        aruco_params.adaptiveThreshWinSizeMin = 3
        aruco_params.adaptiveThreshWinSizeMax = 23
        aruco_params.adaptiveThreshWinSizeStep = 4
        aruco_params.minMarkerPerimeterRate = 0.03
        aruco_params.maxMarkerPerimeterRate = 4.0
        aruco_params.polygonalApproxAccuracyRate = 0.05
        aruco_params.minCornerDistanceRate = 0.05
        aruco_params.minDistanceToBorder = 3
        
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Performance-Parameter
        detection_size = 960
        detect_every = 1
        frame_count = 0
        cached_markers = []
        
        # FPS-Tracking
        fps_count = 0
        fps_start = time.time()
        current_fps = 0.0
        
        # Komponenten-Labels
        component_labels = {
            0: "Arduino Leonardo",
            1: "Breadboard", 
            2: "LED",
            3: "220 Ohm Resistor",
            4: "Potentiometer",
            5: "Jumper Wires"
        }
        
        self.running = True
        print("🚀 Starte Fullscreen AR-Verarbeitung...")
        
        while self.running:
            frame_start = time.time()
            
            # Frame lesen
            ret, frame = get_fresh_frame(cap)
            
            if not ret or frame is None:
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue
            
            # Validiere Frame-Dimensionen
            if frame.shape[0] == 0 or frame.shape[1] == 0:
                continue
                
            frame_count += 1
            fps_count += 1
            h, w = frame.shape[:2]
            
            # ADAPTIVE DETECTION
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
            
            # Marker-Visualisierung für AR
            if self.settings['show_markers'] or self.settings['show_ids']:
                for marker_id, center_x, center_y, corners_2d in cached_markers:
                    component_name = component_labels.get(marker_id, f"Unknown (ID: {marker_id})")
                    
                    # Komponentenspezifische Farbe
                    colors = {
                        0: (255, 100, 100),   # Arduino - Helles Blau
                        1: (100, 255, 100),   # Breadboard - Helles Grün  
                        2: (100, 100, 255),   # LED - Helles Rot
                        3: (100, 255, 255),   # Resistor - Helles Cyan
                        4: (255, 100, 255),   # Potentiometer - Helles Magenta
                        5: (255, 255, 100)    # Jumper Wires - Helles Gelb
                    }
                    box_color = colors.get(marker_id, (255, 255, 255))
                    
                    if self.settings['show_markers']:
                        # Erweiterte AR-Visualisierung
                        center = np.mean(corners_2d, axis=0)
                        vectors = corners_2d - center
                        extended_vectors = vectors * 1.3  # Mehr Padding für AR-Effekt
                        extended_corners = center + extended_vectors
                        extended_corners = extended_corners.astype(np.int32)
                        
                        # Glowing Effect - mehrere Linien mit verschiedener Dicke
                        cv2.polylines(frame, [extended_corners], True, box_color, 6)
                        cv2.polylines(frame, [extended_corners], True, (255, 255, 255), 3)
                        cv2.polylines(frame, [corners_2d], True, (255, 255, 255), 2)
                        
                        # AR-style Center mit Glow
                        cv2.circle(frame, (center_x, center_y), 12, box_color, -1)
                        cv2.circle(frame, (center_x, center_y), 15, (255, 255, 255), 3)
                        cv2.circle(frame, (center_x, center_y), 8, (0, 0, 0), -1)
                        
                        # AR-Label mit Glow-Effekt
                        text_size = cv2.getTextSize(component_name, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                        box_bottom = np.max(extended_corners[:, 1])
                        label_x = center_x - text_size[0] // 2
                        label_y = box_bottom + 35
                        
                        # Grenze prüfen
                        if label_y > h - 40:
                            box_top = np.min(extended_corners[:, 1])
                            label_y = box_top - 15
                        label_x = max(10, min(label_x, w - text_size[0] - 10))
                        
                        # AR-Label-Hintergrund mit Glow
                        label_bg_x1 = label_x - 15
                        label_bg_y1 = label_y - text_size[1] - 12
                        label_bg_x2 = label_x + text_size[0] + 15
                        label_bg_y2 = label_y + 12
                        
                        # Glow-Effekt für Label
                        for thickness in [12, 8, 4]:
                            alpha = 0.3 - (thickness * 0.02)
                            overlay = frame.copy()
                            cv2.rectangle(overlay, (label_bg_x1-thickness//2, label_bg_y1-thickness//2), 
                                        (label_bg_x2+thickness//2, label_bg_y2+thickness//2), box_color, -1)
                            cv2.addWeighted(frame, 1-alpha, overlay, alpha, 0, frame)
                        
                        # Label-Box
                        cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), (0, 0, 0), -1)
                        cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), box_color, 3)
                        
                        # Text mit Glow
                        cv2.putText(frame, component_name, (label_x, label_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)  # Shadow
                        cv2.putText(frame, component_name, (label_x, label_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)
                    
                    if self.settings['show_ids']:
                        # AR-style ID mit Glow
                        id_text = f"#{marker_id}"
                        cv2.putText(frame, id_text, (center_x - 25, center_y - 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4)  # Shadow
                        cv2.putText(frame, id_text, (center_x - 25, center_y - 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
                        cv2.putText(frame, id_text, (center_x - 25, center_y - 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, box_color, 1)
            
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


class TransparentOverlay(QWidget):
    """Transparentes Widget für AR-Overlays"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        """Override um transparenz zu gewährleisten"""
        pass


class AROverlayPanel(TransparentOverlay):
    """Transparentes Overlay für Komponenten-Info"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.detected_components = set()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup transparent overlay UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Container für bessere Sichtbarkeit
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(15, 25, 35, 0.90);
                border: 1px solid rgba(26, 188, 156, 0.6);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        container.setMaximumWidth(360)
        # Entferne feste Höhenbegrenzung für dynamische Anpassung
        container.setMinimumHeight(200)
        container.setSizePolicy(container.sizePolicy().horizontalPolicy(), 
                               QSizePolicy.Policy.Minimum)
        
        container_layout = QVBoxLayout(container)
        
        # Header
        header = QLabel("DETECTED COMPONENTS")
        header.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: rgba(26, 188, 156, 1.0);
                background: transparent;
                border: none;
                padding: 10px 8px;
                letter-spacing: 1px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(header)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                color: rgba(26, 188, 156, 0.3);
                background: rgba(26, 188, 156, 0.3);
                border: none;
                max-height: 1px;
                margin: 5px 10px;
            }
        """)
        container_layout.addWidget(separator)
        
        # Status
        self.status_label = QLabel("Scanning...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(149, 165, 166, 1.0);
                background: transparent;
                border: none;
                font-size: 11px;
                padding: 5px 8px;
                font-style: italic;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        # Fortschritt
        self.progress_label = QLabel("Progress: 0/6")
        self.progress_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.progress_label.setStyleSheet("""
            QLabel {
                color: rgba(189, 195, 199, 1.0);
                background: transparent;
                border: none;
                padding: 8px;
                margin-top: 5px;
            }
        """)
        container_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(52, 73, 94, 0.6);
                border-radius: 6px;
                text-align: center;
                color: white;
                background: rgba(44, 62, 80, 0.4);
                font-weight: bold;
                font-size: 10px;
                height: 20px;
                margin: 5px 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(26, 188, 156, 0.9), stop:1 rgba(22, 160, 133, 0.9));
                border-radius: 5px;
                margin: 1px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Komponenten-Liste (kompakt und scrollbar)
        self.components_display = QLabel("")
        self.components_display.setStyleSheet("""
            QLabel {
                color: rgba(236, 240, 241, 1.0);
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(26, 188, 156, 0.2);
                border-radius: 6px;
                padding: 10px;
                font-size: 10px;
                line-height: 1.2;
                margin: 5px;
            }
        """)
        self.components_display.setWordWrap(True)
        self.components_display.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Dynamische Mindesthöhe basierend auf Inhalt
        self.components_display.setMinimumHeight(60)
        container_layout.addWidget(self.components_display)
        
        layout.addWidget(container)
        layout.addStretch()
        
    def update_components(self, markers):
        """Update mit echten Erkennungsdaten"""
        component_labels = {
            0: "Arduino Leonardo",
            1: "Breadboard", 
            2: "LED",
            3: "220Ω Resistor",
            4: "Potentiometer",
            5: "Jumper Wires"
        }
        
        # Erkannte Komponenten sammeln
        current_components = set()
        for marker_id, _, _, _ in markers:
            if marker_id in component_labels:
                current_components.add(marker_id)
        
        # Nur aktualisieren wenn sich was geändert hat
        if current_components != self.detected_components:
            self.detected_components = current_components
            
            # Kompakte Liste erstellen mit allen Komponenten
            component_text_lines = []
            
            # Zeige alle verfügbaren Komponenten mit Status
            for component_id in sorted(component_labels.keys()):
                name = component_labels[component_id]
                is_detected = component_id in current_components
                
                if is_detected:
                    # Verkürze Namen für bessere Darstellung
                    if len(name) > 18:
                        name = name[:15] + "..."
                    component_text_lines.append(f"✓ {name}")
                else:
                    # Verkürze Namen für bessere Darstellung
                    if len(name) > 18:
                        name = name[:15] + "..."
                    component_text_lines.append(f"○ {name}")
            
            # Kombiniere alle Zeilen
            if component_text_lines:
                all_components_text = "\n".join(component_text_lines)
                self.components_display.setText(all_components_text)
            else:
                self.components_display.setText("No components available.")
            
            # Passe die Höhe dynamisch an den Inhalt an
            font_metrics = self.components_display.fontMetrics()
            text_height = font_metrics.boundingRect(self.components_display.rect(), 
                                                   Qt.TextFlag.TextWordWrap, 
                                                   self.components_display.text()).height()
            self.components_display.setMinimumHeight(max(60, text_height + 20))
            
            # Fortschritt aktualisieren
            count = len(current_components)
            self.progress_bar.setValue(count)
            self.progress_label.setText(f"Progress: {count}/6 components")
            
            # Status aktualisieren mit modernen Texten
            if count == 6:
                self.status_label.setText("All components detected!")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: rgba(46, 204, 113, 1.0);
                        background: transparent;
                        border: none;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 5px 8px;
                    }
                """)
            elif count >= 4:
                self.status_label.setText("Almost complete...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: rgba(243, 156, 18, 1.0);
                        background: transparent;
                        border: none;
                        font-size: 11px;
                        padding: 5px 8px;
                    }
                """)
            elif count >= 2:
                self.status_label.setText("Good progress...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: rgba(52, 152, 219, 1.0);
                        background: transparent;
                        border: none;
                        font-size: 11px;
                        padding: 5px 8px;
                    }
                """)
            elif count >= 1:
                self.status_label.setText("Detection active...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: rgba(155, 89, 182, 1.0);
                        background: transparent;
                        border: none;
                        font-size: 11px;
                        padding: 5px 8px;
                    }
                """)
            else:
                self.status_label.setText("Scanning...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: rgba(149, 165, 166, 1.0);
                        background: transparent;
                        border: none;
                        font-size: 11px;
                        padding: 5px 8px;
                        font-style: italic;
                    }
                """)


class ARControlOverlay(TransparentOverlay):
    """Transparentes Overlay für Kontroll-Buttons"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup control overlay"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addStretch()
        
        # Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(44, 62, 80, 0.90);
                border: 1px solid rgba(149, 165, 166, 0.4);
                border-radius: 20px;
                padding: 12px;
            }
        """)
        container.setMaximumHeight(50)
        
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(15, 8, 15, 8)
        container_layout.setSpacing(12)
        
        # Toggle Buttons
        button_style = """
            QPushButton {
                background: rgba(52, 73, 94, 0.8);
                border: 1px solid rgba(149, 165, 166, 0.4);
                border-radius: 15px;
                color: rgba(236, 240, 241, 1.0);
                font-weight: 500;
                font-size: 10px;
                padding: 6px 12px;
                min-width: 70px;
                max-height: 30px;
            }
            QPushButton:hover {
                background: rgba(149, 165, 166, 0.2);
                border-color: rgba(236, 240, 241, 0.6);
            }
            QPushButton:checked {
                background: rgba(26, 188, 156, 0.8);
                border-color: rgba(26, 188, 156, 1.0);
                color: white;
            }
        """
        
        self.markers_btn = QPushButton("MARKERS")
        self.markers_btn.setCheckable(True)
        self.markers_btn.setChecked(True)
        self.markers_btn.setStyleSheet(button_style)
        self.markers_btn.clicked.connect(self.emit_settings)
        container_layout.addWidget(self.markers_btn)
        
        self.ids_btn = QPushButton("IDs")
        self.ids_btn.setCheckable(True)
        self.ids_btn.setChecked(True)
        self.ids_btn.setStyleSheet(button_style)
        self.ids_btn.clicked.connect(self.emit_settings)
        container_layout.addWidget(self.ids_btn)
        
        # Info Button
        info_btn = QPushButton("INFO")
        info_btn.setStyleSheet("""
            QPushButton {
                background: rgba(52, 152, 219, 0.8);
                border: 1px solid rgba(52, 152, 219, 1.0);
                border-radius: 15px;
                color: white;
                font-weight: 500;
                font-size: 10px;
                min-width: 50px;
                max-width: 50px;
                max-height: 30px;
                padding: 6px;
            }
            QPushButton:hover {
                background: rgba(52, 152, 219, 1.0);
            }
        """)
        container_layout.addWidget(info_btn)
        
        layout.addWidget(container)
        
    def emit_settings(self):
        """Emit current settings"""
        settings = {
            'show_markers': self.markers_btn.isChecked(),
            'show_ids': self.ids_btn.isChecked(),
            'target_fps': 30  # Fixed für diese Version
        }
        self.settings_changed.emit(settings)


class FullscreenARWindow(QMainWindow):
    """Hauptfenster mit Fullscreen Kamera-Feed und transparenten Overlays"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup fullscreen UI mit Overlays"""
        self.setWindowTitle("🎥 Fullscreen AR with Transparent Overlays")
        self.setMinimumSize(1200, 800)
        
        # Central widget für Kamera-Feed
        self.camera_label = QLabel()
        self.setCentralWidget(self.camera_label)
        
        # Kamera-Label füllt das gesamte Fenster
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: none;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setText("🎥 Initializing Fullscreen AR Camera...")
        self.camera_label.setScaledContents(False)
        
        # Transparente Overlays
        self.setup_overlays()
        
    def setup_overlays(self):
        """Setup transparente AR-Overlays"""
        # Komponenten-Overlay (links oben)
        self.components_overlay = AROverlayPanel(self.camera_label)
        self.components_overlay.setGeometry(0, 0, 370, 320)
        
        # Control-Overlay (unten zentriert)
        self.control_overlay = ARControlOverlay(self.camera_label)
        
        # Verbinde Settings
        self.control_overlay.settings_changed.connect(self.update_camera_settings)
        
    def setup_camera(self):
        """Initialize camera processing"""
        self.camera_thread = AROverlayCameraThread()
        self.camera_thread.frame_ready.connect(self.update_display)
        
        # Starte Kamera-Thread
        self.camera_thread.start()
        
        print("🚀 Fullscreen AR Application gestartet!")
        
    def update_camera_settings(self, settings):
        """Update camera settings"""
        if hasattr(self, 'camera_thread'):
            self.camera_thread.update_settings(settings)
        
    def update_display(self, frame, markers, fps, frame_time):
        """Update camera display und alle Overlays"""
        # Convert frame to Qt format
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        # Scale to fill the entire window while maintaining aspect ratio
        label_size = self.camera_label.size()
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fill window (kann etwas abgeschnitten werden)
        scaled_pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                    Qt.TransformationMode.SmoothTransformation)
        
        # Center the pixmap if it's larger than the label
        if scaled_pixmap.width() > label_size.width() or scaled_pixmap.height() > label_size.height():
            x = (scaled_pixmap.width() - label_size.width()) // 2
            y = (scaled_pixmap.height() - label_size.height()) // 2
            scaled_pixmap = scaled_pixmap.copy(x, y, label_size.width(), label_size.height())
        
        self.camera_label.setPixmap(scaled_pixmap)
        
        # Update Overlays
        self.components_overlay.update_components(markers)
        
        # Position overlays dynamically
        self.position_overlays()
        
    def position_overlays(self):
        """Position overlays basierend auf Fenster-Größe"""
        window_size = self.size()
        
        # Components overlay - links oben mit etwas mehr Abstand
        self.components_overlay.setGeometry(25, 25, 360, 320)
        
        # Control overlay - unten zentriert mit modernen Proportionen
        control_width = 240
        control_height = 50
        control_x = (window_size.width() - control_width) // 2
        control_y = window_size.height() - control_height - 25
        self.control_overlay.setGeometry(control_x, control_y, control_width, control_height)
        
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        if hasattr(self, 'components_overlay'):
            self.position_overlays()
        
    def closeEvent(self, event):
        """Handle application closing"""
        print("🛑 Schließe Fullscreen AR Anwendung...")
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Apply dark theme als Basis
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("Fullscreen AR with Transparent Overlays")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = FullscreenARWindow()
    window.show()
    
    print("🎥 Fullscreen AR Application mit transparenten Overlays!")
    print("✨ Kamera-Feed füllt das gesamte Fenster")
    print("🎯 AR-Overlays erscheinen direkt im Kamerabild") 
    print("🔍 Echte ArUco-Marker-Erkennung in Echtzeit")
    print("⚙️ Interaktive Overlay-Kontrollen")
    print("📊 Live-Performance-Monitoring")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
