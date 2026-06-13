/**
 * Spelunk cockpit — generative-UI chat shell.
 *
 * Mounts into the SimpleXML view's #spelunk-cockpit div. Sends the analyst's
 * question to bin/chat_handler.py (same-origin /splunkd/__raw/services/spelunk/chat,
 * Splunk session inherited), then renders each StepEvent by switching on
 * `event.type` -> a component from ./components (the generative-UI registry).
 *
 * Transport: polling first (POST /chat/start -> GET /chat/step). Streaming is a
 * later upgrade with the SAME registry.
 *
 * INTENT (phase-4): chat shell + transport client + registry. Stub only.
 */

import * as React from "react";
import { createRoot } from "react-dom/client";

const MOUNT_ID = "spelunk-cockpit";

function Cockpit(): JSX.Element {
    // TODO(phase-4): chat state, transport client, event registry rendering.
    return <div>Spelunk cockpit — scaffold</div>;
}

const el = document.getElementById(MOUNT_ID);
if (el) createRoot(el).render(<Cockpit />);
