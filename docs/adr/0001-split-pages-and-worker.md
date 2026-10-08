# Split static Pages frontend from an independent API Worker

Status: accepted

We're moving `base64` and `xml` off the Flask app and onto Cloudflare. Cloudflare Pages Functions would let us deploy frontend and API together as one project with one `wrangler`/git-integration pipeline — the simplest path. We chose instead to run two independent Cloudflare services: a Pages project (`toolbox`) serving plain static HTML/CSS/JS, and a separate Worker (`toolbox`) serving only the `/tools/*/api/*` JSON routes, connected over `fetch` with a CORS allowlist.

We picked this over Pages Functions because the goal is genuine frontend/backend decoupling: each side gets its own deploy, its own versioning, and the backend can be replaced or reused by another frontend later without touching the other. The cost is real — CORS configuration, two deploy pipelines instead of one, and no shared build step — but that cost is accepted deliberately in exchange for the decoupling.

## Considered Options

- **Pages Functions (rejected)**: frontend and API in one Pages project, one deploy. Simplest, but frontend and backend are permanently bound to the same deploy unit.
- **Pages + independent Worker (chosen)**: two services, decoupled, CORS required.

## Consequences

As of this deployment (2026-10), Cloudflare has unified Pages into Workers with Static Assets: `wrangler pages deploy` just delegates to `wrangler deploy` under the hood, and a "Pages project" is really a Worker with an `assets` binding. This doesn't change the decision above — we still have two independent, separately-deployed services — but it does mean the frontend is named `toolbox-pages` (a Worker), not a classic Pages project, because Workers and former-Pages projects now share one name namespace per account and `toolbox` was already taken by the API worker.
