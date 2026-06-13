"""Custom search command ``| spelunk "<question>"`` (Splunk-native entry point).

Registered via default/commands.conf as a chunked, streaming custom search
command. Lets an analyst invoke the agent directly from SPL and get the
narrative + key findings back as result rows — the same spelunk_core.pipeline
the cockpit uses, just rendered as a search command instead of generative UI.

INTENT (not yet implemented): a splunklib EventingCommand subclass that runs
the pipeline and emits rows. Stub only.
"""

# TODO(phase-5): EventingCommand subclass. Stub only.
