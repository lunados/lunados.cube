# Design — Plansichten remote

Status: done · 2026-11-02 · umgesetzt (G5-Kern `0.8.0-proof`, Gateway `0.2.0-proof`, Offline-Parität 88/88, Host-Abnahme 7/7; D-6 revidiert: alle Sichten remote, CPU-Grenze dokumentiert)

## Context

Entscheidungen D-1–D-8 in [MILE-010](../../../../docs/02-Milestones/MILE-010-remote-plan-views.md) (entschieden 2026-11-02). Grundlage: G5 `0.7.0-proof` (MILE-006), G6 lokal (MILE-005–009).

## Decisions

- **Umfang (D-2, D-3):** `/9` und alle drei Plan-Tools mit VP-07 bis VP-11.
- **Gleichheit und Grenzen (D-4, D-5):** Remote = lokal, byte-gleich; Grenzen und Fehlercodes wie lokal.
- **Risiko (D-6):** Laufzeit zuerst messen; bei Überschreitung Umfang auf VP-10/VP-11 begrenzen.
- **Abnahme (D-7, D-8):** Rollen wie MILE-006; Live-Stichproben mit vorab festgelegten Erwartungen.

## Risks

- Rechenzeit der Plan-Printer in der Python-Laufzeit von Cloudflare (Pyodide) ist unbekannt.
- Antworten nahe 2 MiB plus Rahmen im Gateway.
