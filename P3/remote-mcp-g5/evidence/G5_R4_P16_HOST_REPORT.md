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

---

## Anhang A — Restliche Vektoren R-02, R-03, R-05 bis R-11, R-13 (Nachlauf 2026-10-25, ca. 20:00 MEZ)

**Status Anhang A: PASS (10/10).** Zusammen mit §4 sind damit alle 13 Vektoren R-01 bis R-13 live gegen G5 bestätigt. Dieser Anhang ersetzt den Punkt „Nicht geprüft: R-02, R-03, R-05 bis R-11 und R-13“ in §7.3.

**Quelle:** `P3/charge3-p16/fixtures/r01_r13_materialized.json` im Arbeitsbereich `~/SitesHeroku/lunados.cube`, nur gelesen. `input_text`, `input_format` und `context` habe ich unverändert gesendet. Connector: ausschließlich `AIAEAO Cube G5 Remote`, 10 Aufrufe `cube_validate` (Aufrufe 15–24).

| ID | Herkunft | `input_text` | Erwartet | Beobachtet | Diagnosepfad | `declared_context_sha256` | Status |
|---|---|---|---|---|---|---|---|
| R-02 | EXP-011 | `X:α:Conclusion["primary"]` | UNRESOLVED · `P1_INSTANTIATION_SLOT_MISSING` | UNRESOLVED · `P1_INSTANTIATION_SLOT_MISSING` | `/referents/4/slots/basis_refs` | `101f579b84cd7c0b66c861d51465d31bc9c2566dbc6ac2ccd88807e399bffd96` | PASS |
| R-03 | EXP-014-M02 | `X:α:Satisfaction["primary"]` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | `/referents/2/slots/expectation_ref` | `9164bfc21302d2134484c06c8dc7c4fb7527c2743c75afecd4902c90acfc9f41` | PASS |
| R-05 | EXP-014-M04 | `X:α:Conclusion["primary"]` | PASS | PASS, `diagnostics: []` | — | `93759b2662617cab708116b069ee354f8a42ad5d7dac4a3087f03e7c9271723b` | PASS |
| R-06 | RCP-01 | `X:α:Authority["primary"]` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | `/referents/3/slots/source_ref` (Capability) | `abd7fffb9d67c2063ae6cf7fc7af0c36a42563db5bd50579806b7f0be49e99f7` | PASS |
| R-07 | RCP-02 | `X:α:Authority["primary"]` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | FAIL · `P1_INSTANTIATION_SLOT_TYPE` | `/referents/3/slots/source_ref` (Role Binding) | `2bf5040a02c8650efb7fe15f45aa3a023f2911199cc4da0a327361d3a1f83a52` | PASS |
| R-08 | RCP-09 / EXP-014-M03 | `X:α:Admission["primary"]` | FAIL · `P1_INSTANTIATION_CONDITION` | FAIL · `P1_INSTANTIATION_CONDITION` („Admitted decision must declare authority_ref“) | `/referents/4/slots/authority_ref` | `d4574fcdb13c42f73da85979bb5f0a29880004bbe39f7f72a27fbf128a9ee513` | PASS |
| R-09 | RCP-09 | `X:α:Admission["primary"]` | PASS | PASS, `diagnostics: []` | — | `d0dc3a7400e17089d3821b438b187f4c47b48b0f2ef202a9f212993e2b82cb44` | PASS |
| R-10 | EXP-014-S08 | `X:α:Result["primary"]` | UNRESOLVED · `P1_INSTANTIATION_SLOT_MISSING` | UNRESOLVED · `P1_INSTANTIATION_SLOT_MISSING` | `/referents/2/slots/action_ref` | `9e08c126a17ae8f03321b38dcbbc2abfd45c802f9decb28f3127de1a73267bcf` | PASS |
| R-11 | EXP-015-H3 | `X:ζ:Perception["primary"]` | UNRESOLVED · `P1_LAYER_WITNESS_MISSING` | UNRESOLVED · `P1_LAYER_WITNESS_MISSING` („…before slots“) | `/referents/2/witness_ref` | `c0e7320db072fbd5a1e5641c66f6c926ce895af20cd8385ecc96290ad11eae5b` | PASS |
| R-13 | Scope-Grenze (Z-Zonen) | `Z:α:Ownership["primary"]` | UNRESOLVED · `P1_INSTANTIATION_PROFILE_REQUIRED` | UNRESOLVED · `P1_INSTANTIATION_PROFILE_REQUIRED` | `/` | `3db7eb42506b7eee034b11a67b2809eaa22460267f35b2093bdfbadd55cca1db` | PASS |

**Keine Hochstufung:** In allen zehn Reports stehen `epistemic_warrant`, `current_authority` und `canonical_admission` auf `NOT_EVALUATED`, und `source_warrant` ist `declared_unverified`. Auch die PASS-Fälle R-05 (Conclusion `verifies`) und R-09 (Admission `refused`) leiten weder Warrant noch Admission ab. Alle zehn Reports tragen `binding_context_profile: P1.6/instantiation-profile-v1`.

### A.1 Beobachtungen ohne Einfluss auf das Ergebnis

1. **R-13, Meldungstext:** Die Diagnose lautet „…requires an explicit instantiation profile not defined by binding-context/1“, obwohl der Kontext `binding-context/2` ist. Der Code ist korrekt, der Text ist für Z-Zonen unter /2 missverständlich.
2. **R-03, Profil-Konzept-Abweichung nicht gemeldet:** Der Hilfsreferent `item-1` hat `concept_id = X:endpoint:completion`, verweist aber per `instantiation_profile_ref` auf `p16-X:endpoint:expectation`. Gemeldet wird nur der Slot-Typfehler am primären Satisfaction-Referenten. Eine eigene Diagnose für diese Abweichung zwischen Profil und Konzept eines nicht-primären Referenten erscheint nicht. Mögliche Lücke, Kandidat für P1.7.

### A.2 Gesamtbild nach Anhang A

| Bereich | Belegt durch |
|---|---|
| EXP-011 (Evidence → Conclusion, fehlende Basis) | R-01, R-02 |
| EXP-014 M02 / M03 / M04 / S08 | R-03, R-08, R-04/R-05, R-10 |
| EXP-015 H3 (Witness vor Slots) | R-11 |
| EXP-019-RCP, strukturelle Vorbedingungen 01 / 02 / 09 | R-06, R-07, R-08/R-09 |
| Rückwärtskompatibilität und Scope-Grenze | R-12, R-13, A2 |

Die RCP-Effekt-Probes (reale Grants, Admission Point, Effekt-Zähler) sind dadurch nicht berührt und bleiben Echtbetrieb.

**Gesamtstatus des Berichts inklusive Anhang A: PASS.**
