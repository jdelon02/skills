---
name: gsd-fast
description: "Execute a trivial task inline — no subagents, no planning overhead"
---
Invoke this Kimi skill with `/skill:gsd-fast`.



<objective>
Execute a trivial task directly in the current context without spawning subagents
or generating PLAN.md files. For tasks too small to justify planning overhead:
typo fixes, config changes, small refactors, forgotten commits, simple additions.

This is NOT a replacement for /skill:gsd-quick — use /skill:gsd-quick for anything that
needs research, multi-step planning, or verification. /skill:gsd-fast is for tasks
you could describe in one sentence and execute in under 2 minutes.
</objective>

<execution_context>
@$HOME/.agents/gsd-core/workflows/fast.md
</execution_context>

<process>
Execute end-to-end.
</process>
