## ADDED Requirements

### Requirement: Quellengebundene dokumentarische Beschreibung

Das durch D-1 gewählte eigene dokumentarische Format SHALL Identität, Version, Quellenpins, Fähigkeiten mit Input/Output und implemented/candidate/unknown sowie Ausschlüsse ausdrücken. Ein passender Module-v2-Deskriptor wird nur mit exakter Version und Hash referenziert; seine normative Bedeutung bleibt unverändert. Das neue Format SHALL keine Authority, Admission, Ausführung oder Host-Verfügbarkeit implizieren.

#### Scenario: Gültiger gepinnter Bestand
- **WHEN** ein Owner-Deskriptor und seine deklarierten lokalen Quellenbytes gegen den gewählten Vertrag geprüft werden
- **THEN** sind Schema- und Hashprüfung getrennt nachvollziehbar und der dokumentarische Geltungsbereich bleibt sichtbar.

#### Scenario: Fehler und fehlende Quellen
- **WHEN** Formatversion, Typ oder Hash falsch sind oder referenzierte Bytes fehlen
- **THEN** werden Fehler bzw. unavailable/unprüfbar getrennt ausgewiesen; kein latest-Fallback und kein erfolgreich behaupteter Pin-Nachweis.

#### Scenario: Geschlossener v2-Vertrag
- **WHEN** eine generische MCP-Tooldeklaration als unveränderter Module-v2-Deskriptor angeboten wird
- **THEN** wird sie nicht als v2-konform ausgegeben; das eigene dokumentarische Format kann sie nach seinem separat geprüften Vertrag beschreiben.

### Requirement: Vollständige Owner- und Lib-Zuordnung

Die Artefakte SHALL alle Rollen der MILE-071-Baseline sowie den internen Bereich `translator/` des Connector-Moduls abdecken. `translator/` ist kein achtes Modul. Lib SHALL alle 13 gepinnten Einträge mit eigener, entschiedener Cube-Zuordnung enthalten.

#### Scenario: Quelle ist ein Entwurf
- **WHEN** nur Zielarchitektur, Registry-Eintrag oder Translator-Vorschlag vorliegt
- **THEN** wird daraus weder implemented noch eine laufende Host-Fähigkeit abgeleitet.

#### Scenario: Lib-Abgleich
- **WHEN** die Lib-Beschreibung gegen den gepinnten INDEX geprüft wird
- **THEN** sind genau 13 Einträge vorhanden; Quellenstatus und cube-profile/standalone/deferred bleiben getrennt; ein fehlender Eintrag oder offene D-2 verhindert vollständige Abnahme.

### Requirement: Hashführender Host-Pfad und eindeutige Namen

Die ADR SHALL D-3 unverändert wiedergeben. Nach D-4 SHALL `lunados.connector` als gemeinsames Ziel-Repo, `translator/` als interner Bereich und `aiaeao-connector` als bestehender technischer Paketname unterscheidbar sein, ohne Code oder technische Identitäten umzuschreiben.

#### Scenario: Zwei Pfade, derselbe Snapshot
- **WHEN** direkter Build-/Test-Snapshot und Host-Laufzeitsnapshot denselben gepinnten INDEX-Hash haben
- **THEN** beschreibt die ADR beide erlaubten Bezugswege; bei abweichendem Hash gilt keine Gleichheit und kein stiller Fallback.

#### Scenario: Connector-Nennung
- **WHEN** Nutzer einen Deskriptor oder aktuellen Space-Erklärtext lesen
- **THEN** sind technischer Referent und Verantwortung eindeutig; historische Pins bleiben erhalten.

### Requirement: Passive additive Nachbardiscovery

G4 und G5 SHALL denselben serialisierten neighbors-Inhalt mit Version und Hash liefern. Bestehende Felder SHALL je Oberfläche unverändert bleiben. Discovery SHALL Nachbarn weder laden noch aufrufen oder automatisch binden.

#### Scenario: Parität ohne Nachbarzugriff
- **WHEN** Discovery lokal und im G5-Artefakt ohne Nachbar-Checkout oder Netzwerkzugriff ausgeführt wird
- **THEN** sind neighbors-Bytes gleich, alle übrigen Felder gegenüber der jeweiligen Baseline unverändert und keine Nachbaroperation findet statt.

#### Scenario: Fehlender Remote-Nachweis
- **WHEN** nur Offline-Parität nachgewiesen ist
- **THEN** behauptet der Abnahmebericht keinen tatsächlich ausgelieferten G5-/Host-Stand; die beanspruchte Remote-Abnahme bleibt offen bis zur Beobachtung.
