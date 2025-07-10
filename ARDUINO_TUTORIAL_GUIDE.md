# 🎓 Arduino Tutorial System - Benutzerhandbuch

## Überblick
Das Arduino Tutorial System ist ein interaktiver, AR-basierter Schritt-für-Schritt Guide zum Aufbau einer Arduino-Schaltung mit LED und Potentiometer. Das System verwendet ArUco-Marker zur Komponentenerkennung und bietet eine moderne UI mit Echtzeitfeedback.

## 🚀 Schnellstart

### 1. System starten
```bash
cd /Users/franzos/Desktop/invention-main/src
python main.py
```

### 2. Arduino Tutorial wählen
- Wählen Sie Option **6** im Hauptmenü: "🎓 Arduino Tutorial System (Step-by-Step)"

### 3. Komponenten vorbereiten
Sie benötigen folgende Komponenten mit ArUco-Markern:

| Komponente | ArUco ID | Beschreibung |
|------------|----------|--------------|
| Arduino Leonardo | 0 | Mikrocontroller |
| Breadboard | 1 | Steckbrett |
| LED | 2 | Leuchtdiode |
| 220Ω Resistor | 3 | Schutzwiderstand |
| Potentiometer | 4 | Variable Widerstand |
| Jumper Wires | 5 | Verbindungskabel |

## 📚 Tutorial-Phasen

### Phase 1: Komponenten-Validierung ✅
**Ziel:** Alle 6 Komponenten müssen gleichzeitig erkannt werden
- Legen Sie alle ArUco-Marker sichtbar in das Kamerabild
- Das System zeigt den Erkennungsstatus jeder Komponente in Echtzeit
- Erst bei erfolgreicher Validierung startet das eigentliche Tutorial

### Phase 2: Schritt-für-Schritt Anleitung 🔧

#### Schritt 1: Arbeitsplatz vorbereiten
- **Erforderlich:** Arduino (ID: 0), Breadboard (ID: 1)
- **Aufgabe:** Platziere Arduino und Breadboard nebeneinander

#### Schritt 2: GND-Verbindung
- **Erforderlich:** Arduino, Breadboard, Jumper Wires (ID: 5)
- **Aufgabe:** GND-Verbindung zwischen Arduino und Breadboard (-)

#### Schritt 3: 5V Stromversorgung
- **Erforderlich:** Arduino, Breadboard, Jumper Wires
- **Aufgabe:** 5V von Arduino zu Breadboard (+) Schiene

#### Schritt 4: LED einsetzen
- **Erforderlich:** Arduino, Breadboard, LED (ID: 2)
- **Aufgabe:** LED auf Breadboard platzieren (langes Bein = +, kurzes Bein = -)

#### Schritt 5: LED-Schutzwiderstand
- **Erforderlich:** Arduino, Breadboard, LED, Resistor (ID: 3)
- **Aufgabe:** 220Ω Widerstand zwischen LED-Kathode und GND

#### Schritt 6: LED-Signalverbindung
- **Erforderlich:** Alle außer Potentiometer
- **Aufgabe:** LED-Anode mit Arduino Digital Pin D9 verbinden

#### Schritt 7: Potentiometer hinzufügen
- **Erforderlich:** Arduino, Breadboard, LED, Resistor, Potentiometer (ID: 4)
- **Aufgabe:** Potentiometer auf Breadboard platzieren

#### Schritt 8: Potentiometer GND
- **Erforderlich:** Alle Komponenten
- **Aufgabe:** Linker Potentiometer-Pin mit GND-Schiene

#### Schritt 9: Potentiometer 5V
- **Erforderlich:** Alle Komponenten
- **Aufgabe:** Rechter Potentiometer-Pin mit 5V-Schiene

#### Schritt 10: Potentiometer Signal
- **Erforderlich:** Alle Komponenten
- **Aufgabe:** Mittlerer Potentiometer-Pin mit Arduino A0

#### Schritt 11: Finale Überprüfung ✅
- **Erforderlich:** Alle Komponenten
- **Aufgabe:** Überprüfung aller Verbindungen
- **🎉 Erfolg:** "SCHALTUNG VOLLSTÄNDIG!" Nachricht

## 🎮 Steuerung

### Tastatur-Shortcuts
- **Q:** Tutorial beenden
- **R:** Tutorial neustarten (jederzeit verfügbar)

### Navigation
- Das System erkennt automatisch die erforderlichen Komponenten für jeden Schritt
- Der nächste Schritt wird nur freigeschaltet, wenn alle Anforderungen erfüllt sind
- Fehlende Komponenten werden in Echtzeit angezeigt

## 🎨 UI-Features

### Moderne Benutzeroberfläche
- **Komponenten-Status:** Live-Anzeige erkannter Marker
- **Schritt-Anzeige:** Aktueller Schritt mit Fortschrittsbalken
- **Instruktionen:** Klare Anweisungen für jeden Schritt
- **Validierung:** Echtzeitfeedback über Schritt-Vollendung
- **Phasen-Farben:** Verschiedene Farben für unterschiedliche Tutorial-Phasen

### Erweiterte AR-Overlays
- **Marker-Erkennung:** Farbige Boxen um erkannte Komponenten
- **ID-Anzeige:** ArUco-ID für jede Komponente
- **Koordinaten:** Position jeder Komponente im Bild
- **Status-Indikatoren:** Visuelle Bestätigung der Schritt-Vollendung

## 🔧 Technische Details

### Kamera-Optimierung
- **Auflösung:** 1920x1080 bei 30fps (Logitech-optimiert)
- **ArUco Dictionary:** DICT_6X6_250
- **Erkennungsparameter:** Optimiert für zuverlässige Marker-Erkennung

### Performance
- **FPS-Anzeige:** Live-Überwachung der Bildrate
- **Adaptive Erkennung:** Intelligente Skalierung für beste Performance
- **Marker-Caching:** Zwischenspeicherung für flüssige Darstellung

### Phasen-System
```python
# Verfügbare Phasen
phases = {
    "validation": "Komponenten-Überprüfung",
    "preparation": "Arbeitsplatz-Vorbereitung", 
    "power_setup": "Stromversorgung",
    "components": "Komponenten-Platzierung",
    "connections": "Verbindungen",
    "analog_input": "Analoge Eingabe",
    "verification": "Finale Überprüfung"
}
```

## 🎯 Best Practices

### Optimale Nutzung
1. **Beleuchtung:** Sorgen Sie für ausreichende, gleichmäßige Beleuchtung
2. **Marker-Größe:** ArUco-Marker sollten mindestens 3cm x 3cm groß sein
3. **Kamera-Abstand:** 30-80cm Abstand zur Kamera für beste Erkennung
4. **Marker-Qualität:** Verwenden Sie hochauflösende, kontrastreiche Marker

### Fehlerbehebung
- **Marker nicht erkannt:** Prüfen Sie Beleuchtung und Marker-Qualität
- **Langsame Performance:** Reduzieren Sie andere laufende Programme
- **Kamera-Probleme:** Starten Sie das System neu oder wechseln Sie USB-Ports

## 📝 Arduino Code (nach Tutorial-Abschluss)

Nach erfolgreichem Abschluss des Tutorials können Sie folgenden Code verwenden:

```cpp
// Arduino LED + Potentiometer Steuerung
const int ledPin = 9;      // LED an Digital Pin 9
const int potPin = A0;     // Potentiometer an Analog Pin A0

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int potValue = analogRead(potPin);        // Lese Potentiometer (0-1023)
  int brightness = map(potValue, 0, 1023, 0, 255);  // Skaliere zu 0-255
  
  analogWrite(ledPin, brightness);          // Setze LED-Helligkeit
  
  Serial.print("Pot: ");
  Serial.print(potValue);
  Serial.print(" | LED: ");
  Serial.println(brightness);
  
  delay(50);
}
```

## 🔗 Integration mit anderen Modi

Das Arduino Tutorial System ist vollständig in die bestehende AR-Anwendung integriert:

- **Menü-Navigation:** Zugriff über Hauptmenü Option 6
- **Rückkehr zum Menü:** Nach Tutorial-Beendigung
- **Kompatibilität:** Funktioniert mit allen anderen AR-Modi

---

**🎓 Viel Erfolg beim Lernen mit dem Arduino Tutorial System!**

Für weitere Hilfe oder Fragen, konsultieren Sie die Dokumentation der anderen AR-Modi oder starten Sie das Tutorial einfach neu mit der 'R'-Taste.
