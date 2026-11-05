# VP-07.7 · Modulkörper, Grant, Evidence und Content

Opt-in-Profil `P2-VP-MIGRATION/0.7.7`: wie `0.7.6`, aber die geschlossene Konzepttabelle des Adapters kennt zusätzlich `Z:module-body:core`, `connector`, `toolbox`, `adapter`, `Z:boundary:grant` sowie `Y:resource-object:evidence` und `content` – jeweils mit dem kanonischen VG-Anker und der vorgeschlagenen Form ihrer Familie. X-Endpunkte bleiben außen vor. Spezifikation: `VP07_7_ACCEPTANCE_SPEC.md`.

```sh
python3 -m vpmigration from-plan --context context.json --plan plan-id --profile P2-VP-MIGRATION/0.7.7 --origin-lines --out source.json
python3 -m vpmigration print-panels --source source.json --view cube.flow --partition subject --granularity detail --out panels
python3 -m vpmigration check-panels --dir panels
```

`scripts/pin_076_digests.py` hält die 0.7.6-Ausgaben der OL-Fälle fest (vor dem 0.7.7-Code geschrieben); `tests/test_vp077.py` prüft Tabelle, Druck, geschlossene 0.7.6-Tabelle, X-Endpunkte, Aussagenpfad, Pins und G6 = CLI.
