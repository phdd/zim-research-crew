# intake.md (NVDD – Machbarkeitsstudie / Durchführbarkeitsstudie)

## Antragsteller (Stammdaten)
- Firmenname: Neustädter Verpackung Vertriebs-GmbH (NVDD)
- Adresse: Magazinstr. 15 A, 01099 Dresden, Deutschland
- Umsatzsteuer-Identifikationsnummer (USt-IdNr.): DE 243 512 790
- Website/Impressum-Link (optional, für Stammdatenabgleich): https://www.nv-dresden.de/

## Projekt (Machbarkeitsstudie / Durchführbarkeitsstudie)
- Projekttitel (Arbeitstitel): KI-gestützte E-Mail- & Vorgangsautomatisierung für Verpackungsprozesse
- Kontext: Als Anbieter von Industrieverpackungen entstehen täglich viele eingehende E-Mails (Anfragen, Angebotsrückläufe, Bestellungen, Terminfragen, Reklamationen) inklusive Anhängen und unstrukturierten Informationen. Heute werden Nachrichten manuell gelesen, verteilt, nachgefasst und in Systeme/Dateiablagen übertragen; dadurch entstehen Medienbrüche, Wartezeiten und Fehler (vergessene Rückfragen, doppelte Erfassung, fehlende Dokumentation). Ziel ist, die E-Mail-Verarbeitung durch KI so zu beschleunigen, dass aus E-Mails automatisch nachvollziehbare Vorgänge mit Aufgaben, Fristen und Dokumentation entstehen (mit Human-in-the-loop).
- Technischer Ansatz: was soll technologisch geprüft/validiert werden?:
  - E-Mail-Ingestion aus zentralen Postfächern inkl. Anhänge (PDF, Bilder, Office) + Thread-/Kontext-Zusammenführung
  - Vorgangstyp-/Intent-Klassifikation (z. B. Anfrage/Angebot, Bestellung, Liefertermin, Reklamation, Rückfrage, Rechnung/sonstiges)
  - Focus auf Sprachmodelle (LLMs) und Multi-Agenten-Systemen / Deep Agents zur automatisierten Analyse, Entscheidungsfindung und Prozesssteuerung (sicherheit durch guardrails betonen)
  - Struktur-Extraktion zentraler Felder aus Mail/Anhang (Kunde/Absender, Artikel/Material, Mengen, Termine, Referenzen, Lieferadresse/Logistik-Hinweise)
  - Automatisches Anlegen von Vorgängen/Cases mit Aufgaben (Owner, Frist, Status), inkl. Checklisten (fehlende Angaben)
  - Rückfragen-Generator: KI erkennt fehlende Informationen und schlägt Antwortentwürfe vor (mit Quellen aus Mail/Anhang)
  - Dokumentation/Audit-Trail: Nachvollziehbarkeit von KI-Vorschlägen und menschlichen Korrekturen (wer/was/wann/warum)
  - Integrationsmachbarkeit: ERP/CRM/DMS/Task-Tool via API/Export; Rollen-/Rechtekonzept und DSGVO-Prüfpunkte
  - Qualitäts-/Sicherheitskonzept: Confidence Scores, Review-Queue, Fehlerklassen, Fallback-Regeln

## Erfolg (informell, wird formalisiert)
- Woran erkennen wir am Ende der Machbarkeitsstudie, dass es „funktioniert“? (Alltagssprache):
  - Jede relevante E-Mail wird automatisch einem Vorgang zugeordnet oder als neuer Vorgang angelegt (nichts geht unter).
  - Aufgaben entstehen automatisch mit Zuständigkeit und Frist; Prioritäten (z. B. Terminsachen/Reklamationen) sind sichtbar.
  - Weniger manuelles Sortieren/Übertragen: die KI macht die Vorarbeit, Mitarbeitende prüfen nur noch und korrigieren bei Bedarf.
  - Rückfragen werden seltener und zielgenauer, weil fehlende Pflichtinfos automatisch erkannt werden.
  - Entscheidungen bleiben nachvollziehbar (warum Zuordnung so, welche Textstellen/Anhänge als Grundlage).
  - Es gibt eine klare Go/No-Go-Vorlage fürs Folge-FuE-Projekt (Technikrisiken, Datenbasis, Integrationspfad, Aufwand/Nutzen).

## Team (Pflicht)
- Projektleiter (Geschäftsführer, Name + Rolle): Andreas Beck – Geschäftsführer (Dresden, Projektleitung, fachliche Steuerung)
- Weitere Schlüsselrollen (Name – Organisation – Rolle):
  - Peter Heisig (Dresden) – sit.institute GmbH – Technische Leitung
  - Tom Schreiber (Dresden) – sit.institute GmbH – KI-Entwicklung

## Rahmen
- Geplante Laufzeit: 01/2026 bis 06/2026 (6 Monate)
- Geplantes Budget (gesamt): 80.000 EUR (schätzung gewünscht)
