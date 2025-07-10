#!/usr/bin/env python3
"""
AR Electronics Tutorial - Modern UI Launcher
Choose between different AR visualization modes
"""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QTextEdit,
                            QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QFont, QPixmap, QIcon
import qdarktheme
import qtawesome as qta


class ModernLauncher(QMainWindow):
    """Modern launcher for AR applications"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup launcher UI"""
        self.setWindowTitle("AR Electronics Tutorial - Modern Launcher")
        self.setFixedSize(800, 600)
        # self.setWindowIcon(qta.icon('fa.rocket'))  # Commented out due to icon issue
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🚀 AR Electronics Tutorial")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Modern Augmented Reality Interface")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #E8EAF6; border: none;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_frame)
        
        # Options section
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background: #2C3E50;
                border: 2px solid #3498DB;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        options_layout = QVBoxLayout(options_frame)
        
        options_title = QLabel("Choose Your AR Experience:")
        options_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        options_title.setStyleSheet("color: #3498DB; border: none; margin-bottom: 15px;")
        options_layout.addWidget(options_title)
        
        # Radio button group
        self.button_group = QButtonGroup()
        
        # Option 1: Fullscreen AR with Overlays (NEW!)
        option1_frame = self.create_option_frame(
            "🎯 Fullscreen AR with Overlays (NEW!)",
            "🎥 Camera fills entire window with transparent overlays\n"
            "• AR-style transparent UI elements\n"
            "• Fullscreen immersive experience\n"
            "• Live component detection overlays\n"
            "• Modern floating controls",
            "fullscreen_ar_overlay.py"
        )
        options_layout.addWidget(option1_frame)
        
        # Option 2: Real Camera Modern UI
        option2_frame = self.create_option_frame(
            "Real Camera Modern UI",
            "� PyQt6 interface with your real camera\n"
            "• Live ArUco marker detection\n"
            "• Real-time component recognition\n"
            "• Modern controls and monitoring\n"
            "• Uses your Logitech HD camera",
            "real_ar_modern.py"
        )
        options_layout.addWidget(option2_frame)
        
        # Option 3: Enhanced Modern UI (Demo)
        option3_frame = self.create_option_frame(
            "Enhanced Modern UI (Demo)",
            "🎨 Full PyQt6 interface with advanced controls\n"
            "• Real-time performance monitoring\n"
            "• Configurable detection settings\n"
            "• Animated progress indicators\n"
            "• Modern dark theme (simulated data)",
            "enhanced_ar_modern.py"
        )
        options_layout.addWidget(option3_frame)
        
        # Option 4: Simple Demo UI
        option4_frame = self.create_option_frame(
            "Simple Demo UI (No Camera)",
            "🎯 PyQt6 interface demonstration\n"
            "• Shows modern UI without camera\n"
            "• Simulated component detection\n"
            "• Interactive controls demonstration\n"
            "• Perfect for testing UI",
            "ar_demo_simple.py"
        )
        options_layout.addWidget(option4_frame)
        
        # Option 5: Original OpenCV
        option5_frame = self.create_option_frame(
            "Original OpenCV Version",
            "⚡ High-performance OpenCV-only interface\n"
            "• Ultra-fast processing\n"
            "• Minimal UI overhead\n"
            "• Maximum compatibility\n"
            "• Traditional AR overlay",
            "main.py"
        )
        options_layout.addWidget(option5_frame)
        
        main_layout.addWidget(options_frame)
        
        # Launch buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        self.launch_btn = QPushButton("🚀 Launch AR Application")
        self.launch_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.launch_btn.setFixedHeight(50)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1ABC9C, stop:1 #16A085);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #48C9B0, stop:1 #1ABC9C);
            }
            QPushButton:pressed {
                background: #148F77;
            }
            QPushButton:disabled {
                background: #7F8C8D;
                color: #BDC3C7;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_application)
        self.launch_btn.setEnabled(False)
        
        exit_btn = QPushButton("❌ Exit")
        exit_btn.setFont(QFont("Arial", 12))
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E74C3C, stop:1 #C0392B);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EC7063, stop:1 #E74C3C);
            }
            QPushButton:pressed {
                background: #A93226;
            }
        """)
        exit_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.launch_btn)
        button_layout.addWidget(exit_btn)
        
        main_layout.addWidget(button_frame)
        
        # Default selection
        self.button_group.buttons()[0].setChecked(True)
        self.launch_btn.setEnabled(True)
        
    def create_option_frame(self, title, description, script):
        """Create an option selection frame"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 73, 94, 0.5);
                border: 1px solid #34495E;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background: rgba(52, 73, 94, 0.7);
                border: 1px solid #3498DB;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        # Radio button
        radio = QRadioButton()
        radio.setStyleSheet("""
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498DB;
                border-radius: 9px;
                background: #2C3E50;
            }
            QRadioButton::indicator:checked {
                background: #3498DB;
                border: 2px solid #2980B9;
            }
        """)
        radio.toggled.connect(lambda checked: self.launch_btn.setEnabled(True))
        
        # Store script path in radio button
        radio.script = script
        self.button_group.addButton(radio)
        
        layout.addWidget(radio)
        
        # Content
        content_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3498DB; border: none;")
        content_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #BDC3C7; border: none;")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout)
        
        return frame
        
    def launch_application(self):
        """Launch selected AR application"""
        # Get selected script
        selected_script = None
        for button in self.button_group.buttons():
            if button.isChecked():
                selected_script = button.script
                break
                
        if not selected_script:
            QMessageBox.warning(self, "No Selection", "Please select an AR mode first.")
            return
            
        # Check if file exists
        script_path = os.path.join(os.path.dirname(__file__), selected_script)
        if not os.path.exists(script_path):
            QMessageBox.critical(self, "File Not Found", f"Script not found: {selected_script}")
            return
            
        try:
            # Launch the selected application
            if selected_script.endswith('.py'):
                # For Python scripts, use the current Python interpreter
                process = QProcess()
                process.start(sys.executable, [script_path])
                
                if process.waitForStarted(3000):
                    QMessageBox.information(self, "Launched", f"AR application started!\nScript: {selected_script}")
                    self.close()
                else:
                    QMessageBox.critical(self, "Launch Failed", "Failed to start the AR application.")
            else:
                QMessageBox.critical(self, "Invalid File", "Selected file is not a Python script.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch application:\n{str(e)}")


def main():
    """Main launcher entry point"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    
    # Set application properties
    app.setApplicationName("AR Electronics Tutorial Launcher")
    app.setApplicationVersion("1.0")
    
    # Create and show launcher
    launcher = ModernLauncher()
    launcher.show()
    
    print("🎯 AR Electronics Tutorial Launcher")
    print("Choose your preferred AR interface:")
    print("1. Enhanced Modern UI - Full PyQt6 with advanced features")
    print("2. Classic PyQt6 UI - Clean and elegant interface") 
    print("3. Original OpenCV - High-performance traditional AR")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
