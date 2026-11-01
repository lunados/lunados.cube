# MILE-001-A — Ausgangsstand und Änderungskorridor

Stand: 2026-11-01. Vor Änderung wurde eine **frische lokale stdio-MCP-Verbindung** mit dem vorhandenen SDK 2.0.0 geöffnet. [Rohantwort vor Änderung](a-before.json) enthält zehn Toolregistrierungen, Discovery, Legacy-Card und Quellhashes. Die Repo-Root-venv enthält kein MCP; verwendet wird die vorhandene Adapter-venv.

| Kontext | Entry-Profil | Codequelle unter P1 |
|---|---|---|
| /1 | P1-VC/1.0.0 | semantic-validator-v1 |
| /2 | P1.6/instantiation-profile-v1 | instantiation-profile-v1 |
| /3 | P1.8/simulation-profile-v1 | simulation-profile-v1 |
| /4 | P1.9/comparison-profile-v1 | comparison-profile-v1 |
| /5 | P1.10/migration-profile-v1 | migration-profile-v1 |
| /6 | P1.10.1/migration-profile-v2 | migration-profile-v2 |
| /7 | P1.11/migration-methods-v1 | migration-methods-v1 |

Dispatch-Quelle: `P3/adapters/mcp-local/aiaeao_mcp_local/p1_adapter.py::_validator_for`; Registrierung: `server.py`; Discovery: `surface.py`. Höhere Kontexte laden vorherige Module mit. Vorher nennt die Beschreibung von `cube_validate` nur /1 und /2; die lokale Discovery nennt keine Kontext-/Entry-Profilzuordnung.

## Vor Implementierung festgelegte Ergänzung

Additives Feld `domains.P1.validation_contexts`, eigenes Format `aiaeao.cube.local-validation-discovery/1`. Pro Kontext: implementierter Dispatch, Entry-Profil, erforderliche Quellmodule, beobachtete Dateipräsenz und ausdrücklich **keine** Laufzeit-Ladebestätigung. Kein impliziter Versionswechsel. Der bestehende äußere Surface-Vertrag erlaubt zusätzliche P1-Metadaten; seine Versionskennung bleibt erhalten, das neue Feld hat eine eigene Version und ein eigenes Schema.

Die zehn registrierten lokalen Operationen bleiben unverändert: vier Legacy-Printer-Tools, Read-Reference, Validate, Discover-Surface und drei Plan-Tools. P0 bleibt dokumentarisch, P1 deklarative Prüfung, P2 Darstellung. G5 wird weder geändert noch als mitgeprüft ausgegeben. Der öffentliche Reader bietet damit keine lokale Validierungsfähigkeit.

## Geschützte Basis

Kanonische UTF-8-JSON-Hashes (sortierte Schlüssel, kompakt, ensure_ascii=false):
- Legacy: `670da85b2783b08b512139a87dd3ea964a2d5f5f4b18d0b0730bf37c9aa9a51a`
- G4: `c97504dcde28e1692d52352e00b4912524589281a8ddc774b4563bf742cc27f9`

Die Ergänzung erfolgt ausschließlich im lokalen Discovery-Pfad. Diese beiden Ausgaben und Validatorsemantik bleiben unverändert. Dateipräsenz beweist keine erfolgreiche Initialisierung aller Validatoren; konkrete Laufzeitbelege werden separat gespeichert.
