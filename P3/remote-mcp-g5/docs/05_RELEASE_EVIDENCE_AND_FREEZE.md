# G5 – Formale Release-Evidence, Betriebsfreigabe und Freeze-Abschluss

**Datum:** 2026-10-24 · **Freeze:** `P3-MCP-REMOTE/0.1.0-proof` · **Scope:** G5-Dokumentationsaddendum, kein P0/P1/P2/G4-Code-Update und kein Cloudflare-Deploy.

## Prüfstatus – nachgewiesen vs. noch offen

| Bereich | Stand 24.10.2026 | Evidenz / Limit |
|---|---|---|
| G4 Local | ACCEPTED | Vorheriger Claude/Mac-Host- und MCP-SDK-Test |
| G5 offline | PASS | 17 Python-Vertragstests; JS-Gateway-Sicherheitstests, Release-Hashchecks |
| G5 R1 Core Cloudflare | PASS | Private Worker deployed; tatsächliche Fachausführung durch R3 belegt |
| G5 R2 Gateway | PASS | Gateway-Version `4cd84f5b-0dd1-4361-aa97-eca964c32dc5`, Service Binding CORE |
| G5 R3 Remote SDK | PASS **nach Konsolidierung** | Vom Nutzer gemeldeter kompletter `sdk_remote_smoke.py`-Lauf, inkl. Auth, Origin, sieben Tools, 14 Ressourcen, P1 und SVG-Byte-Parität; aktueller Scriptstand prüft MIME gegen gepinnten Lock |
| G5 Source Freeze | PASS lokale Verifikation | `verify_release.py --require-npm-lock`: npm Full Lock vorhanden, 28 Source-Dateien SHA-256 und Registry-MIME PASS |
| G5 R4 unabhängiger Claude Host | Vorheriger Report funktional PASS, formell INCOMPLETE | 27 + 1 Remote Calls; ursprüngliche MIME-Divergenz, hostseitiger SVG-Hash und R3-Evidence-Nachweis offen; **neuer Host-MIME-Recheck nicht gemeldet** |
| GitHub Commit/Tag | **NICHT DURCHGEFÜHRT** | Aktuellen Branch/Index des Nutzers nicht behaupten |
| Production Authorization | **NICHT ERTEILT** | `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` gilt unverändert |

## Finales Evidenzverfahren

### 1. Lokale Source- und Security-Checks

```sh
cd "$HOME/Downloads/lunados.cube"
python3 P3/remote-mcp-g5/scripts/verify_g5.py
python3 P3/remote-mcp-g5/scripts/verify_release.py --require-npm-lock
cd P3/remote-mcp-g5/gateway
npm ci
npm audit --omit=dev
npm audit
npm run check:freeze
npm run dry-run
```

**Stop** bei Sicherheitswarnungen; keinen `npm audit fix --force` als automatisches Releaseverfahren ausführen. `package-lock.json` muss zusammen mit `package.json` versioniert werden; `node_modules` niemals.

### 2. Nachvollziehbares R3-Protokoll (sanitized)

```sh
cd "$HOME/Downloads/lunados.cube"
source P3/adapters/mcp-local/.venv/bin/activate
export AIAEAO_G5_URL='https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp'
export AIAEAO_G5_TOKEN="$(security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' -w)"
python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py \
  --evidence P3/remote-mcp-g5/evidence/G5_R3_POST_FREEZE_PASS.json
unset AIAEAO_G5_TOKEN
```

JSON wird ausschließlich nach bestandenen Assertions erzeugt. Manuell auf sensitive Inhalte prüfen, **erst dann committen**. Im Acceptance-Eintrag festhalten: Zeitstempel, Runner-Version, Gateway-Version-ID, P0-Lock, P2 Golden-SVG SHA.

### 3. Unabhängiger Host-Recheck

Den Prompt aus `06_CLAUDE_R4_FINAL_RECHECK_PROMPT.md` nutzen. Der Host muss **remote** aufrufen, Markdown-Resource-MIME (`text/markdown`) selbst bestätigen und den R3-Client-Beleg als externen Nachweis kenntlich machen. Für einen vollständigen eigenständigen Host-PASS außerdem tatsächliche SVG-Bytes unabhängig hashen. Wenn der Host diese nicht bereitstellen kann, den Punkt `NOT TESTED` belassen; SDK-Ergebnis kann R3, aber nicht eine behauptete hostseitige Hashprüfung beweisen.

### 4. Formale Freigabe dokumentieren

Nach Vorliegen beider Evidence-Dateien in `G5_ACCEPTANCE.md` mit explizitem Nachweislink ergänzen, z. B.:

```text
R3 = PASS; evidence/G5_R3_POST_FREEZE_PASS.json; gateway_version=4cd84f5b-...; SHA checks verified.
R4 = PASS / INCOMPLETE; evidence/G5_R4_HOST_FINAL_REPORT.md; scope, genuine calls, omissions.
SOURCE_FREEZE = PASS; npm lock + SHA256 manifest committed.
PRODUCTION = NOT AUTHORIZED.
```

Keine Scheingenauigkeit: erst nach Host-Recheck `G5-R4 ACCEPTED` vergeben. Keine Git- oder Cloudflare-Operation wird durch dieses Addendum ausgeführt.

### 5. GitHub-Commit & Release Tag: eigener Nutzer-Gate

- Source Freeze und Lock diffen, auf Secret-/Build-Artefakte prüfen (`git status`, `git diff`, `git diff --cached`).
- G5-P3-Änderungen, Dokumentation und bereinigte Evidence gezielt stagen.
- Commit und ggf. Tag **erst nach expliziter Entscheidung**. Das Dokument führt keinen Push aus.
- Der Produktivstatus bleibt auf `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` auch bei einem erfolgreichen Proof-Tag.

## Rollback / Sicherheit

Im Fehlerfall Gateway auf zuletzt funktionierende Worker-Version zurücksetzen oder öffentliche Gateway-Route sperren. Privaten Python-Core nicht öffentlich machen. Bei Token-Leck Secret rotieren und Clients aktualisieren; Monitoring und Kosten gesondert prüfen. Keine Änderungen an `cube.lunados.net`.

## Terminologie: Freeze ≠ Production

**Functional Proof:** Cloudflare R1-R3 bereits bestätigt; unabhängige Claude-R4-Evidenz wird formell geschlossen.
**Source Freeze:** dokumentierter, geprüfter P3-Kandidatenstand, **nicht** behaupteter GitHub-Push.
**Production Authorization:** eigene spätere Entscheidung mit OAuth/Identity, Quotas, Governance, Observability, Datenschutz, Abuse-Schutz.
