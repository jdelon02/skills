---
name: gsd-ship
description: "Create PR, run review, and prepare for merge after verification passes"
---
Invoke this Kimi skill with `/skill:gsd-ship`.


<objective>
Bridge local completion → merged PR. After /skill:gsd-verify-work passes, ship the work: push branch, create PR with auto-generated body, optionally trigger review, and track the merge.

Closes the plan → execute → verify → ship loop.
</objective>

<execution_context>
@$HOME/.agents/gsd-core/workflows/ship.md
</execution_context>

Execute the ship workflow from @$HOME/.agents/gsd-core/workflows/ship.md end-to-end.
