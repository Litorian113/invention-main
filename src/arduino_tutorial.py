import cv2
import numpy as np
import time
from camera_utils import get_logitech_camera_optimized, get_fresh_frame

class ArduinoTutorialSystem:
    """Umfassendes Step-by-Step Arduino Tutorial mit ArUco Marker Erkennung"""
    
    def __init__(self):
        # Komponenten-Validierung Phase
        self.validation_phase = True
        self.validation_complete = False
        
        # Tutorial-Schritte Definition (erweitert auf 10+ Schritte) - Ohne Sonderzeichen
        self.tutorial_steps = [
            {
                "step": 0,
                "phase": "validation",
                "title": "Komponenten-Ueberpruefung",
                "description": "Zeige alle Komponenten gleichzeitig in die Kamera",
                "required_markers": [0, 1, 2, 3, 4, 5],  # Alle Komponenten
                "success_message": "[OK] Alle Komponenten erkannt! Tutorial kann beginnen",
                "instruction": "Lege alle ArUco-Marker sichtbar in das Kamerabild"
            },
            {
                "step": 1,
                "phase": "preparation", 
                "title": "Arbeitsplatz vorbereiten",
                "description": "Arduino und Breadboard positionieren",
                "required_markers": [0, 1],  # Arduino, Breadboard
                "success_message": "[OK] Schritt 1: Grundkomponenten bereit!",
                "instruction": "Platziere Arduino und Breadboard nebeneinander auf dem Arbeitsplatz"
            },
            {
                "step": 2,
                "phase": "power_setup",
                "title": "Stromversorgung vorbereiten", 
                "description": "GND-Verbindung zwischen Arduino und Breadboard",
                "required_markers": [0, 1, 5],  # Arduino, Breadboard, Jumper
                "success_message": "[OK] Schritt 2: Jumper-Kabel fuer GND bereit!",
                "instruction": "Nimm ein Jumper-Kabel fuer die GND-Verbindung zwischen Arduino und Breadboard (-) Schiene"
            },
            {
                "step": 3,
                "phase": "power_setup",
                "title": "5V Stromversorgung",
                "description": "5V-Verbindung von Arduino zu Breadboard",
                "required_markers": [0, 1, 5],  # Arduino, Breadboard, Jumper
                "success_message": "[OK] Schritt 3: 5V-Verbindung hergestellt!",
                "instruction": "Verbinde Arduino 5V mit Breadboard (+) Schiene mit einem weiteren Jumper-Kabel"
            },
            {
                "step": 4,
                "phase": "components",
                "title": "LED einsetzen",
                "description": "LED auf Breadboard platzieren",
                "required_markers": [0, 1, 2],  # Arduino, Breadboard, LED
                "success_message": "[OK] Schritt 4: LED wurde platziert!",
                "instruction": "Stecke die LED in das Breadboard (langes Bein = Anode/+, kurzes Bein = Kathode/-)"
            },
            {
                "step": 5,
                "phase": "components",
                "title": "LED-Schutzwiderstand",
                "description": "220 Ohm Widerstand fuer LED-Schutz hinzufuegen",
                "required_markers": [0, 1, 2, 3],  # Arduino, Breadboard, LED, Resistor
                "success_message": "[OK] Schritt 5: Schutzwiderstand platziert!",
                "instruction": "Platziere den 220 Ohm Widerstand zwischen LED-Kathode (-) und GND-Schiene"
            },
            {
                "step": 6,
                "phase": "connections",
                "title": "LED-Signalverbindung",
                "description": "LED-Anode mit Arduino Digital Pin verbinden",
                "required_markers": [0, 1, 2, 3, 5],  # Alle außer Potentiometer
                "success_message": "[OK] Schritt 6: LED mit Arduino Pin D9 verbunden!",
                "instruction": "Verbinde LED-Anode (+) mit Arduino Digital Pin D9 mit Jumper-Kabel"
            },
            {
                "step": 7,
                "phase": "analog_input",
                "title": "Potentiometer hinzufuegen",
                "description": "Potentiometer fuer analoge Eingabe",
                "required_markers": [0, 1, 2, 3, 4],  # Alle außer Jumper (temporär)
                "success_message": "[OK] Schritt 7: Potentiometer wurde hinzugefuegt!",
                "instruction": "Platziere das Potentiometer auf dem Breadboard"
            },
            {
                "step": 8,
                "phase": "analog_input",
                "title": "Potentiometer GND",
                "description": "Potentiometer GND-Verbindung",
                "required_markers": [0, 1, 2, 3, 4, 5],  # Alle Komponenten
                "success_message": "[OK] Schritt 8: Potentiometer GND verbunden!",
                "instruction": "Verbinde linken Potentiometer-Pin mit GND-Schiene (Jumper-Kabel)"
            },
            {
                "step": 9,
                "phase": "analog_input", 
                "title": "Potentiometer 5V",
                "description": "Potentiometer 5V-Versorgung",
                "required_markers": [0, 1, 2, 3, 4, 5],  # Alle Komponenten
                "success_message": "[OK] Schritt 9: Potentiometer 5V verbunden!",
                "instruction": "Verbinde rechten Potentiometer-Pin mit 5V-Schiene (Jumper-Kabel)"
            },
            {
                "step": 10,
                "phase": "analog_input",
                "title": "Potentiometer Signal",
                "description": "Potentiometer-Signal zu Arduino",
                "required_markers": [0, 1, 2, 3, 4, 5],  # Alle Komponenten
                "success_message": "[OK] Schritt 10: Potentiometer mit Arduino A0 verbunden!",
                "instruction": "Verbinde mittleren Potentiometer-Pin mit Arduino Analog Pin A0"
            },
            {
                "step": 11,
                "phase": "verification",
                "title": "Schaltung vervollstaendigen",
                "description": "Finale Ueberpruefung aller Verbindungen",
                "required_markers": [0, 1, 2, 3, 4, 5],  # Alle Komponenten
                "success_message": "SCHALTUNG VOLLSTAENDIG! Alle Komponenten korrekt verbunden!",
                "instruction": "Ueberpruefe alle Verbindungen - die Schaltung ist bereit fuer den Code-Upload"
            }
        ]
        
        self.current_step = 0
        self.step_completed = [False] * len(self.tutorial_steps)
        self.tutorial_completed = False
        
        # Marker-Namen für bessere Ausgabe (ohne Sonderzeichen)
        self.marker_names = {
            0: "Arduino",
            1: "Breadboard",
            2: "LED",
            3: "220 Ohm Resistor", 
            4: "Potentiometer",
            5: "Jumper Wires"
        }
        
        # Kurze Namen für Marker-Labels
        self.marker_short_names = {
            0: "Arduino",
            1: "Breadboard", 
            2: "LED",
            3: "Resistor",
            4: "Poti",
            5: "Jumper"
        }
        
        # Phasen-Farben
        self.phase_colors = {
            "validation": (255, 165, 0),    # Orange
            "preparation": (0, 255, 255),   # Cyan
            "power_setup": (255, 255, 0),   # Gelb
            "components": (0, 255, 0),      # Grün
            "connections": (255, 0, 255),   # Magenta
            "analog_input": (0, 100, 255),  # Blau
            "verification": (0, 255, 0)     # Grün
        }
        
        # UI-Farben
        self.colors = {
            "success": (0, 255, 0),
            "waiting": (0, 255, 255), 
            "error": (0, 0, 255),
            "info": (255, 255, 0),
            "completed": (128, 255, 128),
            "warning": (0, 165, 255)
        }
        
        # Text-Eigenschaften (VERGRÖSSERT für bessere Lesbarkeit)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale_large = 1.2      # Erhöht von 0.7
        self.font_scale_medium = 0.9     # Erhöht von 0.5  
        self.font_scale_small = 0.7      # Erhöht von 0.4
        self.font_scale_tiny = 0.5       # Erhöht von 0.3
        self.font_thickness_bold = 3     # Erhöht von 2
        self.font_thickness_normal = 2   # Erhöht von 1
        
        # Komponenten-Status für Validierung
        self.components_seen = set()
        self.validation_timer = 0
        self.validation_hold_time = 3.0  # 3 Sekunden alle Komponenten zeigen

    def check_validation_phase(self, detected_markers):
        """Überprüfe die initiale Komponenten-Validierung"""
        if not self.validation_phase:
            return True
            
        detected_marker_ids = set([marker[0] for marker in detected_markers])
        required_markers = set([0, 1, 2, 3, 4, 5])
        
        if required_markers.issubset(detected_marker_ids):
            self.validation_timer += 0.1  # Grober Timer
            
            if self.validation_timer >= self.validation_hold_time:
                self.validation_phase = False
                self.validation_complete = True
                self.current_step = 1  # Springe zu Schritt 1
                print("\n[SUCCESS] Komponenten-Validierung abgeschlossen!")
                print("[INFO] Tutorial startet jetzt...")
                print(f"[NEXT] {self.tutorial_steps[1]['instruction']}")
                return True
        else:
            self.validation_timer = 0  # Reset timer wenn nicht alle da sind
            
        return False

    def check_step_completion(self, detected_markers):
        """Überprüfe ob der aktuelle Schritt abgeschlossen werden kann"""
        if self.validation_phase:
            return self.check_validation_phase(detected_markers)
            
        if self.current_step >= len(self.tutorial_steps):
            if not self.tutorial_completed:
                self.tutorial_completed = True
                print("\n[SUCCESS] TUTORIAL VOLLSTAENDIG ABGESCHLOSSEN!")
                print("[INFO] Schaltung vollstaendig - Kehre zurueck zum Circuitspace")
                print("[INFO] Du kannst jetzt den Arduino-Code hochladen und testen!")
            return True
            
        current_step_data = self.tutorial_steps[self.current_step]
        required_markers = set(current_step_data["required_markers"])
        detected_marker_ids = set([marker[0] for marker in detected_markers])
        
        # Prüfe ob alle erforderlichen Marker erkannt wurden
        if required_markers.issubset(detected_marker_ids):
            if not self.step_completed[self.current_step]:
                self.step_completed[self.current_step] = True
                print(f"\n[SUCCESS] {current_step_data['success_message']}")
                
                # Automatisch zum nächsten Schritt
                self.current_step += 1
                
                if self.current_step < len(self.tutorial_steps):
                    next_step = self.tutorial_steps[self.current_step]
                    print(f"[NEXT] {next_step['instruction']}")
                    time.sleep(0.5)  # Kurze Pause für Feedback
                
            return True
        
        return False

    def get_missing_components(self, detected_markers):
        """Ermittle welche Komponenten noch fehlen"""
        if self.validation_phase:
            required_markers = set([0, 1, 2, 3, 4, 5])
        elif self.current_step >= len(self.tutorial_steps):
            return []
        else:
            current_step_data = self.tutorial_steps[self.current_step]
            required_markers = set(current_step_data["required_markers"])
            
        detected_marker_ids = set([marker[0] for marker in detected_markers])
        missing = required_markers - detected_marker_ids
        return [self.marker_names[marker_id] for marker_id in missing]

    def draw_tutorial_ui(self, frame, detected_markers):
        """Zeichne das Tutorial-UI auf das Frame"""
        h, w = frame.shape[:2]
        
        if self.validation_phase:
            self.draw_validation_ui(frame, detected_markers, w, h)
        else:
            # Normal Tutorial UI
            self.draw_status_box(frame, w, detected_markers)
            self.draw_current_step_box(frame, h, detected_markers)
            self.draw_progress_bar(frame, w, h)
            self.draw_component_status(frame, w, h, detected_markers)
            
        if self.tutorial_completed:
            self.draw_completion_overlay(frame, w, h)

    def draw_validation_ui(self, frame, detected_markers, w, h):
        """Zeichne Validierungs-UI ohne Sonderzeichen"""
        # Großer Hintergrund
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (20, 20, 50), -1)
        cv2.addWeighted(frame, 0.2, overlay, 0.8, 0, frame)
        
        # Titel
        title = "KOMPONENTEN-VALIDIERUNG"
        title_size = cv2.getTextSize(title, self.font, self.font_scale_large, self.font_thickness_bold)[0]
        title_x = (w - title_size[0]) // 2
        cv2.putText(frame, title, (title_x, 80), 
                   self.font, self.font_scale_large, self.colors["warning"], self.font_thickness_bold)
        
        # Anweisung
        instruction = "Zeige alle 6 Komponenten gleichzeitig in die Kamera"
        inst_size = cv2.getTextSize(instruction, self.font, self.font_scale_medium, self.font_thickness_normal)[0]
        inst_x = (w - inst_size[0]) // 2
        cv2.putText(frame, instruction, (inst_x, 130), 
                   self.font, self.font_scale_medium, (255, 255, 255), self.font_thickness_normal)
        
        # Komponenten-Checkliste
        start_y = 180
        detected_ids = [marker[0] for marker in detected_markers]
        
        for i, (marker_id, name) in enumerate(self.marker_names.items()):
            detected = marker_id in detected_ids
            status = "[OK]" if detected else "[--]"
            color = self.colors["success"] if detected else self.colors["error"]
            
            y_pos = start_y + i * 40
            cv2.putText(frame, f"{status} {name}", (50, y_pos), 
                       self.font, self.font_scale_medium, color, self.font_thickness_normal)
        
        # Timer-Anzeige
        if len(detected_ids) == 6:
            progress = min(self.validation_timer / self.validation_hold_time, 1.0)
            timer_text = f"Halte alle Komponenten sichtbar: {self.validation_timer:.1f}s / {self.validation_hold_time:.1f}s"
            
            cv2.putText(frame, timer_text, (50, h - 100), 
                       self.font, self.font_scale_small, self.colors["warning"], self.font_thickness_normal)
            
            # Fortschrittsbalken
            bar_width = w - 100
            bar_height = 20
            bar_x = 50
            bar_y = h - 60
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (100, 100, 100), 2)
            
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                             self.colors["warning"], -1)

    def draw_status_box(self, frame, w, detected_markers):
        """Zeichne Status-Box oben mit dünnerer Schrift"""
        box_height = 100
        
        # Hintergrund
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, box_height), (20, 20, 20), -1)
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        if self.current_step < len(self.tutorial_steps):
            step_data = self.tutorial_steps[self.current_step]
            phase_color = self.phase_colors.get(step_data.get("phase", "info"), self.colors["info"])
            
            # Titel mit Phasen-Farbe
            cv2.putText(frame, f"Schritt {step_data['step']}: {step_data['title']}", 
                       (20, 30), self.font, self.font_scale_medium, phase_color, self.font_thickness_normal)
            
            # Beschreibung
            cv2.putText(frame, step_data['description'], 
                       (20, 55), self.font, self.font_scale_small, (255, 255, 255), self.font_thickness_normal)
            
            # Aktuelle Anweisung
            cv2.putText(frame, f"> {step_data['instruction']}", 
                       (20, 80), self.font, self.font_scale_tiny, (200, 255, 200), self.font_thickness_normal)

    def draw_current_step_box(self, frame, h, detected_markers):
        """Zeichne aktuellen Schritt Box links mit dünnerer Schrift"""
        box_width = 350
        box_height = 250
        start_y = 120
        
        # Hintergrund
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, start_y), (box_width, start_y + box_height), (30, 30, 30), -1)
        cv2.addWeighted(frame, 0.4, overlay, 0.6, 0, frame)
        
        if self.current_step < len(self.tutorial_steps):
            step_data = self.tutorial_steps[self.current_step]
            phase_color = self.phase_colors.get(step_data.get("phase", "info"), self.colors["info"])
            
            # Header mit Phase
            phase_name = step_data.get("phase", "unknown").replace("_", " ").title()
            cv2.putText(frame, f"Phase: {phase_name}", 
                       (10, start_y + 25), self.font, self.font_scale_small, phase_color, self.font_thickness_normal)
            
            # Benötigte Komponenten
            y_offset = 50
            cv2.putText(frame, "Benoetigte Komponenten:", 
                       (10, start_y + y_offset), self.font, self.font_scale_tiny, (200, 200, 200), self.font_thickness_normal)
            
            y_offset += 25
            for marker_id in step_data["required_markers"]:
                component_name = self.marker_names[marker_id]
                detected = any(marker[0] == marker_id for marker in detected_markers)
                
                status = "[OK]" if detected else "[--]"
                color = self.colors["success"] if detected else self.colors["error"]
                
                cv2.putText(frame, f"{status} {component_name}", 
                           (15, start_y + y_offset), self.font, self.font_scale_tiny, color, self.font_thickness_normal)
                y_offset += 20
            
            # Fehlende Komponenten
            missing = self.get_missing_components(detected_markers)
            if missing:
                y_offset += 10
                cv2.putText(frame, "Noch benoetigt:", 
                           (10, start_y + y_offset), self.font, self.font_scale_tiny, self.colors["error"], self.font_thickness_normal)
                y_offset += 20
                for component in missing:
                    cv2.putText(frame, f"- {component}", 
                               (15, start_y + y_offset), self.font, self.font_scale_tiny, self.colors["error"], self.font_thickness_normal)
                    y_offset += 15

    def draw_progress_bar(self, frame, w, h):
        """Zeichne erweiterten Fortschrittsbalken unten mit dünnerer Schrift"""
        bar_height = 40
        bar_y = h - bar_height - 10
        bar_width = w - 40
        
        # Hintergrund
        cv2.rectangle(frame, (20, bar_y), (20 + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        cv2.rectangle(frame, (20, bar_y), (20 + bar_width, bar_y + bar_height), (100, 100, 100), 2)
        
        # Fortschritt (ohne Validierung)
        total_steps = len(self.tutorial_steps) - 1  # -1 für Validierungsschritt
        current_progress = max(0, self.current_step - 1)  # -1 da Schritt 0 = Validierung
        progress = min(current_progress / total_steps, 1.0) if total_steps > 0 else 0
        progress_width = int(bar_width * progress)
        
        if progress_width > 0:
            cv2.rectangle(frame, (20, bar_y), (20 + progress_width, bar_y + bar_height), 
                         self.colors["success"], -1)
        
        # Text
        if self.validation_phase:
            progress_text = "Komponenten-Validierung laeuft..."
        else:
            progress_text = f"Fortschritt: {current_progress}/{total_steps} Schritte ({progress*100:.0f}%)"
            
        cv2.putText(frame, progress_text, (25, bar_y + 25), 
                   self.font, self.font_scale_tiny, (255, 255, 255), self.font_thickness_normal)

    def draw_component_status(self, frame, w, h, detected_markers):
        """Zeichne erweiterten Komponenten-Status rechts mit dünnerer Schrift"""
        box_width = 220
        start_x = w - box_width - 10
        start_y = 120
        box_height = 350
        
        # Hintergrund
        overlay = frame.copy()
        cv2.rectangle(overlay, (start_x, start_y), (w - 10, start_y + box_height), (20, 20, 40), -1)
        cv2.addWeighted(frame, 0.4, overlay, 0.6, 0, frame)
        
        # Header
        cv2.putText(frame, "Live-Komponenten-Status:", 
                   (start_x + 5, start_y + 25), self.font, self.font_scale_tiny, self.colors["info"], self.font_thickness_normal)
        
        y_offset = 45
        detected_ids = [marker[0] for marker in detected_markers]
        
        for marker_id, name in self.marker_names.items():
            detected = marker_id in detected_ids
            status = "ERKANNT" if detected else "FEHLT"
            color = self.colors["success"] if detected else (100, 100, 100)
            
            # Komponenten-Name
            cv2.putText(frame, name, 
                       (start_x + 5, start_y + y_offset), self.font, self.font_scale_tiny, (255, 255, 255), self.font_thickness_normal)
            y_offset += 15
            
            # Status
            cv2.putText(frame, status, 
                       (start_x + 5, start_y + y_offset), self.font, self.font_scale_tiny, color, self.font_thickness_normal)
            y_offset += 30
        
        # Tutorial-Statistiken
        y_offset += 20
        cv2.putText(frame, "Tutorial-Info:", 
                   (start_x + 5, start_y + y_offset), self.font, self.font_scale_tiny, self.colors["info"], self.font_thickness_normal)
        y_offset += 20
        
        completed_steps = sum(self.step_completed)
        cv2.putText(frame, f"Abgeschlossen: {completed_steps}", 
                   (start_x + 5, start_y + y_offset), self.font, self.font_scale_tiny, (200, 200, 200), self.font_thickness_normal)
        y_offset += 15
        
        cv2.putText(frame, f"Erkannte Marker: {len(detected_ids)}", 
                   (start_x + 5, start_y + y_offset), self.font, self.font_scale_tiny, (200, 200, 200), self.font_thickness_normal)

    def draw_completion_overlay(self, frame, w, h):
        """Zeichne Abschluss-Overlay ohne Sonderzeichen"""
        # Semi-transparenter Hintergrund
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 150, 0), -1)
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        # Großer Erfolgs-Text
        success_texts = [
            "TUTORIAL ABGESCHLOSSEN!",
            "Schaltung vollstaendig!",
            "Kehre zurueck zum Circuitspace"
        ]
        
        for i, text in enumerate(success_texts):
            font_scale = self.font_scale_large - i*0.1
            thickness = self.font_thickness_bold - i
            text_size = cv2.getTextSize(text, self.font, font_scale, thickness)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h//2 - 50 + i * 60
            
            cv2.putText(frame, text, (text_x, text_y), 
                       self.font, font_scale, (255, 255, 255), thickness)
        
        # Rückkehr-Anweisung
        return_text = "Druecke 'R' um zum Circuitspace zurueckzukehren oder 'Q' zum Beenden"
        return_size = cv2.getTextSize(return_text, self.font, self.font_scale_small, self.font_thickness_normal)[0]
        return_x = (w - return_size[0]) // 2
        cv2.putText(frame, return_text, (return_x, h//2 + 100), 
                   self.font, self.font_scale_small, (200, 255, 200), self.font_thickness_normal)

def tutorial_mode_main():
    """Haupt-Tutorial-Funktion mit erweitertem System"""
    print("[INFO] Erweiterte Arduino Tutorial System gestartet!")
    print("[INFO] Phase 1: Komponenten-Validierung")
    print("[INFO] Zeige alle 6 ArUco-Marker gleichzeitig in die Kamera")
    print("[CONTROLS] 'q' = Beenden, 'r' = Tutorial neustarten")
    
    # Kamera initialisieren
    cap = get_logitech_camera_optimized()
    if cap is None:
        print("[ERROR] Could not initialize camera")
        return
    
    # ArUco Setup
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    
    # Optimierte Parameter
    aruco_params.adaptiveThreshWinSizeMin = 3
    aruco_params.adaptiveThreshWinSizeMax = 23
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.03
    aruco_params.maxMarkerPerimeterRate = 4.0
    aruco_params.polygonalApproxAccuracyRate = 0.05
    aruco_params.minCornerDistanceRate = 0.05
    aruco_params.minDistanceToBorder = 3
    
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    
    # Tutorial System
    tutorial = ArduinoTutorialSystem()
    
    while True:
        ret, frame = get_fresh_frame(cap)
        if not ret or frame is None:
            continue
        
        # ArUco Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)
        
        # Verarbeite erkannte Marker
        detected_markers = []
        if ids is not None:
            for i, corner in enumerate(corners):
                marker_id = ids[i][0]
                center_x = int(np.mean(corner[0][:, 0]))
                center_y = int(np.mean(corner[0][:, 1]))
                corners_2d = corner[0].astype(np.int32)
                detected_markers.append((marker_id, center_x, center_y, corners_2d))
                
                # Zeichne erkannte Marker mit Komponenten-Namen statt ID
                cv2.polylines(frame, [corners_2d], True, (0, 255, 0), 2)
                
                # Komponenten-Name statt ID anzeigen (dünnere Schrift)
                component_name = tutorial.marker_short_names.get(marker_id, f"ID:{marker_id}")
                cv2.putText(frame, component_name, 
                           (center_x - 30, center_y - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Tutorial-Logik
        tutorial.check_step_completion(detected_markers)
        
        # Tutorial-UI zeichnen
        tutorial.draw_tutorial_ui(frame, detected_markers)
        
        # Frame anzeigen
        # Erstelle Fenster im Vollbild-Modus
        window_name = 'Arduino Tutorial System'
        cv2.imshow(window_name, frame)
        
        # Tastatur-Eingabe
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Tutorial neustarten
            tutorial = ArduinoTutorialSystem()
            print("\n[INFO] Tutorial wurde neugestartet!")
            print("[INFO] Phase 1: Komponenten-Validierung")
            print("[INFO] Zeige alle 6 ArUco-Marker gleichzeitig in die Kamera")
    
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Erweiterte Tutorial System beendet")

if __name__ == "__main__":
    tutorial_mode_main()
