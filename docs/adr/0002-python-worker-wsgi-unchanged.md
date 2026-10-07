# Run the existing Flask app on the Worker unchanged, via the WSGI adapter

Status: accepted

Cloudflare Workers historically meant rewriting backend logic in JavaScript/TypeScript, since the runtime only exposed a `fetch`-event JS entrypoint. Cloudflare Python Workers reached GA in September 2026 and added an official `workers.wsgi` adapter that can run a WSGI app (Flask, Django, etc.) directly. We chose to keep `app.py`, `tools/base64_tool.py`, and `tools/xml_tool.py` as-is — including the `zlib.decompress(data, -15)` raw-deflate inflate used for SAML redirect-binding — and add a thin `worker_entry.py` shim (a `WorkerEntrypoint` subclass that calls `wsgi.fetch(app, request, self.env)`, per the official `create-cloudflare --framework=flask` template) rather than reimplementing the encode/decode/parse logic in JavaScript.

The alternative — rewriting the business logic in JS/TS — was the more battle-tested path (DecompressionStream, DOMParser, etc. are all stable Workers APIs), while the WSGI route depends on a GA feature that is only weeks old at the time of this decision, with the raw-deflate path specifically unverified under Pyodide. We accepted that risk to avoid a full rewrite and preserve local dev parity (`./venv/bin/python app.py` keeps working untouched). The `render_template` HTML routes were stripped from the Flask app (moved to the static Pages frontend) since the Worker now only serves JSON; this is a deliberate, scoped exception to "unchanged."

## Considered Options

- **Rewrite logic in JS/TS (rejected)**: more proven Workers path, but throws away working, tested Python code for no functional gain.
- **Python Worker via `workers.wsgi` (chosen)**: zero rewrite of business logic, but relies on a GA feature that's weeks old, and the `zlib` raw-deflate path is unverified in this runtime — must be smoke-tested after first deploy.

## Consequences

- Verified 2026-10-07 via `pywrangler dev`: `zlib.decompress(data, -15)` correctly inflates a base64+raw-deflate SAML redirect-binding payload under the Workers Python runtime. The risk flagged above is resolved.
