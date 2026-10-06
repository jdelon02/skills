---
name: gsd-resume-work
description: "Resume work from previous session with full context restoration"
---
Invoke this Kimi skill with `/skill:gsd-resume-work`.



<objective>
Restore complete project context and resume work seamlessly from previous session.

Routes to the resume-project workflow which handles:

- STATE.md loading (or reconstruction if missing)
- Checkpoint detection (.continue-here files)
- Incomplete work detection (PLAN without SUMMARY)
- Status presentation
- Context-aware next action routing
  </objective>

<execution_context>
@$HOME/.agents/gsd-core/workflows/resume-project.md
</execution_context>

<process>
Execute end-to-end.
</process>
