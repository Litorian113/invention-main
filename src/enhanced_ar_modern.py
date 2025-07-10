#!/usr/bin/env python3
"""
Enhanced AR Application - Hybrid approach combining OpenCV AR with PyQt6 modern UI
Maintains the existing AR functionality while adding modern UI elements
"""
import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QProgressBar, 
                            QListWidget, QListWidgetItem, QTextEdit, QCheckBox,
                            QSlider, QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush, QIcon
import qdarktheme
import qtawesome as qta

from camera_utils import get_logitech_camera_optimized


class AnimatedProgressBar(QProgressBar):
    """Animated progress bar with smooth transitions"""
    
    def __init__(self):
        super().__init__()
        self.setRange(0, 6)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setDuration(500)
        
    def animate_to_value(self, value):
        """Animate to target value"""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()


class ModernControlPanel(QFrame):
    """Advanced control panel for AR settings"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedWidth(300)
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
        header = QLabel("⚙️ AR CONTROLS")
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
        
        # Detection Settings Group
        detection_group = QGroupBox("Detection Settings")
        detection_group.setStyleSheet("""
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
        
        detection_layout = QVBoxLayout(detection_group)
        
        # Detection quality slider
        quality_label = QLabel("Detection Quality:")
        quality_label.setStyleSheet("color: #BBE1FA; font-size: 11px;")
        detection_layout.addWidget(quality_label)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 5)
        self.quality_slider.setValue(3)
        self.quality_slider.setStyleSheet("""
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
        self.quality_slider.valueChanged.connect(self.emit_settings)
        detection_layout.addWidget(self.quality_slider)
        
        # Show markers checkbox
        self.show_markers_cb = QCheckBox("Show Marker Boundaries")
        self.show_markers_cb.setChecked(True)
        self.show_markers_cb.setStyleSheet("""
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
        """)
        self.show_markers_cb.stateChanged.connect(self.emit_settings)
        detection_layout.addWidget(self.show_markers_cb)
        
        # Show IDs checkbox
        self.show_ids_cb = QCheckBox("Show Marker IDs")
        self.show_ids_cb.setChecked(True)
        self.show_ids_cb.setStyleSheet(self.show_markers_cb.styleSheet())
        self.show_ids_cb.stateChanged.connect(self.emit_settings)
        detection_layout.addWidget(self.show_ids_cb)
        
        layout.addWidget(detection_group)
        
        # Performance Group
        perf_group = QGroupBox("Performance")
        perf_group.setStyleSheet(detection_group.styleSheet())
        
        perf_layout = QVBoxLayout(perf_group)
        
        # FPS target slider
        fps_label = QLabel("Target FPS:")
        fps_label.setStyleSheet("color: #BBE1FA; font-size: 11px;")
        perf_layout.addWidget(fps_label)
        
        self.fps_slider = QSlider(Qt.Orientation.Horizontal)
        self.fps_slider.setRange(15, 60)
        self.fps_slider.setValue(30)
        self.fps_slider.setStyleSheet(self.quality_slider.styleSheet())
        self.fps_slider.valueChanged.connect(self.emit_settings)
        perf_layout.addWidget(self.fps_slider)
        
        self.fps_value_label = QLabel("30 FPS")
        self.fps_value_label.setStyleSheet("color: #3282B8; font-size: 10px; text-align: center;")
        self.fps_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        perf_layout.addWidget(self.fps_value_label)
        
        self.fps_slider.valueChanged.connect(lambda v: self.fps_value_label.setText(f"{v} FPS"))
        
        layout.addWidget(perf_group)
        
        # Stats display
        stats_group = QGroupBox("Statistics")
        stats_group.setStyleSheet(detection_group.styleSheet())
        
        stats_layout = QVBoxLayout(stats_group)
        
        self.current_fps_label = QLabel("Current FPS: 0.0")
        self.marker_count_label = QLabel("Markers: 0")
        self.frame_time_label = QLabel("Frame Time: 0ms")
        
        for label in [self.current_fps_label, self.marker_count_label, self.frame_time_label]:
            label.setStyleSheet("color: #BBE1FA; font-size: 10px;")
            stats_layout.addWidget(label)
            
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
    def emit_settings(self):
        """Emit current settings"""
        settings = {
            'quality': self.quality_slider.value(),
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


class EnhancedComponentsPanel(QFrame):
    """Enhanced components panel with animations and detailed info"""
    
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
        
        # Header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa.microchip', color='#1ABC9C').pixmap(24, 24))
        
        header = QLabel("DETECTED COMPONENTS")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #1ABC9C;
                border: none;
                background: transparent;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(header)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Components list with enhanced styling
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
            QListWidget::item:selected {
                background: rgba(26, 188, 156, 0.3);
                border: 1px solid #1ABC9C;
            }
        """)
        layout.addWidget(self.components_list)
        
        # Enhanced progress section
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
        
        self.progress_bar = AnimatedProgressBar()
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
        
        # Completion status
        self.completion_label = QLabel("")
        self.completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completion_label.setStyleSheet("color: #F39C12; font-size: 10px; border: none;")
        progress_layout.addWidget(self.completion_label)
        
        layout.addWidget(progress_frame)
        
    def update_components(self, markers):
        """Update detected components with enhanced visuals"""
        component_labels = {
            0: ("Arduino Leonardo", "fa.microchip", "#E74C3C"),
            1: ("Breadboard", "fa.th", "#3498DB"), 
            2: ("LED", "fa.lightbulb", "#F1C40F"),
            3: ("220Ω Resistor", "fa.minus", "#E67E22"),
            4: ("Potentiometer", "fa.adjust", "#9B59B6"),
            5: ("Jumper Wires", "fa.exchange", "#2ECC71")
        }
        
        # Update detected components
        current_components = set()
        for marker_id, _, _, _ in markers:
            if marker_id in component_labels:
                current_components.add(marker_id)
        
        # Only update if changed
        if current_components != self.detected_components:
            self.detected_components = current_components
            
            # Clear and rebuild list
            self.components_list.clear()
            
            for component_id in sorted(current_components):
                name, icon_name, color = component_labels[component_id]
                item = QListWidgetItem(f"  {name} (ID: {component_id})")
                item.setIcon(qta.icon(icon_name, color=color))
                self.components_list.addItem(item)
            
            # Update progress with animation
            count = len(current_components)
            self.progress_bar.animate_to_value(count)
            self.progress_label.setText(f"Progress: {count}/6 Components")
            
            # Update completion status
            if count == 6:
                self.completion_label.setText("🎉 All components detected!")
                self.completion_label.setStyleSheet("color: #2ECC71; font-size: 11px; font-weight: bold; border: none;")
            elif count >= 4:
                self.completion_label.setText("Almost there!")
                self.completion_label.setStyleSheet("color: #F39C12; font-size: 10px; border: none;")
            elif count >= 2:
                self.completion_label.setText("Good progress...")
                self.completion_label.setStyleSheet("color: #3498DB; font-size: 10px; border: none;")
            else:
                self.completion_label.setText("Place components in view")
                self.completion_label.setStyleSheet("color: #95A5A6; font-size: 10px; border: none;")


class EnhancedARThread(QThread):
    """Enhanced camera thread with configurable settings"""
    
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
        """Enhanced camera processing with configurable quality"""
        # Initialize camera
        cap = get_logitech_camera_optimized()
        if cap is None:
            print("Error: Could not initialize camera")
            return
            
        # ArUco setup with quality-based parameters
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        
        self.running = True
        fps_count = 0
        fps_start = time.time()
        current_fps = 0.0
        
        while self.running:
            frame_start = time.time()
            
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            fps_count += 1
            
            # Dynamic ArUco parameters based on quality setting
            aruco_params = cv2.aruco.DetectorParameters()
            quality = self.settings['quality']
            
            if quality == 1:  # Fast
                aruco_params.adaptiveThreshWinSizeMin = 7
                aruco_params.adaptiveThreshWinSizeMax = 13
                aruco_params.minMarkerPerimeterRate = 0.1
                detection_scale = 0.5
            elif quality == 2:  # Balanced Fast
                aruco_params.adaptiveThreshWinSizeMin = 5
                aruco_params.adaptiveThreshWinSizeMax = 15
                aruco_params.minMarkerPerimeterRate = 0.08
                detection_scale = 0.6
            elif quality == 3:  # Balanced
                aruco_params.adaptiveThreshWinSizeMin = 3
                aruco_params.adaptiveThreshWinSizeMax = 20
                aruco_params.minMarkerPerimeterRate = 0.05
                detection_scale = 0.8
            elif quality == 4:  # High Quality
                aruco_params.adaptiveThreshWinSizeMin = 3
                aruco_params.adaptiveThreshWinSizeMax = 25
                aruco_params.minMarkerPerimeterRate = 0.03
                detection_scale = 1.0
            else:  # Ultra High Quality
                aruco_params.adaptiveThreshWinSizeMin = 3
                aruco_params.adaptiveThreshWinSizeMax = 30
                aruco_params.minMarkerPerimeterRate = 0.02
                detection_scale = 1.0
                
            detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
            
            # Scale frame for detection if needed
            h, w = frame.shape[:2]
            if detection_scale < 1.0:
                small_frame = cv2.resize(frame, (int(w * detection_scale), int(h * detection_scale)))
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ArUco detection
            corners, ids, _ = detector.detectMarkers(gray)
            
            # Process markers
            markers = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    
                    # Scale coordinates back if needed
                    if detection_scale < 1.0:
                        scaled_corner = corner / detection_scale
                    else:
                        scaled_corner = corner
                        
                    center_x = int(np.mean(scaled_corner[0][:, 0]))
                    center_y = int(np.mean(scaled_corner[0][:, 1]))
                    corners_2d = scaled_corner[0].astype(np.int32)
                    markers.append((marker_id, center_x, center_y, corners_2d))
                    
                    # Draw markers based on settings
                    if self.settings['show_markers']:
                        # Draw enhanced marker visualization
                        cv2.polylines(frame, [corners_2d], True, (0, 255, 255), 3)
                        cv2.circle(frame, (center_x, center_y), 8, (0, 255, 0), -1)
                        cv2.circle(frame, (center_x, center_y), 12, (255, 255, 255), 2)
                        
                    if self.settings['show_ids']:
                        # Enhanced ID display
                        cv2.putText(frame, f"ID:{marker_id}", (center_x - 25, center_y - 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(frame, f"ID:{marker_id}", (center_x - 25, center_y - 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 1)
            
            # Calculate performance metrics
            frame_time = (time.time() - frame_start) * 1000
            
            # Calculate FPS
            if fps_count >= 30:
                elapsed = time.time() - fps_start
                current_fps = 30 / elapsed if elapsed > 0 else 0
                fps_start = time.time()
                fps_count = 0
            
            # Emit frame with data
            self.frame_ready.emit(frame, markers, current_fps, frame_time)
            
            # Dynamic sleep based on target FPS
            target_frame_time = 1000 / self.settings['target_fps']
            if frame_time < target_frame_time:
                sleep_time = int(target_frame_time - frame_time)
                self.msleep(sleep_time)
            
        cap.release()
        
    def stop(self):
        """Stop the camera thread"""
        self.running = False
        self.wait()


class ModernARMainWindow(QMainWindow):
    """Enhanced main window with modern UI and advanced controls"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the enhanced user interface"""
        self.setWindowTitle("Enhanced AR Electronics Tutorial - Modern UI")
        self.setMinimumSize(1400, 900)
        
        # Set application icon
        self.setWindowIcon(qta.icon('fa.eye'))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        self.control_panel = ModernControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # Center-left panel - Components  
        self.components_panel = EnhancedComponentsPanel()
        main_layout.addWidget(self.components_panel)
        
        # Center - AR Video display
        self.ar_label = QLabel()
        self.ar_label.setMinimumSize(640, 480)
        self.ar_label.setStyleSheet("""
            QLabel {
                border: 3px solid #3282B8;
                border-radius: 15px;
                background-color: #1A1A2E;
            }
        """)
        self.ar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ar_label.setText("Initializing AR Camera...")
        self.ar_label.setFont(QFont("Arial", 16))
        main_layout.addWidget(self.ar_label)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Control panel
        main_layout.setStretch(1, 1)  # Components panel
        main_layout.setStretch(2, 4)  # Video display
        
    def setup_camera(self):
        """Initialize enhanced camera processing"""
        self.camera_thread = EnhancedARThread()
        self.camera_thread.frame_ready.connect(self.update_display)
        self.control_panel.settings_changed.connect(self.camera_thread.update_settings)
        self.camera_thread.start()
        
    def update_display(self, frame, markers, fps, frame_time):
        """Update all UI components with new data"""
        # Convert frame to Qt format and display
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        # Scale to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.ar_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ar_label.setPixmap(scaled_pixmap)
        
        # Update components panel
        self.components_panel.update_components(markers)
        
        # Update control panel stats
        self.control_panel.update_stats(fps, len(markers), frame_time)
        
    def closeEvent(self, event):
        """Handle application closing"""
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Apply modern dark theme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("Enhanced AR Electronics Tutorial")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Modern AR Labs")
    
    # Create and show main window
    window = ModernARMainWindow()
    window.show()
    
    print("🚀 Enhanced AR Application Started!")
    print("✨ Modern PyQt6 UI with advanced controls")
    print("🎯 Real-time performance monitoring")
    print("⚙️ Configurable detection settings")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
