# AR Computer Vision Project

Ein modernes Augmented Reality (AR) Projekt mit Computer Vision-Funktionalitäten, speziell optimiert für Logitech HD-Webcams und ArUco-Marker-Erkennung.

## Features

- **Adaptive ArUco-Marker-Erkennung**: Hochperformante Erkennung von ArUco-Markern
- **Automatische Kamera-Erkennung**: Intelligente Auswahl der besten verfügbaren Kamera
- **Logitech HD-Webcam Optimierung**: Spezielle Optimierungen für Logitech HD 1080p Webcams
- **AR-Visualisierung**: Moderne UI für Augmented Reality-Anwendungen
- **3D-Model Integration**: Unterstützung für GLB und OBJ 3D-Modelle

## Projektstruktur

```
├── src/                    # Hauptanwendungscode
│   ├── camera_utils.py     # Kamera-Utilities und -Optimierung
│   ├── ar_modern_ui.py     # Moderne AR-Benutzeroberfläche
│   ├── ar_textured.py      # Texturierte AR-Objekte
│   └── main.py            # Hauptanwendung
├── assets/                 # Ressourcen
│   ├── images/            # Bilder und Texturen
│   └── models/            # 3D-Modelle
├── adaptive_aruco.py       # Adaptive ArUco-Erkennung
├── optimized_aruco.py      # Optimierte ArUco-Algorithmen
└── logitech_detector.py    # Logitech-spezifische Optimierungen
```

## Installation

1. Virtual Environment erstellen:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

2. Dependencies installieren:
```bash
pip install -r requirements.txt
```

## Verwendung

```bash
cd src
python main.py
```

## Kamera-Optimierung

Das Projekt enthält spezielle Optimierungen für verschiedene Kameratypen:

- **Logitech HD 1080p Webcam**: Vollautomatische Konfiguration mit 1920x1080@30fps
- **Externe USB-Kameras**: Prioritäre Erkennung und Optimierung
- **Integrierte Kameras**: Fallback-Unterstützung

## Requirements

- Python 3.8+
- OpenCV 4.0+
- NumPy
- Weitere Dependencies siehe `requirements.txt`

## Lizenz

Privates Projekt - Alle Rechte vorbehalten
