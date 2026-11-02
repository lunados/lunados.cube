# MILE-010 — Nachweise

Stand: 2026-11-02 · abgeschlossen ([C-RESULT](C-RESULT.md)).

| Datei | Inhalt |
|---|---|
| [Spezifikation G5 R5](../../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md) | TASK-058: Abnahmespezifikation, Q-1–Q-10, Präzisierungen und Live-Befund (§10) |
| [G5-Erwartungen R5](../../../P3/remote-mcp-g5/evidence/G5_R5_EXPECTATIONS.json) | TASK-059: Erwartungen für 87 Aufrufe aus den lokalen Server-Funktionen, vor Code |
| [Offline-Parität](../../../P3/remote-mcp-g5/evidence/G5_R5_OFFLINE_PARITY.json) | TASK-060: Kern = lokal, 88/88, Rechenzeit je Aufruf |
| [Skript-Läufe 1–4](../../../P3/remote-mcp-g5/evidence/G5_R5_LIVE_SCRIPT_RUN4.json), [CPU-Ereignis](../../../P3/remote-mcp-g5/evidence/G5_R5_CORE_CPU_EVENT.json) | TASK-061: Live-Abnahme per Skript, 87/88 bzw. 86/88, Abbruch `exceededCpu` |
| [Host-Bericht R5](../../../P3/remote-mcp-g5/evidence/G5_R5_HOST_REPORT.md) | TASK-061: Host-Abnahme über den Connector, Teilmenge 7/7, PASS |
| [verify_mile010.py](verify_mile010.py), [verification.json](verification.json) | Abschlussprüfung (Reihenfolge, G5-Gates, Live-Läufe, Host-Bericht, Schichten, Prüfsummen, Links); `all_ok` |
| [C-RESULT.md](C-RESULT.md), [MANIFEST.json](MANIFEST.json) | Abschlussnachweis und Hashes |
