# Cube v9.4 — Agent Application Guide

## Purpose

Apply the v9.4 reference to unfamiliar domains without asking the consumer to
read old development experiments. This is a **read-only descriptive reference**.
No response from this repository grants AIAEAO runtime Authority or establishes
foreign-system historical facts.

## Minimal procedure

1. Load `/manifest.json`; bind all model statements to `reference_version=v9.4`.
2. Read `core.json` and `grammar/concepts.json` for X/Y/Z definition homes;
   use F/M solely as qualifiers. Do not infer a 5-dimensional ontology.
3. Load `time.json` if historical order, validity, scheduling or freshness is
   material; load `observer.json` if access, delivery, perception, projection or
   coverage is material. A necessary qualifier is not optional for validity.
4. Read `grammar/relations.json`, `grammar/constraints.json` and
   `notation/syntax.json` before forming a typed expression. Visual IDs are
   available in `visual/symbols.json` for **display**, not for machine identity.
5. Separate given facts, assumptions, claims, interpretations, plans,
   actual actions/results, verification and unknowns. For foreign inputs,
   preserve external identifiers and disclose semantic loss.
6. State scope, time roles, evidence origin, observer limits, method profile
   and unknown bindings when relevant. Do not invent a technical resolver,
   authorization decision or observed Event.
7. A syntactically valid AST is not proof of resolution, semantics, truth,
   current admission or successful execution. Distinguish these results.

## Missing information

Missing predicate signature or referent binding -> `unresolved`.
Unsupported inference -> `not_established`, not automatically false.
Missing current authorization for an effect -> refuse effect; P0 itself has
**no effectful functions**.

## Examples

- `examples/migration.json`: source/target document infrastructure and sync jobs.
- `examples/metaphysics.json`: hypotheses, opposition, proof and synthesis limits.

Both are **hypothetical mapping illustrations**, not real observed executions.
Their `mapped_referents` are references to concept catalog entries, not live
resolver-backed instances or conformant Canonical Events.

## Source authority

`morphology.md` is the adopted v9.4 documentary point of truth. The JSON
endpoints are curated read-only projections of it. In case of disagreement, the
original v9.4 definitions prevail; the Cube release must then be corrected as
a new immutable release, not resolved ad hoc by an AI Agent.

The public release does not depend on EXP-023, a running Rust binary, the
AIAEAO server instance, Core/Adapter schemas or production runtime conformance.
