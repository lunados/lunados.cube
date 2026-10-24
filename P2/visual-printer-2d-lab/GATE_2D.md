# VP-02 · Local 2D usability gate

## Automated initial checks (covered)

- 129 anchors and P0↔P1 glyph equality; stable v9.4 ordering for the five contract pairs
- Strict v0.1 plan validation: canonical anchor IDs, allowed forms and colors, status-witness declaration pointer, no unknown keys, no arbitrary relations
- XML well-formed, `title` and `desc` present, no image/script/foreignObject or external references
- UTF-8 glyph preservation, XML text safely escaped, deterministic byte-identical render
- Four fixtures and sample SVGs generated reproducibly
- Basic rasterization via CairoSVG (optional; PNGs are screenshots, not normative source)

## Human QA (not silently certified)

| Question | Criterion | Outcome |
| --- | --- | --- |
| Unicode | No missing glyph/tofu on target systems (macOS Safari, Chrome; Linux CI) | **OPEN** |
| Readability | Labels and marker IDs legible at 100% and 150% | **OPEN** |
| Pair grammar | Five v9.4 pair orders preserved; no false implication from connector line | **OPEN** |
| Relations | Operator/arrow direction and declaration scope understandable | **OPEN** |
| Thread | Ordinal display NOT mistaken for event proof or causation | **OPEN** |
| Topology | Frames do not imply authority or active connectors | **OPEN** |
| Density | Compact view on typical 13" laptop acceptable | **OPEN** |
| Grayscale | Monochrome still understandable | **OPEN** |
| Cross-agent | Claude/Grok create matching JSON plans and equivalent SVGs | **OPEN** |

## Decision gate

- `2D_GO`: all key human QA categories acceptable; minor issues recorded for VP-03.
- `2D_REVISE`: typography, template density, relationship presentation or accessibility unacceptable, but architecture sound.
- `2D_STOP`: basic type/identity or authority invariants cannot be preserved.
- **No 3D implementation or natural axis order contract before explicit 2D_GO.**
