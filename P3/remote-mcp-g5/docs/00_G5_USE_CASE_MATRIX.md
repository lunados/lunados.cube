# G5 – Client-/Use-Case-Matrix (Freeze Documentation Addendum)

**Stand:** 2026-10-24 · **Profil:** `P3-MCP-REMOTE/0.1.0-proof` · **Freigabe:** `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.

**Remote-MCP-Endpunkt:** `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`.
**Öffentlicher Health-Endpunkt:** `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/health` (nicht authentifiziert).
**Privater Cloudflare Core:** `aiaeao-cube-g5-core`, `workers_dev:false`, keine öffentliche Route, Gateway Service Binding `CORE`.
**Separat:** Lokaler G4 MCP `stdio`; kein Cloudflare-Token erforderlich.

## Welcher Weg passt zu welchem Use Case?

| Anwendungsfall | Anbindung | Geheimnis | Geprüft / Einschränkung |
|---|---|---|---|
| Claude auf claude.ai / Claude Desktop | Remote Custom Connector (HTTPS) | `Authorization: Bearer <proof-token>` als Request Header | **Host bewiesen**: alle sieben Tools im Claude G5-R4-Lauf; finaler MIME-Host-Recheck noch offen |
| Zed, nativer Zed Agent | Settings → AI → MCP Servers → Add Remote Server, `context_servers` | Derselbe Proof-Token als Header; mögliche Ablage in lokaler Settings-Datei | **Noch nicht host-getestet**, Resources nur via `cube_read_reference` als sicherer Fallback |
| Zed mit externem Agenten (ACP) | Zed MCP kann an ACP-Agent weitergegeben werden, oder Agent nutzt eigenen MCP-Eintrag | Abhängig von tatsächlichem Weitergabepfad | **Nicht automatisch garantiert**: Weitergabe und Policy im Agent prüfen |
| Selbstständiger Remote-Agent mit MCP-SDK | Streamable HTTP + eigener Auth-Header | Aus lokalem Secret Store/Env des Agent-Prozesses | **Python SDK Remote-R3 bewiesen** (inkl. SHA-/Byte-Parität) |
| Local-first ohne Cloud | Lokaler G4 `stdio` | Kein Cloudflare Proof-Token | **G4 accepted**; für vertrauliche Daten ggf. bevorzugt |
| Mehrere Fremdnutzer / SaaS | **Nicht freigegeben** | Ein geteilter Proof-Token reicht nicht | OAuth/Identity, getrennte Quoten, Rollen, Auditing, Rotation erforderlich |
| Einfache HTTP-REST-API | **Nicht vorhanden** | – | `/mcp` spricht MCP JSON-RPC, nicht beliebige REST-Requests; `/health` ist nur Health |

### Immer derselbe fachliche Vertrag

- **P0**: 14 P0-Resources (13 gepinnte Quellen + Index), rein dokumentarisch; `cube_read_reference` ist der Tool-Fallback.
- **P1**: `cube_validate`; `PASS`, `FAIL`, `UNRESOLVED` sind fachliche Berichte; Konfigurationsfehler sind MCP-Fehler.
- **P2**: `cube_get_capabilities`, `cube_prepare_print`, `cube_check_print`, `cube_render_svg` für deklarierte VP-Daten; kein automatisches ACG→SVG.
- **P3 Discovery**: `cube_discover_surface`; sieben Tools insgesamt.
- Domänen bleiben getrennt: keine automatischen Aussagen über Wahrheit, Kausalität, Authority, Admission oder gemeinsamen Status.

### Belege / Versionsidentität

- User-Log vom 2026-10-24: `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 7 tools, 14 resources, P0, P1, VP06 byte parity` nach konsolidiertem Gateway-Deploy.
- Cloudflare Gateway Version-ID (User-Log): `4cd84f5b-0dd1-4361-aa97-eca964c32dc5`.
- `verify_release.py --require-npm-lock`: User-Log PASS, 28 Dateien auf SHA-256 geprüft, Registry-MIME entspricht P0-Lock.
- Claude R4: 27 tatsächliche Remote-Toolaufrufe + frühere Discovery; funktional grün; ursprünglich `INCOMPLETE`, da hostseitiger SVG-Hash und finales MIME/Evidence-Reconciliation offen waren.
- **Weder** R4 formal Accepted **noch** Production Authorized allein aus diesen Dokumenten ableiten.

## Einrichtung und Verifikation

1. `01_CLAUDE_CONNECTOR.md` – Claude.ai/Desktop über Cloud-Connector.
2. `02_ZED_REMOTE_MCP.md` – nativer Zed Agent und ACP-Weitergabe.
3. `03_INDEPENDENT_AGENT_AND_SDK.md` – eigener SDK-/Agent-Harness.
4. `04_BEARER_API_TOKEN_GATE.md` – Token-Gate, Security, Rotation, Negative Tests.
5. `05_RELEASE_EVIDENCE_AND_FREEZE.md` – Evidence, Freigabegates, Change Control.
6. `06_CLAUDE_R4_FINAL_RECHECK_PROMPT.md` – gezielter Host-Recheck ohne Wiederholung aller 27 Aufrufe.

**Referenzdokumente:** `P3/remote-mcp-g5/{SECURITY.md,DEPLOYMENT.md,RELEASE_FREEZE.md,G5_ACCEPTANCE.md}` und tatsächliche Gateway-Implementierung `gateway/src/index.mjs`.
