AIAEAO PURE CUBE — P0 STATIC REFERENCE PACKAGE
Reference: Morphology v9.4 (adopted documentary text, 2026-10-23)
Target public domain: https://cube.lunados.net

WHAT TO DEPLOY
  Upload the contents of this directory as the static website root.
  Entry point for agents: GET /manifest.json
  Reference views: /v9.4/core.json /v9.4/time.json /v9.4/observer.json
  Extended references: grammar/, notation/, visual/, agent-guide.md
  Examples: migration.json, metaphysics.json

SCOPE
  P0 is read-only, static and self-contained for its declared descriptive
  reference profile. No backend, token, live API functions, registry service,
  connection or dependency on the separate AIAEAO server is present.
  AIAEAO Morphology v9.4 remains the single adopted documentary point of truth.
  JSON and EBNF resources are version-scoped access projections, not competing
  authoritative models or evidence of production contract conformance.
  Syntax and structural interchange are informed by ACG concept v0.2; a full
  native parser, actual referent resolver and executable REL/TIME/FUNC contracts
  are not established by this static package. No agent should improvise them.

HOSTING
  Cloudflare Pages: place _headers at deployment root; it sets
  X-Robots-Tag: noindex, CORS for read-only JSON, and nosniff.
  GitHub Pages: can serve files but does NOT natively apply _headers.
  To set the HTTP header, put the domain behind a configurable reverse proxy
  / CDN and explicitly test deployed response headers.
  robots.txt allows access: disallowing crawling would prevent compliant
  crawlers from reading the noindex header. noindex is not authentication.
  .nojekyll supports GitHub Pages static serving of underscore paths.

VERIFY LOCALLY
  python3 scripts/test_release.py
  All checked URLs in the manifest are static GET resources.

PUBLICATION CHECKLIST
  [ ] Choose/publish appropriate license for text, JSON and any code; this
      package does not assert permissions beyond user ownership.
  [ ] Bind cube.lunados.net DNS and static hosting, HTTPS only.
  [ ] Verify response headers on every /v9.4/ resource and root manifest.
  [ ] Verify Content-Type application/json for JSON URLs.
  [ ] Freeze deployed /v9.4/ assets; use another version path for changes.
  [ ] Check source-v9.4 consistency / reviewer signoff on derived JSON views.

NO INDEX HEADER
  X-Robots-Tag: noindex
  Do not confuse it with a made-up X-Robots header.
