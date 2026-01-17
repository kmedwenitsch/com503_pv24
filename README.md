# PV24 Forecast Prototype

## Projektbeschreibung
Dieses Projekt ist ein lokal lauffähiger Prototyp eines verteilten Systems zur PV-Erzeugungsprognose.  
Der Prototyp kombiniert historische PV-Erzeugungsdaten mit aktuellen Wetterdaten aus dem externen Webservice Open-Meteo und stellt die Ergebnisse über ein REST-Backend sowie ein lokales Web-Frontend dar.
Ebenfalls soll zukünftig der aktuelle Strommarktpreis (über ENTSO-E  Webservice) zu Zeitpunkten der Prognose angezeigt werden sowie eine Empfehlung, ob eine Einspeisung oder der Eigenverbrauch zum jeweiligen Zeitpunkt wirtschaftlich sinnvoller ist.

Die verwendeten Inputdaten im Prototyp stammen beispielhaft von einer PV-Anlage in Neudörfl (Burgenland).

Das Projekt wurde im Rahmen der Lehrveranstaltung COM503 – Verteilte Systeme umgesetzt.

## Projektteam

Karina Medwenitsch, Teresa Nikits, Melissa Behlil

---

## Funktionaler Umfang
Der Prototyp führt folgende Schritte aus:

- Einlesen historischer PV-Erzeugungsdaten aus einer CSV-Datei  
- Abruf aktueller Wetterdaten über den externen Webservice Open-Meteo
- Berechnung einer PV-Tagesprognose auf Basis der letzten 24 Stunden  
- Abruf aktueller Day-Ahead-Strompreise über die ENTSO-E Web API
- Bereitstellung der Ergebnisse über eine REST-API (FastAPI)  
- Visualisierung der Prognose in einem lokalen Web-Frontend (Streamlit)  

Das Kalenderjahr der historischen PV-Daten wird bewusst ignoriert, da diese repräsentative Beispieldaten für die jeweiligen Kalendertage darstellen sollen.  
Die Zuordnung erfolgt ausschließlich über Monat und Tag.

---

## Hinweis zum Prototyp-Charakter
Dieses Projekt ist ein Prototyp und kein produktives System.

Einschränkungen:
- Vereinfachtes Prognosemodell (heuristische Skalierung, kein trainiertes LSTM)
- ENTSO-E Day-Ahead-Preise sind architektonisch vorbereitet, werden aber nicht live genutzt, da ein API-Token erforderlich ist, der zum Zeitpunkt der Abgabe (Jänner 2026) nicht erworben werden kann
- Kein automatischer Scheduler, die Pipeline wird manuell ausgelöst

Die Architektur ist so aufgebaut, dass externe Services austauschbar sind und eine spätere Cloud-Integration möglich ist.

---

## Technologiestack
- Python 3.9  
- FastAPI (Backend / REST API)  
- Streamlit (Frontend / Visualisierung)  
- Open-Meteo API (externer Webservice)  
- pandas, numpy (Datenverarbeitung)

---

## Installation

### Voraussetzungen
- Windows  
- Python 3.9  
- Internetverbindung (für Open-Meteo)

---

### Setup
Im Projekt-Root-Verzeichnis (PowerShell):

```python -m venv .venv```

Virtuelle Umgebung aktivieren:

```.\.venv\Scripts\Activate.ps1```

Abhängigkeiten installieren:

```pip install -r requirements.txt```

---

### Ausführung
Backend starten:

```python -m uvicorn backend.app.main:app --reload --port 8000```

Backend-Endpunkte:

http://localhost:8000/health - Statuscheck

http://localhost:8000/docs - SwaggerUI

Frontend in zweitem Terminal starten:

```python -m streamlit run frontend\streamlit_app.py```

Frontend läuft auf:

http://localhost:8501/

Im Frontend unter "Run-Date" ist schließlich ein Datum anzugeben (oder leer lassen, dann wird das heutige Datum verwendet),
dann "Run Daily Pipeline" klicken.

Im rechten Bereich erscheint ein Graph mit der vorraussichtlichen Erzeugungskurve der PV-Anlage.
Ebenfalls wird darunter eine Tabelle mit den prognostizierten kWh Strom pro Stunde ausgegeben sowie der aktuelle Strommarktpreis und eine Einspeise- bzw. Eigenverbrauchsempfehlung (aktuell noch nicht implementiert).


