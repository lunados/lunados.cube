# Deliver remote plan views

Status: done · 2026-11-02 · archiviert · [MILE-010](../../../../docs/02-Milestones/MILE-010-remote-plan-views.md) · [Nachweis](../../../../docs/10-Evidence/MILE-010/C-RESULT.md)

## Why

G5 prüft remote bis `binding-context/8`; `/9` (P1.13, MILE-008) endet remote geschlossen. Die Plansichten VP-07 bis VP-11 laufen nur lokal (G6, `remote_available: false`).

## What Changes

- G5-Kern `P3-MCP-REMOTE/0.8.0-proof`: `cube_validate` mit `/9`; die drei Plan-Tools mit den Printern VP-07 bis VP-11.
- Gateway: drei neue Tools mit Schemas; Discovery.
- Bereitstellung und Host-Abnahme R5.

## Capabilities

### New Capabilities

- `remote-plan-views`: Plansichten über den Remote-Connector, byte-gleich zu lokal.

### Modified Capabilities

- `remote-coverage-validation`: um `binding-context/9` erweitert.

## Impact

Nur `P3/remote-mcp-g5` (Kern, Gateway, Zusammenbau, Prüfskripte, Nachweise). P0, P1, P2, lokaler Adapter und lunados.lib unverändert. Grobe Planung: 2,25–3,5 PT.
