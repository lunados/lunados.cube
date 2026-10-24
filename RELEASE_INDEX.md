# AIAEAO Visual Printer – VP-06 Full Release Candidate

This is a **repository-root overlay package**, not an already deployed service. The Python printer itself lives in `P2/visual-printer-release-v1/`; all VP-01–VP-05 predecessors are preserved unchanged in their sibling P2 folders.

To review **locally**, unpack with Finder and open `P2/visual-printer-release-v1/quick_preview.html`, then run:

```bash
cd P2/visual-printer-release-v1
python3 scripts/verify_vp06.py
python3 -m vpprint capabilities
```

The optional folders `.github/workflows/` and `AIAEAO_Pure_Cube_P0_v9.4/validation/v1/visual/printer/v1/` are intended **only for a later, separate reviewed GitHub publication**. They must be merged from the repository root. No existing P0/P1 asset is overwritten by this ZIP; the optional webroot contains only new static printer metadata.

**Important:** The URL in the metadata is a potential static GET reference; the SVG printer itself always runs locally. This is **not** an online `/print` API or a web application. No 3D or automatic multi-SVG generation is included.

Further documentation: `P2/visual-printer-release-v1/README.md`, `agent/AGENT_QUICKSTART.md`, `DEPLOYMENT_GUIDE.md`, `VP06_CONTRACT.md`.
