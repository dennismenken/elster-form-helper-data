# elster-form-helper-data

Sammlung strukturierter Formularfeld-Daten (JSON) zu ausgewählten ELSTER-Steuerformularen (z. B. Körperschaftsteuer **KSt**, Gewerbesteuer **GewSt**, Umsatzsteuer **USt**) und Veranlagungsjahren. Dient als technische Grundlage für eigene Tools (Validierung, Ausfüllhilfen etc.).

> **Hinweis zur Abgrenzung:**  
> Dieses Projekt ist **inoffiziell** und steht in keinerlei Verbindung zu den Betreibern von ELSTER oder den deutschen Steuerverwaltungen.  
> Die Nutzung der Bezeichnung „ELSTER“ erfolgt ausschließlich beschreibend, um die Herkunft der extrahierten Daten zu kennzeichnen. Es wird ausdrücklich keine offizielle Unterstützung oder Anerkennung durch die Steuerverwaltungen beansprucht.  
> ELSTER ist eine eingetragene Marke der deutschen Steuerverwaltungen.  
> 
> **WICHTIG:** Die hier bereitgestellten Daten sind inoffiziell, können unvollständig oder veraltet sein und werden OHNE JEGLICHE GEWÄHR bereitgestellt. Es besteht keinerlei Anspruch auf Richtigkeit, Vollständigkeit oder Aktualität. Für rechtsverbindliche Zwecke sind ausschließlich die offiziellen ELSTER-Formulare, Anleitungen und Rechtsquellen maßgeblich.

---
## Generator & Scraper (Kurz)
`formular_daten_generator.py` fasst pro Teilformular die nummerierten JSON-Dateien zusammen, erzeugt eine aggregierte `<slug>.json` und legt Übersichten (`Endpunkt-Uebersicht.md`, `JSON-Daten.md`) im jeweiligen Jahresordner an.

Wesentliche Schritte:
1. Iteration über Formularart/Jahr
2. Merge aller `*.json` eines Unterordners
3. Schreiben `<slug>.json` (Präfixe `01`/`99` entfernt)
4. Generierung einfacher Markdown-Übersichten

Hilfsfunktionen: `slugify`, `remove_prefix`.

`kst_elster_scraper.py` (experimentell) lädt Hilfetexte von ELSTER für definierte Jahre/Formulare und exportiert Markdown (`elster_<form><jahr>_help.md`). Strukturänderungen der Quellseite können das Ergebnis verfälschen.

---
## Datenmodell (JSON-Struktur)
Ein typischer Dateiinhalt (vereinfachtes Beispiel):
```json
[
  {
    "context_label": "1 - Allgemeine Angaben",
    "sections": [
      {
        "section_label": null,
        "rows": [
          { "row": "1", "label": "Bezeichnung", "type": "text", "values": [] }
        ],
        "sections": []
      },
      {
        "section_label": "Rechtsform",
        "rows": [
          { "row": "9", "label": "Rechtsform", "type": "radio", "values": ["Keine Angabe", "…"] }
        ],
        "sections": []
      }
    ]
  }
]
````

### Felder

* `context_label` (String): Oberer Kontext oder Blocktitel.
* `sections` (Array): Rekursive Liste von Abschnitten.

  * `section_label` (String | null): Titel des Abschnitts.
  * `rows` (Array): Zeilen / Eingabeelemente.

    * `row` (String | null): Fachliche oder Formularzeilen-Nummer (kann mehrfach vorkommen falls mehrere Felder gleiche Zeilennummer nutzen).
    * `label` (String): Sichtbarer Feld-/Hinweistext.
    * `type` (String): Feldtyp, beobachtete Werte u. a.: `text`, `note`, `checkbox`, `select`, `radio`, `repeater`.
    * `values` (Array<String>): Bei Auswahlfeldern (radio/select) die möglichen Werte; sonst leer.
  * `sections` (Array): Verschachtelte Unterabschnitte.

### Hinweise zur Interpretation

* `note` kennzeichnet rein erläuternde Zeilen ohne Eingabe.
* `repeater` deutet auf dynamisch wiederholbare Gruppen hin.
* Mehrfache gleiche `row`-Nummern können verschiedene Felder derselben Formularzeile repräsentieren.

---

## Nutzung

1. Python >= 3.10.
2. Abhängigkeiten installieren:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Zusammenführen:

```
python formular_daten_generator.py
```

4. (Optional) Hilfetexte:

```
python kst_elster_scraper.py
```

5. Neues Jahr/Formular: Ordner anlegen, Roh-JSON einfügen, Generator erneut ausführen.

---

## Qualität / Validierung

Es existieren aktuell keine automatischen Tests in diesem Repository. Für produktive Nutzung wird empfohlen:

* Schema-Validierung (z. B. mittels JSON Schema) für Konsumenten
* Konsistenzprüfungen (z. B. doppelte `row` + unterschiedlicher Typ)
* Diff-Überwachung bei Updates

---

## Haftungsausschluss

Die bereitgestellten Daten und Skripte sind rein informativ / technisch orientiert.
Keine Steuer- oder Rechtsberatung. Nutzung auf eigenes Risiko.
Es wird keinerlei Haftung für Schäden, Fehlberechnungen oder steuerliche Nachteile übernommen.

Marken- und Produktnamen können geschützte Bezeichnungen ihrer jeweiligen Inhaber sein.
**ELSTER ist ein Angebot der deutschen Steuerverwaltungen – dieses Projekt ist nicht offiziell, sondern eine private, unabhängige Initiative.**

---

## Lizenz (MIT)

Copyright (c) 2025

Hiermit wird unentgeltlich jeder Person, die eine Kopie der Software und der zugehörigen Dokumentationen (die "Software") erhält, die Erlaubnis erteilt, sie uneingeschränkt zu nutzen, inklusive und ohne Ausnahme mit dem Recht, sie zu verwenden, zu kopieren, zu verändern, zusammenzuführen, zu veröffentlichen, zu verbreiten, zu unterlizenzieren und/oder zu verkaufen, und Personen, die diese Software erhalten, diese Rechte zu geben, unter den folgenden Bedingungen:

Der obige Urheberrechtshinweis und dieser Erlaubnishinweis müssen in allen Kopien oder Teilkopien der Software enthalten sein.

DIE SOFTWARE WIRD OHNE JEDE AUSDRÜCKLICHE ODER IMPLIZIERTE GARANTIE BEREITGESTELLT, EINSCHLIESSLICH DER GARANTIE ZUR BENUTZUNG FÜR DEN VORGESEHENEN ODER EINEM BESTIMMTEN ZWECK SOWIE JEGLICHER RECHTSVERLETZUNG, JEDOCH NICHT DARAUF BESCHRÄNKT. IN KEINEM FALL SIND DIE AUTOR\*INNEN ODER COPYRIGHTINHABER FÜR JEGLICHEN SCHADEN ODER SONSTIGE ANSPRÜCHE HAFTBAR ZU MACHEN, OB INFOLGE DER ERFÜLLUNG EINES VERTRAGES, EINES DELIKTES ODER ANDERS IM ZUSAMMENHANG MIT DER SOFTWARE ODER SONSTIGER VERWENDUNG DER SOFTWARE ENTSTANDEN.

---

## Beiträge

Pull Requests für:

* Korrekturen / Ergänzungen zu Feldlisten
* Neues Jahr oder Formulararten
* Verbesserungen beim Scraper / Generator

sind willkommen, solange keine Rechte Dritter verletzt werden.

---

## Kontakt

Fragen oder Hinweise bitte per Issue im Repository einreichen.

```
