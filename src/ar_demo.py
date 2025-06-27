#!/usr/bin/env python3
"""
Modern AR UI Demo - Works without camera for demonstration
Shows the modern PyQt6 interface with simulated AR data
"""
import sys
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QProgressBar, 
                            QListWidget, QListWidgetItem, QCheckBox, QSlider, 
                            QGroupBox, QTextEdit)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush
import qdarktheme
import qtawesome as qta


class SimulatedARWidget(QLabel):
    """Simulated AR display for demo purposes"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                border: 3px solid #1ABC9C;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2C3E50, stop:1 #34495E);
                color: #1ABC9C;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a demo pixmap
        self.create_demo_display()
        
    def create_demo_display(self):
        """Create a demo AR display"""
        # Create a pixmap with simulated AR content
        pixmap = QPixmap(640, 480)
        pixmap.fill(QColor(44, 62, 80))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw simulated markers
        pen = QPen(QColor(26, 188, 156), 3)
        painter.setPen(pen)
        
        # Marker 1 - Arduino
        painter.drawRect(150, 150, 80, 80)
        painter.drawText(155, 240, "Arduino (ID:0)")
        
        # Marker 2 - LED
        painter.drawRect(350, 200, 60, 60)
        painter.drawText(355, 270, "LED (ID:2)")
        
        # Marker 3 - Breadboard
        painter.drawRect(200, 300, 100, 60)
        painter.drawText(205, 370, "Breadboard (ID:1)")
        
        # Add title
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(200, 50, "🚀 Modern AR Interface Demo")
        
        # Add status
        painter.setFont(QFont("Arial", 12))
        painter.drawText(20, 450, "📋 Demo Mode - Simulated AR Detection")
        
        painter.end()
        self.setPixmap(pixmap)


class DemoComponentsPanel(QFrame):
    """Demo components panel with animated updates"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_detection)
        self.timer.start(2000)  # Update every 2 seconds
        self.detected_count = 0
        
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
                padding: 12px;
                margin: 4px;
                border-radius: 10px;
                background: rgba(26, 188, 156, 0.1);
                border: 1px solid rgba(26, 188, 156, 0.2);
            }
            QListWidget::item:selected {
                background: rgba(26, 188, 156, 0.3);
                border: 1px solid #1ABC9C;
            }
        """)
        layout.addWidget(self.components_list)
        
        # Progress section
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
        
        self.status_label = QLabel("Scanning for components...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #F39C12; font-size: 10px; border: none;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_frame)
        
    def simulate_detection(self):
        """Simulate component detection"""
        components = [
            ("Arduino Leonardo", "fa.microchip", "#E74C3C"),
            ("LED", "fa.lightbulb", "#F1C40F"),
            ("Breadboard", "fa.th", "#3498DB"),
            ("220Ω Resistor", "fa.minus", "#E67E22"),
            ("Potentiometer", "fa.adjust", "#9B59B6"),
            ("Jumper Wires", "fa.exchange", "#2ECC71")
        ]
        
        if self.detected_count < len(components):
            # Add next component
            name, icon_name, color = components[self.detected_count]
            item = QListWidgetItem(f"  {name} (ID: {self.detected_count})")
            item.setIcon(qta.icon(icon_name, color=color))
            self.components_list.addItem(item)
            
            self.detected_count += 1
            
            # Update progress
            self.progress_bar.setValue(self.detected_count)
            self.progress_label.setText(f"Progress: {self.detected_count}/6 Components")
            
            # Update status
            if self.detected_count == 6:
                self.status_label.setText("🎉 All components detected!")
                self.status_label.setStyleSheet("color: #2ECC71; font-size: 11px; font-weight: bold; border: none;")
                self.timer.stop()
            elif self.detected_count >= 4:
                self.status_label.setText("Almost there! Keep going...")
                self.status_label.setStyleSheet("color: #F39C12; font-size: 10px; border: none;")
            else:
                self.status_label.setText("Good progress, continue...")
                self.status_label.setStyleSheet("color: #3498DB; font-size: 10px; border: none;")


class DemoControlPanel(QFrame):
    """Demo control panel showing modern UI elements"""
    
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
        
        # Detection quality
        quality_group = QGroupBox("Detection Quality")
        quality_group.setStyleSheet("""
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
        
        quality_layout = QVBoxLayout(quality_group)
        
        quality_slider = QSlider(Qt.Orientation.Horizontal)
        quality_slider.setRange(1, 5)
        quality_slider.setValue(4)
        quality_slider.setStyleSheet("""
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
        quality_layout.addWidget(quality_slider)
        
        quality_label = QLabel("High Quality")
        quality_label.setStyleSheet("color: #BBE1FA; font-size: 10px; text-align: center;")
        quality_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quality_layout.addWidget(quality_label)
        
        layout.addWidget(quality_group)
        
        # Display options
        display_group = QGroupBox("Display Options")
        display_group.setStyleSheet(quality_group.styleSheet())
        
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
        
        markers_cb = QCheckBox("Show Marker Boundaries")
        markers_cb.setChecked(True)
        markers_cb.setStyleSheet(checkbox_style)
        display_layout.addWidget(markers_cb)
        
        ids_cb = QCheckBox("Show Marker IDs")
        ids_cb.setChecked(True)
        ids_cb.setStyleSheet(checkbox_style)
        display_layout.addWidget(ids_cb)
        
        layout.addWidget(display_group)
        
        # Stats
        stats_group = QGroupBox("Performance Stats")
        stats_group.setStyleSheet(quality_group.styleSheet())
        
        stats_layout = QVBoxLayout(stats_group)
        
        fps_label = QLabel("FPS: 30.0")
        markers_label = QLabel("Markers: 3")
        quality_label = QLabel("Quality: Excellent")
        
        for label in [fps_label, markers_label, quality_label]:
            label.setStyleSheet("color: #BBE1FA; font-size: 10px;")
            stats_layout.addWidget(label)
            
        layout.addWidget(stats_group)
        
        # Demo info
        info_text = QTextEdit()
        info_text.setFixedHeight(120)
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
            "🎯 DEMO MODE\n\n"
            "This is a demonstration of the modern PyQt6 AR interface. "
            "The actual version would connect to your camera and perform "
            "real-time ArUco marker detection.\n\n"
            "Features:\n"
            "• Modern dark theme\n"
            "• Animated components\n"
            "• Real-time controls\n"
            "• Performance monitoring"
        )
        layout.addWidget(info_text)
        
        layout.addStretch()


class ModernARDemoWindow(QMainWindow):
    """Demo window showing the modern AR interface"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup demo UI"""
        self.setWindowTitle("🚀 Modern AR Electronics Tutorial - Demo Mode")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(qta.icon('fa.eye'))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        self.control_panel = DemoControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # Center-left panel - Components
        self.components_panel = DemoComponentsPanel()
        main_layout.addWidget(self.components_panel)
        
        # Center - AR Display
        center_layout = QVBoxLayout()
        
        self.ar_widget = SimulatedARWidget()
        center_layout.addWidget(self.ar_widget)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setFixedHeight(60)
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C3E50, stop:1 #34495E);
                border-top: 2px solid #1ABC9C;
                border-radius: 5px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        fps_label = QLabel("FPS: 30.0")
        fps_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        fps_label.setStyleSheet("color: #1ABC9C; padding: 5px;")
        
        status_label = QLabel("● Demo Mode Active")
        status_label.setFont(QFont("Arial", 10))
        status_label.setStyleSheet("color: #F39C12; padding: 5px;")
        
        quit_btn = QPushButton("❌ Exit Demo")
        quit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E74C3C, stop:1 #C0392B);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EC7063, stop:1 #E74C3C);
            }
        """)
        quit_btn.clicked.connect(self.close)
        
        status_layout.addWidget(fps_label)
        status_layout.addStretch()
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        status_layout.addWidget(quit_btn)
        
        center_layout.addWidget(status_frame)
        main_layout.addLayout(center_layout)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Control panel
        main_layout.setStretch(1, 1)  # Components panel
        main_layout.setStretch(2, 3)  # AR display


def main():
    """Main demo entry point"""
    app = QApplication(sys.argv)
    
    # Apply modern dark theme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("Modern AR Electronics Tutorial - Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    window = ModernARDemoWindow()
    window.show()
    
    print("🎯 Modern AR Interface Demo Started!")
    print("✨ This demonstrates the PyQt6 UI without requiring a camera")
    print("🔄 Components will be detected automatically every 2 seconds")
    print("⚙️ Explore the modern interface and controls")
    print("❌ Close the window or click 'Exit Demo' to quit")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
