# Design — Plansichten remote

Status: proposed · Entscheidungen offen

## Context

Entscheidungen D-1–D-8 in [MILE-010](../../../docs/02-Milestones/MILE-010-remote-plan-views.md) (Vorschlag, offen). Grundlage: G5 `0.7.0-proof` (MILE-006), G6 lokal (MILE-005–009).

## Decisions

- **Umfang (D-2, D-3):** `/9` und alle drei Plan-Tools mit VP-07 bis VP-11.
- **Gleichheit und Grenzen (D-4, D-5):** Remote = lokal, byte-gleich; Grenzen und Fehlercodes wie lokal.
- **Risiko (D-6):** Laufzeit zuerst messen; bei Überschreitung Umfang auf VP-10/VP-11 begrenzen.
- **Abnahme (D-7, D-8):** Rollen wie MILE-006; Live-Stichproben mit vorab festgelegten Erwartungen.

## Risks

- Rechenzeit der Plan-Printer in der Python-Laufzeit von Cloudflare (Pyodide) ist unbekannt.
- Antworten nahe 2 MiB plus Rahmen im Gateway.
