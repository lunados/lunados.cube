# AIAEAO Cube P1.6 — Charge 3 Release Freeze / Handover

**Cut:** 2026-10-25 · **Target:** `P1.6/instantiation-profile-v1` über `P3-MCP-REMOTE/0.1.0-proof` · **Status:** `REMOTE_PROOF_EVIDENCE_ACCEPTED; GIT_FREEZE_PENDING` · **Production:** `NOT AUTHORIZED`.

## Freeze-Grenze

- P0 v9.4, sieben Z-Zonen, P1.1–P1.5, P1.6 Charge 1+2 und P2/VP-06 **nicht verändern**.
- Lokale G4-Golden-Card und G5-Gateway-Schema mit **7 Tool-Signaturen** beibehalten; **14 P0-Ressourcen** bleiben read-only.
- Charge 3 ist der gesondert SHA-geprüfte **P3-Overlay** `AIAEAO_Cube_P1_6_Charge_3_MCP_G5_v1_1.zip` (SHA-256 `5d49c43923c6f8722173974b89114d20320b0914be710b841414253b9a57a781`). Der historische `P3/remote-mcp-g5/SHA256SUMS.txt` beschreibt den **älteren** G5-Quellstand; er darf nicht als aktueller Charge-3-Checksum-Gate interpretiert oder still überschrieben werden.
- Für Charge 3 gilt `P3/charge3-p16/CHARGE3_SOURCE_SHA256SUMS.txt` mit `P3/charge3-p16/scripts/verify_sources.py`; die vollständige Offline-Kette läuft über `verify_charge3.py`.
- P1.6 im G5-Core nur in-process, `binding-context/2` explizit, fehlende Module fail-closed, `/1` unverändert.
- Keine neuen frei ausführbaren Tools, keine unbegrenzten URLs, keine Credential-Weitergabe, kein automatisches ACG→SVG, keine Authority-Promotion.

## Release-Abnahme

Evidence-Manifest: `P3/charge3-p16/release/CHARGE3_EVIDENCE_MANIFEST.json` (Pfadangaben relativ zum Repo-Root). Drei Roh-Evidence-Artefakte unter `P3/remote-mcp-g5/evidence/` bleiben **byte-identisch** zu den hochgeladenen Originalen.

### Read-only-Gate

```bash
cd "$HOME/Downloads/lunados.cube"
python3 P3/charge3-p16/release/scripts/verify_charge3_release.py
python3 P3/charge3-p16/scripts/verify_charge3.py
```

Der erste Befehl überprüft SHA-256 und inhaltliche Kohärenz der Evidence; der zweite die gesamte vorhandene lokale Offline-Regression. Beide Befehle führen **kein** Deployment durch und **keine** Remote-Tools aus. Der erste Befehl bestätigt **nicht** den tatsächlichen Claude-Aufruf oder den exakten Live-Cloudflare-Code, sondern dessen dokumentierte Nachweise und die lokal bereitgestellten Artefakte.

### Git-Freeze (bewusster menschlicher Gate)

```bash
cd "$HOME/Downloads/lunados.cube"
git status --short
git diff --check
git diff --stat
# Quell- und Evidence-Dateien nur nach Sichtprüfung gezielt stagen,
# keine generelle Übernahme von .venv, .g5-runtime, dist, node_modules, Tokens oder Logs.
git diff --cached --check
git diff --cached --stat
```

Uncommittete P1.6 Charges 1/2, Charge 3 P3-Overlay und bereits committed G5-Baseline im **gleichen reproduzierbaren Git-Snapshot** sichern. Der Git-Stand aus dem lokalen Mac wurde hier nicht eingesehen; daher wird **kein Commit, Push, Tag oder Commit-SHA behauptet**. Erst nach lokaler Prüfung und bewusstem Commit optionaler Proof-Tag `p1.6-charge3-g5-proof-2026-10-25` (vorher auf Kollisionsfreiheit prüfen). Ein Proof-Tag ist **keine** Produktivfreigabe.

## Known limits / offene Gates

1. Der Hostbericht zeigt 14 dokumentierte Host-Operationen einschließlich drei nicht maßgeblicher Vorlauf-Calls. Er enthält keine MCP-Rohtranskripte und keine zusätzliche erneute R4-Prüfung sämtlicher 13 Vektoren.
2. In R4 wurde `morphology.md` nur über Listing/Index auf MIME überprüft; die P0-Leseantwort wurde für `visual/README.md` geprüft.
3. Der G5-R3-SVG-Golden-Hash und der G5-R4-SVG-Golden-Hash unterscheiden sich **erwartungsgemäß**, weil unterschiedliche Fixtures gerendert wurden.
4. Cloudflare-Version `77189c21-218a-4f83-b292-e4ed73a38bf7` stammt aus der vom Nutzer mitgeteilten Deployment-Ausgabe; die drei Evidence-Dateien enthalten keine attestierte Worker-Build-ID.
5. Bestehende G5-Release-Metadaten können einen vor der Host-Abnahme gebildeten Proof-Status anzeigen; keine stillschweigende Reversionierung oder erneutes Deployment für dieses Evidence-Addendum.
6. Kein OAuth, keine vollständige Mandantentrennung, Betriebsüberwachung, Abuse-/Quota-Governance oder formal geprüfter Production-Rollback als Teil dieser Charge.

## Nachfolgender Workspace-Umzug

Erst **nach** konsistentem Git-Freeze von `~/Downloads/lunados.cube` nach `~/SitesHeroku/lunados.cube` wechseln. Nicht zwei Arbeitskopien unabhängig weiterpflegen. Absolute MCP-Hostpfade und Python-venv aktualisieren und anschließend die beiden lokalen Gates im Zielverzeichnis erneut ausführen. Keine Cloudflare-Konfigurationsänderung allein wegen des Pfadwechsels.
