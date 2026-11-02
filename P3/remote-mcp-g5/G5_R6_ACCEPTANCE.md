# G5 R6 · MILE-011 TASK-067

Status: **offline geprüft; Bereitstellung und Host-Abnahme ausstehend**.

Der private Core `P3-MCP-REMOTE/0.9.0-proof` enthält P1.14 und den lokalen G6-Printer VP-07.6. Das bestehende Gateway behält zehn Tools und seine Authentifizierung; `cube_plan_source` akzeptiert zusätzlich `origin_lines`. `cube_discover_surface` zeigt P1.14 und VP-07.6 an.

Die Erwartungen wurden vor dem Remote-Code in `evidence/G5_R6_EXPECTATIONS.json` fixiert (Commit `58ae4a8`): 12 Validierungen HO-01…HO-12, 13 Flow-Ketten OL-01…OL-12 und Discovery. `scripts/r6_parity.py` prüft dieselben Ergebnisse im isoliert zusammengestellten Core, einschließlich SVG-Digests und Dateizugriffs-Audit: **26/26 wie erwartet**, 0 externe Dateizugriffe, maximal 0,879 s CPU unter CPython. `scripts/r6_legacy_parity.py` prüft die 87 historischen R5-Aufrufe gegen ihre eingefrorenen Erwartungen, ohne deren Evidence zu überschreiben: **87/87 bytegleich**.

Die Live-Abnahme folgt der Anleitung in `DEPLOYMENT.md` §10. `scripts/r6_remote_acceptance.py` prüft alle neuen Aufrufe über das authentifizierte Gateway. Danach werden neun vorher festgelegte Aufrufe im Host überprüft. Ein CPU-Abbruch ist als Abweichung zu dokumentieren, nicht als PASS. Die P1-, P2- und Remote-Ergebnisse behaupten weder Wahrheit noch Autorität oder Admission.
