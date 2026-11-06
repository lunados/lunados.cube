# Beta-Zugang am bestehenden G5-Endpunkt

Status: done · 2026-11-06 · archiviert · [MILE-019](../../../../docs/02-Milestones/MILE-019-beta-token-access.md) · [EPIC-013](../../../../docs/03-Epics/EPIC-013-beta-token-access.md) · [Abschluss](../../../../docs/10-Evidence/MILE-019/CLOSURE.md)

## Why

Der G5-Gateway akzeptiert derzeit nur einen gemeinsamen Bearer-Token. Ein Beta-Token an dessen Stelle würde den bestehenden Entwicklerzugang unterbrechen. Der eingefrorene MILE-017-Entwurf mit zwei Deployments ist für diesen Zweck vorerst nicht nötig.

## What Changes

- Der vorhandene Entwickler-Token bleibt gültig.
- Bis zu zwölf getrennte, optionale Beta-Tokens können am selben `/mcp`-Endpunkt verwendet und einzeln entzogen werden.
- Einrichtung, Negativfälle, Live-Zugriff und Codex-/Claude-Verbindung werden nachvollziehbar geprüft.

## Impact

Nur P3-Gateway, dessen Tests und Betriebsanleitung. Kein zweiter Worker, keine Änderung des privaten Core, keine Cube-Vertragsänderung, keine PIN-/Access-/OAuth-Integration. Die bekannten G5-Grenzen bleiben bestehen.
