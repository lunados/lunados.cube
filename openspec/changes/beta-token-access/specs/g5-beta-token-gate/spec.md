# G5-Beta-Token-Gate

Status: proposed · 2026-11-06 · [MILE-019](../../../../../docs/02-Milestones/MILE-019-beta-token-access.md)

## MODIFIED Requirements

### Requirement: Entwicklerzugang

Der G5-Gateway SHALL den vorhandenen `MCP_BEARER_TOKEN` am bestehenden `/mcp`-Endpunkt weiterhin akzeptieren, unabhängig davon, ob Beta-Token-Plätze belegt sind.

#### Scenario: Keine Beta-Tokens eingerichtet

- **GIVEN** nur der vorhandene Entwickler-Token ist konfiguriert
- **WHEN** ein gültiger MCP-POST mit diesem Bearer-Token eintrifft
- **THEN** erreicht die Anfrage den unveränderten MCP-Handler.

#### Scenario: Fehlerhafter Beta-Platz

- **GIVEN** ein Beta-Token-Platz fehlt oder enthält einen ungültigen Wert
- **WHEN** ein gültiger MCP-POST mit dem Entwickler-Token eintrifft
- **THEN** erreicht die Anfrage weiterhin den MCP-Handler.

#### Scenario: Entwickler-Secret fehlt

- **GIVEN** das erforderliche Entwickler-Secret fehlt oder ist zu kurz, aber ein Beta-Platz ist belegt
- **WHEN** ein MCP-POST eintrifft
- **THEN** antwortet der Gateway wie bisher `503` statt Beta-Zugang zu gewähren.

### Requirement: Authentifizierung vor MCP

Der Gateway SHALL einen fehlenden oder nicht akzeptierten Bearer-Token mit `401` zurückweisen, bevor eine MCP-Operation oder ein Core-Aufruf stattfindet.

#### Scenario: Kein gültiger Schlüssel

- **GIVEN** Entwickler- und Beta-Tokens können konfiguriert sein
- **WHEN** ein MCP-POST ohne oder mit falschem Bearer-Token eintrifft
- **THEN** antwortet das Gateway `401` und ruft weder MCP-Handler noch Core auf.

## ADDED Requirements

### Requirement: Bis zu zwölf Beta-Tokens

Der Gateway SHALL bis zu zwölf getrennte optionale Worker-Secret-Plätze `MCP_BETA_TOKEN_01` bis `_12` unterstützen. Jeder ausreichend starke, einzigartige Wert SHALL den bestehenden MCP-Werkzeugumfang erlauben. Ein leerer, zu kurzer oder doppelt belegter Beta-Wert SHALL keinen Zugang gewähren.

#### Scenario: Zwölf gültige Plätze

- **GIVEN** zwölf unterschiedliche Beta-Tokens sind konfiguriert
- **WHEN** je ein gültiger MCP-POST mit einem dieser Tokens eintrifft
- **THEN** erreicht jede Anfrage denselben MCP-Handler.

#### Scenario: Unbelegter Platz

- **GIVEN** ein Beta-Platz ist unbelegt
- **WHEN** ein beliebiger nicht anderweitig gültiger Bearer-Token verwendet wird
- **THEN** antwortet das Gateway `401`.

#### Scenario: Zu kurzer oder doppelt belegter Beta-Wert

- **GIVEN** ein Beta-Wert ist zu kurz oder derselbe Wert steht in zwei Beta-Plätzen
- **WHEN** der Wert als Bearer-Token verwendet wird
- **THEN** antwortet das Gateway `401`, während ein anderer gültiger Beta-Token und der Entwickler-Token weiter funktionieren.

### Requirement: Einzelner Widerruf

Ein Beta-Token SHALL durch Entfernen oder Ersetzen seines Worker Secrets widerrufbar sein, ohne den Entwickler-Token oder andere unterschiedliche Beta-Tokens zu widerrufen.

#### Scenario: Beta-Platz entzogen

- **GIVEN** zwei unterschiedliche Beta-Tokens und der Entwickler-Token waren gültig
- **WHEN** einer der Beta-Plätze entfernt oder ersetzt und die Änderung bereitgestellt wird
- **THEN** erhält der alte Wert `401`, während der andere Beta- und der Entwickler-Token weiter akzeptiert werden.

### Requirement: Host-Verbindung

Die Abnahme SHALL für Codex und Claude jeweils eine tatsächliche Verbindung zum bestehenden Endpunkt mit einem Beta-Token und einen vorab fixierten kleinen Werkzeugaufruf nachweisen oder eine konkrete Host-Einschränkung ausweisen.

#### Scenario: Beta-Client verbindet sich

- **GIVEN** ein Beta-Token ist eingerichtet und sicher im Client hinterlegt
- **WHEN** Codex bzw. Claude den G5-MCP-Endpunkt verbindet und den vereinbarten Aufruf ausführt
- **THEN** wird das echte Remote-Ergebnis ohne Preisgabe des Tokens protokolliert.
