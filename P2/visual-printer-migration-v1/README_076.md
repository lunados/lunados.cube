# VP-07.6 · Herkunftslinien

Opt-in-Profil `P2-VP-MIGRATION/0.7.6` für `cube.flow`. Der Printer zeigt die gebundene Herkunft jeder Kante als Linienart und Text. `declared` ist durchgezogen, `derived` gestrichelt, `unknown` und nicht gebunden sind gepunktet. Eine nicht auflösbare Ableitungsgrundlage ergibt `VP07_ORIGIN_UNRESOLVED` als Warnung; der Report bleibt ohne P1-Urteil.

`from-plan` akzeptiert einen Migrationsplan mit Binding Context `/10` oder `--statements` für `statement-set/1` bzw. `/2` mit optionalen `--records`. Die Aussagenmenge benötigt einen `/10`-Kontext. Für die Darstellung der Herkunft wird `--origin-lines` gesetzt; `print-panels` verwendet `cube.flow` und `subject` oder `object` als Partition. Dieselben Eingaben stehen lokal in G6 über `cube_plan_source` zur Verfügung; `cube_plan_views` liefert Panels und Report, `cube_plan_check` prüft die Ausgabe.

```sh
python3 -m vpmigration from-plan --context context.json --statements set.json --records records.json --profile P2-VP-MIGRATION/0.7.6 --origin-lines --out source.json
python3 -m vpmigration print-panels --source source.json --view cube.flow --partition subject --granularity standard --out panels
python3 -m vpmigration check-panels --dir panels
```

Die 13 OL-Fälle und das unabhängige Orakel liegen in `fixtures/ol01_ol12_materialized.json` und `oracles/independent_ol01_ol12.json`. `scripts/run_vectors_ol.py` führt sie aus. `tests/test_vp076.py` prüft zusätzlich Text und Linien je Kante sowie CLI/G6-Parität. `DIAGNOSTICS_076.json` und `RULE_COVERAGE_076.json` ergänzen die eingefrorenen Basisregister. Die historischen Output-Pins und `VP07_SHA256SUMS.txt` bleiben unverändert.
