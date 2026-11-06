# MILE-017 — Staging und Production für G5 (Beta-Betrieb)

Status: **eingefroren** (Nutzer, 2026-11-06) · Stand: 2026-11-06 · Grundlage: Konzept „AIAEAO — Staging & Production Concept v1.0“ (Nutzer, Status *Proposed*, unten im Wortlaut) · Voraussetzung: MILE-015 (G5 R9), MILE-016 abgeschlossen

**Entscheidung vom 2026-11-06:** Dieser Entwurf bleibt als späterer Vorschlag erhalten und wird vorerst nicht umgesetzt. Die Trennung in Staging und Production war vor allem als Schutz gegen einen eigenen Zugriffsverlust während der Entwicklung gedacht. Für die geschlossene Beta soll zunächst der bestehende G5-Endpunkt mit getrenntem Entwickler- und Beta-Zugang weiterlaufen. Die aktuelle Planung dafür steht in [MILE-019](MILE-019-beta-token-access.md). Cloudflare One-Time PIN, Access und OAuth sind nicht Teil von MILE-019; eine spätere Umsetzung erfordert eine eigene Entscheidung. Die folgenden Backlog- und Abnahmepunkte sind der **eingefrorene ursprüngliche Vorschlag**, keine aktive Zusage für MILE-019.

## Anlass

G5 ist heute ein einziger Remote-Stand für Entwicklung und Abnahme. Vor einer externen Beta soll die laufende Entwicklung vom stabilen Betrieb getrennt werden: ein Repository, zwei Umgebungen, kontrollierte Releases. Die öffentliche Read-only-Referenz bleibt davon unabhängig erreichbar.

## Ausgangslage (Stand `main` b22a735)

- G5 besteht aus zwei Workern: Gateway `aiaeao-cube-g5-gateway` (`workers_dev: true`) und Kern `aiaeao-cube-g5-core` (`workers_dev: false`, nur über die Service Binding `CORE` erreichbar). Eine Production braucht beide Worker als eigenes Paar, nicht nur ein zweites Gateway.
- Zugang heute: Bearer-Token (`MCP_BEARER_TOKEN`, Worker Secret), Origin-Prüfung, Größenlimits. Laut `P3/remote-mcp-g5/SECURITY.md` fehlen OAuth, Rollen, Quoten und Rate-Limits; vor breiter Freigabe sind Cloudflare Access/WAF oder OAuth vorgesehen.
- G5 hält derzeit keinen beschreibbaren Zustand (kein KV/D1/R2); Ressourcenisolation betrifft zunächst Secrets, Access/OAuth-Konfiguration und Logs.
- Öffentliche Referenz: `P3/public-reference-mcp` (eigener Worker, read-only).
- Abnahmen laufen als R-Serien mit vorab fixierten Erwartungen (zuletzt R9 51/51); dieses Muster gilt auch für Production.
- Cloudflare-Konto auf Workers Paid (seit 2026-11-05).

## Backlog (Vorschlag, aus dem Konzept abgeleitet)

| ID | Inhalt | Abnahme (aus Konzept §7) |
|---|---|---|
| S1 | Wrangler-Environments `staging` / `production` für Gateway und Kern; Production-Namen (z. B. `aiaeao-cube-g5-prod`, Kern entsprechend) und Service Binding je Umgebung | Staging und Production unabhängig deploybar; bestehender Staging-Endpunkt bleibt |
| S2 | Release-Prozess: Git-Tag je freigegebenem Stand, Production nur aus Tags, Rollback auf vorherigen Worker-Stand; Skripte (`assemble_core`, `check_runtime_assets`, `verify_g5`) umgebungsfähig | Release und Rollback reproduzierbar |
| S3 | Secrets und Ressourcen je Umgebung getrennt (Token, OAuth/Access, Logs; künftige KV/D1/R2) | Keine gemeinsamen beschreibbaren Ressourcen |
| S4 | Production-Zugang: Cloudflare Zero Trust Access, E-Mail-Allowlist, One-Time PIN; serverseitige Prüfung von Identität und Berechtigung; Widerruf je Nutzer | Freigegebener Nutzer kommt rein, nicht freigegebener nicht; Widerruf wirkt |
| S5 | OAuth für MCP-Clients (Claude-Connector, Codex): Discovery mit `401` und `resource_metadata`, DCR oder CIMD, Redirect `https://claude.ai/api/mcp/auth_callback` und Loopback für Claude Code | OAuth mit Codex und Claude getestet |
| S6 | Produktvarianten Public / Pro / Premium als Berechtigungen, unabhängig von der Umgebung; in der geschlossenen Beta nur zentrale Allowlist | Allowlist wirkt; keine Lizenzverwaltung nötig |
| S7 | Public Reference bleibt eigenständig | Public Reference unabhängig erreichbar |

## Epics und Aufwand (Schätzung, 2026-11-05)

| Epic | Inhalt | Aufwand (PT) | Unsicherheit |
|---|---|---|---|
| E17-1 Entscheidungen | Die offenen Fragen klären, vor allem Access und OAuth für MCP-Clients; kleiner Probeaufbau mit Claude und Codex gegen einen Test-Worker | 0,5–1 | hoch, bestimmt alles Weitere |
| E17-2 Zwei Umgebungen | Wrangler-Environments für Gateway und Core (je ein Paar mit eigener Service Binding); Skripte umgebungsfähig; heutiger Endpunkt bleibt Staging | 0,5 | gering |
| E17-3 Release und Rollback | Production nur aus Git-Tags, Runbook, Rollback auf den vorherigen Worker-Stand, R-Serie gegen Production | 0,5 | gering |
| E17-4 Secrets und Isolation | Getrennte Secrets, Logs, Zugangskonfiguration; später KV/D1/R2 | 0,25 | gering |
| E17-5 Zugang Production | Cloudflare Access, E-Mail-Allowlist, One-Time PIN, serverseitige Prüfung, Widerruf | 0,5–1 | mittel |
| E17-6 OAuth für MCP-Clients | OAuth im Gateway (Discovery, Registrierung, Token), Tests mit Claude und Codex | 1–2 | hoch |
| E17-7 Produktvarianten | Public/Pro/Premium als Berechtigungen; Beta über zentrale Allowlist | 0,25–0,5 | mittel |
| E17-8 Abnahme | Die zehn Kriterien aus §7 des Konzepts, Nachweis, Live-Lauf | 0,5 | gering |
| **Summe** | | **4–6,25** | ohne E17-6 (Production zunächst mit Access und Token) etwa 2,5–3,5 |

## Offene Fragen (für die Spezifikation)

- Bleibt der heutige Endpunkt als Staging unter seinem Namen, oder bekommt Staging ebenfalls einen neuen, und der heutige wird stillgelegt?
- Access vor dem Worker und OAuth im MCP-Fluss: Wie spielen beide zusammen (Access-Service-Token für Clients ohne Browser, Managed OAuth von Cloudflare oder eigener OAuth-Provider im Worker)?
- Was gehört zu „Pro: Functions + Local Storage“ und „Premium: Cloud Space“ konkret in G5 (lunados.lib-Funktionen, Speicher je Nutzer)?
- Bleibt der Bearer-Token in Staging als Entwicklerzugang, oder wird auch Staging auf Access umgestellt?

## Konzept (Nutzer, v1.0, Wortlaut)

> **Status:** Proposed · **Scope:** G5 MCP Gateway / Beta Release · **Principle:** One Repository · Two Environments · Controlled Releases

### 1. Zielsetzung

Trennung der laufenden AIAEAO-Entwicklung vom stabilen Betrieb für externe Beta-Nutzer.

- **Staging:** Entwicklung, Integration, Experimente und Tests.
- **Production:** Kontrollierte Bereitstellung für eingeladene Beta-Nutzer.
- **Public:** Öffentlich zugängliche Read-only-Referenz bleibt unabhängig erreichbar.

Die Trennung soll Entwicklungsfreiheit, Betriebssicherheit und spätere Skalierbarkeit gewährleisten.

### 2. Repository & Deployment

**Ein gemeinsames Git-Repository**, keine separate Production-Codebasis.

| Aspekt | Staging | Production |
|---|---|---|
| Worker | `aiaeao-cube-g5-gateway` | `aiaeao-cube-g5-prod` |
| Nutzer | Entwickler / Test-Agenten | Eingeladene Beta-Nutzer |
| Code | Aktueller Entwicklungsstand | Freigegebener Release |
| MCP | Experimentell | Stabil |
| OAuth | Entwicklung / Tests | Produktive Authentifizierung |
| Storage | Isolierte Testdaten | Isolierte Nutzerdaten |
| Deployment | Kontinuierlich | Kontrolliert |

**Git-Strategie:**
- `main`: Integrationsbranch für Staging.
- Feature-Branches: Entwicklung und Experimente.
- Release-Tags: Versionierte, freigegebene Produktionsstände.
- Production-Deployments ausschließlich aus freigegebenen Commits.

Cloudflare Wrangler Environments ermöglichen unabhängige Worker-Deployments aus derselben Codebasis.

### 3. Authentifizierung & Zugriff

**Staging**
- Entwicklerzugriff und kontrollierte Test-Identitäten.
- OAuth- und MCP-Experimente möglich.
- Kein ungeschützter Zugriff auf operative Funktionen.

**Production**
- Cloudflare Zero Trust Access.
- E-Mail-Whitelist für ausgewählte Beta-Nutzer.
- One-Time PIN als initiale Login-Methode.
- Managed OAuth für kompatible MCP-Clients, nach erfolgreichem Integrationstest.
- Serverseitige Validierung von Identität und Berechtigungen.
- Individueller Zugriffsentzug möglich.

Die tatsächliche MCP-/OAuth-Kompatibilität wird vor Freigabe je Zielclient geprüft.

### 4. Produktvarianten

| Variante | Funktionsumfang |
|---|---|
| **Public** | Read-only Reference |
| **Pro** | Functions + Local Storage |
| **Premium** | Extended Options + Cloud Space |

Produktvarianten und ihre Berechtigungen sind unabhängig von Deployment-Umgebungen.

Während der geschlossenen Beta erfolgt die Freigabe zunächst über eine zentrale Allowlist. Eine vollständige Lizenzverwaltung ist nicht erforderlich.

### 5. Ressourcenisolation

Staging und Production erhalten getrennte:

- Environment Variables und Secrets
- KV-/D1-/R2-Ressourcen und Durable Objects, soweit verwendet
- OAuth-/Access-Konfigurationen
- Logs und Monitoring-Kontexte
- Nutzerdaten und persistenten Zustände

Keine gemeinsamen beschreibbaren Storage-Ressourcen zwischen Staging und Production.

### 6. Release-Prozess

1. Bestehenden G5-Zustand sichern und per Git-Tag referenzieren.
2. Production-Worker aus freigegebenem Commit bereitstellen.
3. Cloudflare Access und OAuth für Production konfigurieren.
4. MCP-Client-Kompatibilität und Zugriffskontrolle prüfen.
5. Beta-Nutzer gezielt freischalten.
6. Weitere Releases zunächst in Staging validieren.
7. Production ausschließlich über kontrollierte Freigaben aktualisieren.

Rollback erfolgt auf einen vorherigen freigegebenen Worker-Stand. Datenbankmigrationen und persistenter Zustand benötigen gegebenenfalls eigene Rücksetzstrategien.

### 7. Initiale Acceptance Criteria

- [ ] Staging und Production unabhängig deploybar.
- [ ] Bestehender Staging-MCP-Endpunkt bleibt erhalten.
- [ ] Production besitzt eigenständigen stabilen MCP-Endpunkt.
- [ ] Secrets und beschreibbare Ressourcen vollständig getrennt.
- [ ] Freigegebener Beta-Nutzer kann sich authentifizieren und autorisierte MCP-Tools aufrufen.
- [ ] Nicht freigegebener Nutzer erhält keinen Zugriff.
- [ ] Zugriff kann wirksam widerrufen werden.
- [ ] OAuth-Integration mindestens mit Codex und Claude erfolgreich getestet.
- [ ] Public Reference bleibt unabhängig zugänglich.
- [ ] Production-Release und Rollback sind reproduzierbar.

### 8. Architekturprinzip

**Develop freely. Release deliberately. Operate independently.**

Die gemeinsame Codebasis gewährleistet Konsistenz. Unabhängige Deployments sichern die Betriebsstabilität. Authentifizierung, Autorisierung und spätere Lizenzierung bleiben von einzelnen AI-Clients entkoppelt.

**Decision:** Staging/Production-Split vor Beginn der externen Beta etablieren. Kein zusätzliches Production-Repository erforderlich.
