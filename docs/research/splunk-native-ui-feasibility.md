# Splunk Native UI Feasibility — Generative Chat Inside a Splunk App

**Bottom line:** YES. Ship a React SPA in `appserver/static/`, mount it from a simple SimpleXML `<dashboard script="…">` view. Streaming/SSE/fetch to external LLM endpoints is feasible because Splunk Web does not impose a `connect-src`-restrictive CSP by default; the page runs in your Splunk Web origin (no sandboxed iframe per app). Risk is non-zero on `connect-src` if the admin has hardened CSP — mitigate by proxying LLM calls through a custom REST handler (`restmap.conf` + Python). Vercel AI SDK `streamUI` requires a Node server; on Splunk side use the streaming primitive directly (SSE/`ReadableStream` + tool-call JSON → render typed React components in client) — no Splunk-side blocker found.

## 1. Custom React SPA in `appserver/static/` — delivery mechanism

Standard pattern, documented and used in the wild. Files go in `$SPLUNK_HOME/etc/apps/<APP>/appserver/static/`. View is SimpleXML at `default/data/ui/views/<name>.xml` with a `<dashboard script="index.js" stylesheet="app.css">` attribute that loads `appserver/static/index.js`. A `<html><div id="root"/></html>` panel becomes the React mount.
- Reference impl: https://github.com/robertsobolczyk/splunk-react-app — `react.xml` has `<dashboard script="index.js" …>`, build emits `dist/index_bundle.js` aliased to `index.js`.
- Splunk official: https://dev.splunk.com/enterprise/docs/developapps/createapps/buildapps/ (Splunk UI Toolkit / `@splunk/create` scaffolds this exact shape).
- Community confirmation of path: https://community.splunk.com/t5/Dashboards-Visualizations/Where-should-I-put-my-JavaScript-and-CSS-files-in-Splunk/m-p/443552

## 2. JS runtime constraints inside Splunk Web

Code runs in the Splunk Web origin (not an isolated iframe). Arbitrary npm bundles load fine — confirmed by `splunk-react-app` boilerplate and Splunk's own `@splunk/react-ui` / `@splunk/visualizations` packages (React 17/18). Default Splunk Web does not ship a restrictive CSP — `web-features.conf` (https://help.splunk.com/en/data-management/splunk-enterprise-admin-manual/10.2/configuration-file-reference/10.2.2-configuration-file-reference/web-features.conf) describes opt-in CSP only for Studio Dashboards' external content restrictions. Community thread "Content-Security-Policy HTTP Header missing on splunk web" (https://community.splunk.com/t5/Security/Content-Security-Policy-HTTP-Header-missing-on-splunk-web/m-p/753297) confirms no CSP header by default. `fetch()` to external LLM APIs and SSE/streaming responses are therefore unblocked at the platform level (subject to hardened deployments). React 18 streaming works.

## 3. Precedent — LLM chat UI inside Splunk custom view

- **Splunk AI Assistant for SPL** (official, Splunkbase): ships a full chat UI rendered inside Splunk Web — "intuitive chat experience … within a familiar Splunk interface." https://splunkbase.splunk.com/ + https://www.splunk.com/en_us/products/splunk-ai-assistant-for-spl.html
- **AI User Assistant for Splunk** (community, Splunkbase app 8747): multi-LLM (Anthropic/OpenAI/Bedrock/Ollama/…) chat UI inside a Splunk app. https://splunkbase.splunk.com/app/8747
Both demonstrate chat-in-Splunk-Web works in production.

## 4. SSE / streaming precedent

No public sample explicitly demos Vercel AI SDK `streamUI` inside Splunk, BUT: (a) Splunk's own SPL Assistant streams token-by-token in its in-app chat, proving SSE/streaming over HTTP works in the Splunk Web context; (b) no CSP `connect-src` restriction by default (§2). The generative-UI pattern (server emits typed tool-call JSON → client switches on `type` to render `<Chart>`/`<Form>`/`<Table>`) is pure client code — Splunk imposes no obstacle.

## 5. Alternative if blocked

Dashboard Studio custom visualization API is **not** a fit for chat: it's a `postMessage`-sandboxed React component meant for charts (https://help.splunk.com/en/splunk-cloud-platform/developing-views-and-apps-for-splunk-web/10.4.2604/custom-visualizations-for-dashboard-studio/best-practices). Community: "You cannot use React JS directly in Dashboard Studio" (https://community.splunk.com/t5/Dashboards-Visualizations/How-to-use-custom-react-visualization-in-Dashboard-Studio/m-p/619854). The correct fallback is the **same** SimpleXML-loads-React pattern (§1) — that IS the supported path. Splunk UI Toolkit (`@splunk/react-ui`, `@splunk/dashboard-core`) is React-based, not the legacy Bootstrap stack.

## 6. Build + package path

1. `npx @splunk/create` (Splunk UI Toolkit) — scaffolds `appserver/static/` + webpack.
2. Webpack `output.path = appserver/static/`, `output.filename = index.js`.
3. `default/data/ui/views/aegis.xml`: `<dashboard script="index.js" stylesheet="app.css"><row><panel><html><div id="root"/></html></panel></row></dashboard>`.
4. `default/app.conf` `[ui] is_visible = 1`, `default/data/ui/nav/default.xml` links the view.
5. Package: `slim package <app-dir>` → `.tgz` for Splunkbase / `splunk install app`.
6. **AppInspect**: external `fetch()` to LLM APIs will trigger Cloud Vetting warnings (`check_for_outbound_network_communications`). For Splunk Cloud, proxy LLM through a custom REST endpoint in `bin/` via `restmap.conf` — keeps secrets server-side and clears vetting. (Sources: https://dev.splunk.com/enterprise/docs/developapps/createapps and SUIT docs.)

## Sources
- https://github.com/robertsobolczyk/splunk-react-app
- https://gist.github.com/JoseMiralles/c2e9c0d2007e18fcc21776dd7f8239cc
- https://dev.splunk.com/enterprise/docs/developapps/createapps/buildapps/
- https://dev.splunk.com/enterprise/docs/developapps/createapps
- https://splunkbase.splunk.com/app/8747
- https://www.splunk.com/en_us/products/splunk-ai-assistant-for-spl.html
- https://community.splunk.com/t5/Security/Content-Security-Policy-HTTP-Header-missing-on-splunk-web/m-p/753297
- https://help.splunk.com/en/data-management/splunk-enterprise-admin-manual/10.2/configuration-file-reference/10.2.2-configuration-file-reference/web-features.conf
- https://community.splunk.com/t5/Dashboards-Visualizations/How-to-use-custom-react-visualization-in-Dashboard-Studio/m-p/619854
- https://www.npmjs.com/package/@splunk/visualizations
