# Durable handovers

Each step creates Sxx.md, or an explicitly indexed retry file, using docs/project/HANDOVER_TEMPLATE.md. The state file links to the latest actual handover. This folder initially contains no completed-step claims.

Tracked handovers must be public-safe. Keep private paths/names/media in ignored local records and share only necessary local details privately in the chat. The final chat includes the real checkpoint SHA after push; the handover resolves its own containing commit from Git history.
