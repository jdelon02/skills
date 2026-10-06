# Multica default agent prompts

One self-contained prompt per Hermes profile. Paste the entire corresponding Markdown file into that agent's default prompt field in Multica. These are role prompts, not task descriptions or importable skill archives; supply the actual assignment separately.

Created from the profiles in `~/.hermes/profiles/` and the agreed team responsibilities. Existing Hermes profiles and Multica configuration were not changed. These files do not automatically load or assign skills.

The CEO prompt is a proposed strategy/prioritization role because the existing CEO profile contains a generic Hermes persona. Chief-of-staff owns execution coordination, project-planner owns decomposition, and specialist roles retain independent review and integration boundaries.

| Profile | Prompt |
| --- | --- |
| `ceo` | [ceo.md](ceo.md) |
| `chief-of-staff` | [chief-of-staff.md](chief-of-staff.md) |
| `project-planner` | [project-planner.md](project-planner.md) |
| `software-engineer` | [software-engineer.md](software-engineer.md) |
| `architecture-reviewer` | [architecture-reviewer.md](architecture-reviewer.md) |
| `review-verifier` | [review-verifier.md](review-verifier.md) |
| `improvement-strategist` | [improvement-strategist.md](improvement-strategist.md) |
| `git-workflow-manager` | [git-workflow-manager.md](git-workflow-manager.md) |

Prompts are portable: local Hermes profile instructions are consulted when accessible, and external tools or backends are used only when configured. Repository instructions retain their prescribed graph/tool precedence. Default prompts do not grant permissions or imply that agents and integrations are connected.

Validation: eight unique prompt files, matching the eight active profile folders; balanced section tags; no unfinished placeholders. Text was reviewed against role responsibilities and handoff boundaries. No live agent behavior evaluation or Multica installation was performed.
