# Agent-Testumgebung (offline Wheelhouse)

Ziel: Ein AI-Agent in der Linux-VM der Claude-Desktop-App kann den lokalen Cube-MCP-Server und den Research-Runner selbst ausführen — ohne Netzzugang und mit denselben Paketversionen wie die Adapter-venv auf dem Mac. Gilt für die POC- und Testphase.

## Warum offline

- Die Mac-`.venv` enthält macOS-Binaries; die Linux-VM kann sie nicht starten.
- Die VM hat nur Python 3.10. Mehrere gepinnte Pakete (u. a. `httpx2`, `starlette`, `rpds_py`, `pycparser`) verlangen ≥ 3.11.
- Die Netzwerk-Allowlist sperrt in der VM PyPI und GitHub. Der Mac lädt deshalb einmal Linux-Python und Linux-Wheels herunter; die VM installiert nur aus diesem lokalen Bestand.

## Ablauf

1. **Auf dem Mac (mit Netz), vom Repository-Root:**
   ```sh
   scripts/dev/build_wheelhouse.sh
   git add scripts/dev/requirements-agent.lock
   ```
   Pinnt per `pip freeze` exakt die Versionen der Adapter-venv, lädt passende Linux-Wheels (CPython 3.13, x86_64, manylinux ≤ glibc 2.35) nach `.wheelhouse/wheels/linux-x86_64-cp313/` und ein CPython-3.13-Laufzeitarchiv von python-build-standalone nach `.wheelhouse/python/` (gegen die veröffentlichte `SHA256SUMS` geprüft). Schreibt `requirements-agent.lock` mit SHA-256 für Laufzeit und jede Wheel. Version überschreibbar mit `PBS_TAG`/`PBS_PY`.
2. **In der Agent-VM (offline):**
   ```sh
   scripts/dev/agent_env.sh
   .agent-env/venv/bin/python -B scripts/research/comparison_runner.py --cases docs/09-Research/grammar-sampling/cases --output /tmp/mile002-run-1
   ```
   Prüft den Laufzeithash, entpackt nach `.agent-env/python/`, legt `.agent-env/venv/` an und installiert mit `--no-index --require-hashes`. Ein vorhandenes Environment wird geprüft, nicht neu gebaut.

`.wheelhouse/` und `.agent-env/` sind gitignoriert. Committet wird nur das Lock.

## Grenzen

- Patchversion kann abweichen (Mac 3.13.7, Agent z. B. 3.13.16); Paketversionen sind identisch gepinnt.
- Ändert sich die Adapter-venv, `build_wheelhouse.sh` erneut ausführen (Wheel-Ordner vorher leeren) und das neue Lock committen.
- Nur Linux x86_64. Läuft der Agent auf einer anderen Architektur, braucht es ein eigenes Ziel.
- Der Runner startet den MCP-Server mit `sys.executable`; ein Lauf mit `.agent-env` testet also die Linux-Umgebung, nicht die laufende Desktop-Verbindung. Berichte halten Python-Pfad und -Version fest.
- Kein Werkzeug im Cube-MCP führt Tests aus; die Seiteneffektfreiheit der MCP-Tools bleibt unberührt.
