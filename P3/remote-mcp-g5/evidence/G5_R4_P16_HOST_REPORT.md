# G5 R4 — AIAEAO Cube P1.6 Host-Abnahme

**Gesamtstatus: PASS**

| Feld | Wert |
|---|---|
| Datum | 2026-10-25, ca. 18:45–18:50 MEZ |
| Prüfer | Claude (Host-Session), unabhängig von der Implementierung |
| Connector | ausschließlich `AIAEAO Cube G5 Remote` (`transport: remote_mcp_streamable_http`) |
| Nicht verwendet | lokale G4-Instanz, simulierte Tool-Aufrufe |
| Remote-Release | `aiaeao-cube-mcp-remote-g5`, `P3-MCP-REMOTE/0.1.0-proof`, Status `remote_proof_not_accepted` |
| Testvektoren | `P3/charge3-p16/fixtures/r01_r13_materialized.json` (R-01, R-04, R-12), nur gelesen und unverändert gesendet |
| Änderungen | keine an Code, Fixtures, Cloudflare oder Secrets; kein Deployment, keine Production Authorization. Einzige Schreiboperation: diese Berichtsdatei. |

## 1. Tatsächliche Tool-Aufrufe

| # | Aufruf | Zweck |
|---|---|---|
| 1 | `cube_discover_surface` | Schritt 1 |
| 2 | Host `ListMcpResources` (Server `AIAEAO_Cube_G5_Remote`) | Schritt 2: Anzahl, MIME-Typen |
| 3 | Host `ReadMcpResource` `https://cube.lunados.net/v9.4/visual/README.md` | Schritt 2: MIME in der Leseantwort, Inhalt für den clientseitigen Hash |
| 4 | Host `ReadMcpResource` `aiaeao://p0/resources/v1` | Schritt 2: Index mit Bytes und SHA-256 |
| 5 | `cube_read_reference` `morphology.md` (`max_bytes` 256) | Schritt 2: Erreichbarkeit, `total_bytes` |
| 6 | `cube_render_svg` (Golden-Job `P2/visual-printer-release-v1/examples/tree_governance_overview.job.json`) | Schritt 5 |
| 7–9 | `cube_validate` mit repo-abgeleiteten Vektoren (Vorlauf, siehe §7) | ersetzt durch 12–14 |
| 10 | `cube_validate` A1: Inhalt im Format /2 unter dem Label `binding-context/1` | Schritt 3: /2 nur explizit |
| 11 | `cube_validate` A2: Legacy-/1-Kontext `probe:exp011b` vom selben Tag | Schritt 3: /1 rückwärtskompatibel |
| 12 | `cube_validate` **R-01** (materialisierter Vektor) | Schritt 3 und 4 |
| 13 | `cube_validate` **R-04** (materialisierter Vektor) | Schritt 3 und 4 |
| 14 | `cube_validate` **R-12** (materialisierter Vektor) | Schritt 3 und 4 |

## 2. Schritt 1 — Capability-Oberfläche

| ID | Prüfung | Erwartet | Beobachtet | Status |
|---|---|---|---|---|
| S1.1 | Tools | 7 | `cube_get_capabilities`, `cube_prepare_print`, `cube_check_print`, `cube_render_svg`, `cube_read_reference`, `cube_validate`, `cube_discover_surface` | PASS |
| S1.2 | P1.6-Deskriptor | vorhanden | `p16_instantiation.profile = P1.6/instantiation-profile-v1`; `activation = explicit_context_format_2_only`; `binding_context_formats = [/1, /2]`; `scope = declared_X_endpoint_slots`; Warrant, Authority und Admission `NOT_EVALUATED` | PASS |
| S1.3 | Remote-Status | `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` | `deployment.remote_status = G5_PROOF_NOT_PRODUCTION_AUTHORIZED` | PASS |

## 3. Schritt 2 — P0-Ressourcen

| ID | Prüfung | Erwartet | Beobachtet | Status |
|---|---|---|---|---|
| S2.1 | Anzahl | 14 | 14 im Host-Listing (13 Dateien + `aiaeao://p0/resources/v1`); entspricht `domains.P0.resource_count = 14` | PASS |
| S2.2 | MIME `visual/README.md` | `text/markdown` | Listing **und** Leseantwort: `text/markdown` | PASS |
| S2.3 | MIME `morphology.md` | `text/markdown` | Listing und Index: `text/markdown`. Wegen der Größe (268.040 Bytes) nicht über `ReadMcpResource` gelesen; der Tool-Fallback meldet keinen MIME-Typ. | PASS (Listing-Ebene) |
| S2.4 | Hash `visual/README.md`, clientseitig berechnet | Index: `2e985b26bdb250998b35c8d545f04c58531023de93d09b7e8a3e9d10b07c16b2`, 813 Bytes | empfangener Text, selbst gehasht: 813 Bytes, `2e985b26bdb250998b35c8d545f04c58531023de93d09b7e8a3e9d10b07c16b2` | PASS |

Der Index meldet `snapshot_lock_sha256 = cb259c5962a61c507ace6260d37ae364cf6658794a115052e3bc4fefdca477a1` und `verified_repository_commit = 99efc506dbe2dd92a045bf72f4d1a905310b8154`. Beides habe ich nicht selbst nachgeprüft.

## 4. Schritt 3 — P1.6-Vektoren

| ID | `input_text` · Kontextformat | Erwartet | Beobachtet | `declared_context_sha256` | Status |
|---|---|---|---|---|---|
| R-01 | `rel("supports",Y:α:Evidence["item-3"],X:α:Conclusion["primary"])` · /2 | PASS, `required_codes: []` | PASS, `diagnostics: []`, `binding_context_profile: P1.6/instantiation-profile-v1` | `ee6eb8c12362425dd4eaaadd4eb46fcf65210859751f12c61334acd484955fa0` | PASS |
| R-04 | `X:α:Conclusion["primary"]` · /2, `basis_refs` → X Satisfaction | FAIL, `P1_INSTANTIATION_SLOT_TYPE` | FAIL, `P1_INSTANTIATION_SLOT_TYPE` an `/referents/4/slots/basis_refs/0` | `46548bf1c03df7a6c9e32cf223966c077972636e58cfb96eedde0a8e999c2cd4` | PASS |
| R-12 | `X:α:Conclusion["primary"]` · /1 | UNRESOLVED, `P1_INSTANTIATION_PROFILE_REQUIRED` | UNRESOLVED, `P1_INSTANTIATION_PROFILE_REQUIRED`; kein Feld `binding_context_profile` | `56aafc49aeb1d378c63ec2d1f8f83e399a7d32929807700307fc7d830a631e5f` | PASS |

Bei R-01 ist die Basis der Conclusion eine Perception (`item-1`), die selbst über P1.6-Slots gebunden ist. Zwei verkettete Endpoint-Profile wurden gemeinsam aufgelöst.

### Aktivierung und Rückwärtskompatibilität

| ID | Prüfung | Erwartet | Beobachtet | Status |
|---|---|---|---|---|
| S3.4 | /2 nur explizit (A1) | Inhalt im Format /2 unter dem Label /1 wird abgewiesen | MCP-Fehler `P1_MCP_CONFIG_INVALID`, `semantic_status: NOT_EVALUATED`, `files_written: false` | PASS |
| S3.5 | P1.6-Pfad nur bei /2 | `binding_context_profile` nur bei /2 | vorhanden bei R-01 und R-04, fehlt bei R-12 und A2 | PASS |
| S3.6 | /1 rückwärtskompatibel (A2) | identisch mit dem Lauf vor P1.6 | PASS; `input_sha256 52da869ce8fc936dba4a16f602603aa6aba3a18f1c0c1217cdb04cad3f57747a` und `declared_context_sha256 8342a304fd77561c80f1ef5d69f175603713827589bca8938cf25c0dae031af5` bytegleich mit dem Lauf vom selben Nachmittag vor dem P1.6-Deployment | PASS |

## 5. Schritt 4 — Keine Hochstufung

| ID | Prüfung | Beobachtet | Status |
|---|---|---|---|
| S4 | `epistemic_warrant`, `current_authority`, `canonical_admission` = `NOT_EVALUATED` | R-01, R-04, R-12, A2 und Render-Report: jeweils `NOT_EVALUATED`; `source_warrant: declared_unverified`. Aus dem PASS von R-01 wird keine Authority, Truth oder Admission abgeleitet. | PASS |

## 6. Schritt 5 — Clientseitiger SVG-Hash

| ID | Prüfung | Erwartet | Beobachtet | Status |
|---|---|---|---|---|
| S5 | SHA-256 der empfangenen SVG-Bytes, clientseitig | Golden `examples/tree_governance_overview.svg`, selbst gehasht: `e9bd5847f0f526d4a9551e139f2eb4c0259496a95399ca765707dde78ddc4a57`; stimmt mit `VP06_SHA256SUMS.txt` überein | empfangenes `artifact.svg_text` (UTF-8, 10.926 Bytes), selbst gehasht: `e9bd5847f0f526d4a9551e139f2eb4c0259496a95399ca765707dde78ddc4a57` | PASS |

Der vom Server gemeldete `svg_sha256` ist nicht in den Vergleich eingeflossen. Das SVG kam als JSON-String im Tool-Ergebnis an. Ich habe ihn unverändert übernommen, JSON-dekodiert und als UTF-8 gehasht. Ein Übertragungsfehler hätte nur einen falschen Mismatch erzeugen können, keinen falschen Treffer. Render-Report: `status PASS`, `completeness PARTIAL_EXPLICIT`, 18 Invarianten bestanden, darunter `NO_SEMANTIC_AUTHORITY_PROMOTION`.

## 7. Abweichungen und Hinweise

1. **Vorlauf mit Ersatzvektoren (Aufrufe 7–9):** Die angekündigten Vektoren waren zunächst nicht übermittelt. Als Ersatz habe ich Vektoren aus `P1/instantiation-profile-v1/oracles/independent_r01_r13.json` und `fixtures/valid_conclusion_context_v2.json` gebaut, gelesen aus `~/SitesHeroku/lunados.cube`. Sie ergaben dieselben Status und Codes (`e60b8af1…`, `17caf697…`, `ffcc60f2…`). Maßgeblich für diesen Bericht sind die Aufrufe 12–14 mit den materialisierten Vektoren.
2. **Unabhängigkeit:** Vektoren und Erwartungswerte stammen aus dem Projekt-Repo, nicht von einer externen Stelle. Unabhängig sind die Host-Ausführung und die Hash-Berechnung.
3. **Nicht geprüft:** R-02, R-03, R-05 bis R-11 und R-13 (nicht beauftragt); MIME von `morphology.md` beim tatsächlichen Lesen über Resources.
4. **Zwei Repo-Kopien:** `~/Downloads/lunados.cube` (Fundort der materialisierten Vektoren, Ablage dieses Berichts) und `~/SitesHeroku/lunados.cube`.

## 8. Ergebnis

| Schritt | Status |
|---|---|
| 1 Capability-Oberfläche | PASS |
| 2 P0-Ressourcen und MIME | PASS |
| 3 R-01, R-04, R-12; /2 explizit; /1 rückwärtskompatibel | PASS |
| 4 Keine Hochstufung | PASS |
| 5 Clientseitiger SVG-Hash | PASS |
| **Gesamt** | **PASS** |

Dieses PASS bestätigt das beobachtete Verhalten des G5-Host-Connectors für die genannten Fälle. Es ist keine Production Authorization: G5 bleibt `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
