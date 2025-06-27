#!/usr/bin/env python3
"""
Modern AR Application with PyQt6 UI - Beautiful, Performance-focused Overlay
"""
import sys
import cv2
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QScrollArea,
                            QProgressBar, QListWidget, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush
import qdarktheme
import qtawesome as qta

from camera_utils import get_logitech_camera_optimized


class ModernARWidget(QLabel):
    """Custom widget for AR video display with overlays"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #2C3E50;
                border-radius: 10px;
                background-color: #34495E;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Initializing Camera...")
        
        # AR data
        self.markers = []
        self.fps = 0.0
        
    def update_frame(self, cv_image, markers, fps):
        """Update the display with new frame and marker data"""
        self.markers = markers
        self.fps = fps
        
        # Convert OpenCV image to Qt format
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        
        # Convert to pixmap and scale
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.setPixmap(scaled_pixmap)


class ComponentsPanel(QFrame):
    """Modern components detection panel"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.detected_components = set()
        
    def setup_ui(self):
        self.setFixedWidth(300)
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
                padding: 10px;
                background: transparent;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Components list
        self.components_list = QListWidget()
        self.components_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #ECF0F1;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 8px;
                background: rgba(26, 188, 156, 0.1);
            }
            QListWidget::item:selected {
                background: rgba(26, 188, 156, 0.3);
            }
        """)
        layout.addWidget(self.components_list)
        
        # Progress section
        self.progress_label = QLabel("Progress: 0/6 Components")
        self.progress_label.setStyleSheet("color: #BDC3C7; font-size: 11px; border: none;")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495E;
                border-radius: 8px;
                text-align: center;
                color: white;
                background: #2C3E50;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1ABC9C, stop:1 #16A085);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
    def update_components(self, markers):
        """Update detected components list"""
        component_labels = {
            0: "Arduino Leonardo",
            1: "Breadboard", 
            2: "LED",
            3: "220Ω Resistor",
            4: "Potentiometer",
            5: "Jumper Wires"
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
                name = component_labels[component_id]
                item = QListWidgetItem(f"✅ {name} (ID: {component_id})")
                item.setIcon(qta.icon('fa.check-circle', color='#1ABC9C'))
                self.components_list.addItem(item)
            
            # Update progress
            count = len(current_components)
            self.progress_bar.setValue(count)
            self.progress_label.setText(f"Progress: {count}/6 Components")


class InstructionsPanel(QFrame):
    """Modern step-by-step instructions panel"""
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedWidth(350)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8E44AD, stop:1 #9B59B6);
                border: 1px solid #E74C3C;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 ASSEMBLY INSTRUCTIONS")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #E74C3C;
                border: none;
                padding: 10px;
                background: transparent;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Current step
        self.step_label = QLabel("Step 1 of 5")
        self.step_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.step_label.setStyleSheet("color: #ECF0F1; border: none;")
        layout.addWidget(self.step_label)
        
        # Instruction text
        self.instruction_text = QLabel()
        self.instruction_text.setWordWrap(True)
        self.instruction_text.setStyleSheet("""
            QLabel {
                color: #ECF0F1;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.instruction_text)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.setIcon(qta.icon('fa.arrow-left', color='white'))
        self.prev_btn.clicked.connect(self.previous_step)
        
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.setIcon(qta.icon('fa.arrow-right', color='white'))
        self.next_btn.clicked.connect(self.next_step)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #E74C3C, stop:1 #C0392B);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #EC7063, stop:1 #D32F2F);
                }
                QPushButton:pressed {
                    background: #A93226;
                }
            """)
        
        button_layout.addWidget(self.prev_btn)
        button_layout.addWidget(self.next_btn)
        layout.addLayout(button_layout)
        
        self.update_instruction()
        
    def update_instruction(self):
        """Update instruction display"""
        instructions = [
            "Place the Arduino Leonardo on your workspace and ensure it's clearly visible to the camera.",
            "Position the breadboard next to the Arduino with good lighting for marker detection.",
            "Connect the LED to the breadboard using the appropriate pins as shown in the diagram.",
            "Add the 220Ω resistor in series with the LED to protect it from overcurrent.",
            "Connect jumper wires between Arduino and breadboard according to the circuit schematic."
        ]
        
        if 0 <= self.current_step < len(instructions):
            self.step_label.setText(f"Step {self.current_step + 1} of {len(instructions)}")
            self.instruction_text.setText(instructions[self.current_step])
            
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setEnabled(self.current_step < len(instructions) - 1)
        
    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_instruction()
            
    def next_step(self):
        if self.current_step < 4:  # 5 steps total
            self.current_step += 1
            self.update_instruction()


class StatusBar(QFrame):
    """Modern status bar with FPS and other info"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C3E50, stop:1 #34495E);
                border-top: 2px solid #1ABC9C;
            }
        """)
        
        layout = QHBoxLayout(self)
        
        # FPS display
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.fps_label.setStyleSheet("color: #1ABC9C; padding: 5px;")
        
        # Status indicator
        self.status_label = QLabel("● Camera Active")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #2ECC71; padding: 5px;")
        
        # Performance indicator
        self.perf_label = QLabel("Performance: Good")
        self.perf_label.setFont(QFont("Arial", 10))
        self.perf_label.setStyleSheet("color: #F39C12; padding: 5px;")
        
        layout.addWidget(self.fps_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.perf_label)
        
    def update_status(self, fps, marker_count):
        """Update status bar information"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
        # Update performance indicator based on FPS
        if fps > 25:
            self.perf_label.setText("Performance: Excellent")
            self.perf_label.setStyleSheet("color: #2ECC71; padding: 5px;")
        elif fps > 15:
            self.perf_label.setText("Performance: Good")
            self.perf_label.setStyleSheet("color: #F39C12; padding: 5px;")
        else:
            self.perf_label.setText("Performance: Low")
            self.perf_label.setStyleSheet("color: #E74C3C; padding: 5px;")
            
        # Update status
        if marker_count > 0:
            self.status_label.setText(f"● {marker_count} Markers Detected")
            self.status_label.setStyleSheet("color: #2ECC71; padding: 5px;")
        else:
            self.status_label.setText("○ No Markers Detected")
            self.status_label.setStyleSheet("color: #E67E22; padding: 5px;")


class CameraThread(QThread):
    """Background thread for camera processing"""
    
    frame_ready = pyqtSignal(np.ndarray, list, float)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.mutex = QMutex()
        
    def run(self):
        """Main camera processing loop"""
        # Initialize camera
        cap = get_logitech_camera_optimized()
        if cap is None:
            print("Error: Could not initialize camera")
            return
            
        # ArUco setup
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        aruco_params = cv2.aruco.DetectorParameters()
        
        # Optimized parameters
        aruco_params.adaptiveThreshWinSizeMin = 5
        aruco_params.adaptiveThreshWinSizeMax = 15
        aruco_params.adaptiveThreshWinSizeStep = 4
        aruco_params.minMarkerPerimeterRate = 0.05
        aruco_params.maxMarkerPerimeterRate = 0.5
        
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Performance tracking
        fps_count = 0
        fps_start = time.time()
        current_fps = 0.0
        
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            fps_count += 1
            
            # ArUco detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)
            
            # Process markers
            markers = []
            if ids is not None:
                for i, corner in enumerate(corners):
                    marker_id = ids[i][0]
                    center_x = int(np.mean(corner[0][:, 0]))
                    center_y = int(np.mean(corner[0][:, 1]))
                    corners_2d = corner[0].astype(np.int32)
                    markers.append((marker_id, center_x, center_y, corners_2d))
                    
                    # Draw markers on frame
                    cv2.polylines(frame, [corners_2d], True, (0, 255, 255), 2)
                    cv2.circle(frame, (center_x, center_y), 8, (0, 255, 0), -1)
                    cv2.putText(frame, f"ID:{marker_id}", (center_x - 20, center_y - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Calculate FPS
            if fps_count >= 30:
                elapsed = time.time() - fps_start
                current_fps = 30 / elapsed if elapsed > 0 else 0
                fps_start = time.time()
                fps_count = 0
            
            # Emit frame with data
            self.frame_ready.emit(frame, markers, current_fps)
            
            # Small delay for stability
            self.msleep(16)  # ~60 FPS max
            
        cap.release()
        
    def stop(self):
        """Stop the camera thread"""
        self.running = False
        self.wait()


class ModernARMainWindow(QMainWindow):
    """Main application window with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Modern AR Electronics Tutorial - PyQt6")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Components
        self.components_panel = ComponentsPanel()
        main_layout.addWidget(self.components_panel)
        
        # Center - AR Video display
        center_layout = QVBoxLayout()
        
        self.ar_widget = ModernARWidget()
        center_layout.addWidget(self.ar_widget)
        
        # Status bar
        self.status_bar = StatusBar()
        center_layout.addWidget(self.status_bar)
        
        main_layout.addLayout(center_layout)
        
        # Right panel - Instructions
        self.instructions_panel = InstructionsPanel()
        main_layout.addWidget(self.instructions_panel)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Components panel
        main_layout.setStretch(1, 3)  # Video display
        main_layout.setStretch(2, 1)  # Instructions panel
        
    def setup_camera(self):
        """Initialize camera processing"""
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_display)
        self.camera_thread.start()
        
    def update_display(self, frame, markers, fps):
        """Update all UI components with new data"""
        # Update AR video display
        self.ar_widget.update_frame(frame, markers, fps)
        
        # Update components panel
        self.components_panel.update_components(markers)
        
        # Update status bar
        self.status_bar.update_status(fps, len(markers))
        
    def closeEvent(self, event):
        """Handle application closing"""
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("Modern AR Electronics Tutorial")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AR Vision Labs")
    
    # Create and show main window
    window = ModernARMainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
