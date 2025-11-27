## Projekt (Machbarkeitsstudie / Durchführbarkeitsstudie)
- Projekttitel (Arbeitstitel): KI-Assistenzplattform für Buchhalter:innen – Belegfluss, Rückfragen & Buchungsvorschläge aus einer Oberfläche
- Kontext in 2–4 Sätzen: In vielen Buchhaltungen entstehen Verzögerungen durch fehlende/unsaubere Belege, Medienbrüche (E-Mail, WhatsApp, Papier), unklare Zuständigkeiten und manuelle Vorprüfung. Es gibt bereits sehr nutzerfreundliche Kanzlei-/Mandanten-Apps, die Belegtransfer und Kommunikation chatnah bündeln und Workflows visuell steuern (z. B. Aufgaben-/Kanban-Logik, automatische Erinnerungen). Wir wollen ein ähnliches Nutzungsgefühl speziell für **Buchhalter:innen** schaffen – ergänzt um KI, die Unterlagen vorsortiert, Rückfragen automatisiert vorbereitet und Buchungsvorschläge zur Prüfung liefert.
- Technischer Ansatz (3–8 Stichpunkte): was soll technologisch geprüft/validiert werden?:
  - Inbox für Belege aus App/Web/Weiterleitungen + Zuordnung zu Vorgängen (Fall/Monat/Lieferant/Kostenstelle)
  - KI-gestützte Beleg-Extraktion (OCR + Struktur) und Klassifizierung (Rechnung/Quittung/Vertrag etc.)
  - KI-Assistent, der fehlende Pflichtangaben erkennt (z. B. Leistungsdatum, Rechnungsnummer, USt-Infos) und Rückfragen als Chat-„Tasks“ formuliert
  - Buchungsvorschläge (Kontierung/Steuerschlüssel/Kostenstelle) als „Review-Queue“ mit Confidence & Begründung
  - Workflow-Steuerung wie in einfachen Kollaborationstools: Vorgänge wandern durch Status (eingegangen → geprüft → Rückfrage → freigegeben → exportiert)
  - Integrationskonzept (z. B. DATEV-Export / API-Connector zu gängigen Systemen) + Audit-Trail (wer hat wann was entschieden)
  - Sicherheits-/Rechtekonzept (Mandantendaten, Rollen, Protokollierung) + DSGVO-konformes Hosting-Setup (Machbarkeit)

## Erfolg (informell, wird formalisiert)
- Woran erkennen wir am Ende der Machbarkeitsstudie, dass es „funktioniert“?
  - Wir bekommen Belege schneller und vollständiger zusammen, ohne dauernd hinterher zu telefonieren oder E-Mails zu suchen.
  - Rückfragen werden seltener und gezielter, weil das System automatisch erkennt, was fehlt, und eine verständliche Nachfrage vorbereitet.
  - Buchungsvorschläge sind in vielen Standardfällen so gut, dass Buchhalter:innen nur noch prüfen und freigeben müssen.
  - Die Oberfläche ist für Nicht-Techniker sofort nutzbar (wie Chat/ToDo), dadurch machen Mandant:innen/Fachabteilungen wirklich mit.
  - Wir können sauber nachweisen, wer was wann gemacht hat (Audit-Trail), ohne extra Dokumentation.
  - Es gibt eine klare Entscheidungsvorlage, ob ein FuE-Projekt zur Produktentwicklung lohnt (Technikrisiken, Integrationspfad, Aufwand/Nutzen).

## Team (Pflicht)
- Antragsteller (Unternehmensname): Example Analytics GmbH
- Projektleiter (Name + Rolle): Max Berger – Product & Engineering Lead (B2B SaaS / Dokumenten-Workflows)

## Rahmen
- Geplante Laufzeit (Monate): 5
- Bekannte Konkurrenz/Alternativen (optional, 0–3 Namen/Links):
  - Klassische Beleg-/Rechnungs-Workflows (DMS/Invoice-Approval) ohne klare Buchhaltungs-Review-Logik
  - Kanzlei-/Mandanten-Apps mit Chat + Belegtransfer + Workflow (als UX-Referenz, aber nicht auf Buchhalter:innen fokussiert)
  - Buchhaltungssoftware mit OCR/Automatisierung (stark in Buchung, schwächer in Kollaboration/Rückfragensteuerung)
