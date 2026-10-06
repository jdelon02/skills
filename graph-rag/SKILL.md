---
name: graph-rag
description: |
  Graph-based operations for IMS ontology (Decision, Bug, Feature, Component nodes).
  Use to create graph entities, analyze dependencies, track architectural drift, and manage self-improving patterns.
license: Proprietary
compatibility: Requires IMS backend with Neo4j graph database; read/write graph nodes and relationships.
metadata:
  user_invocable: true
  phase: 3
  operations: ["create_decision", "create_bug", "create_feature", "create_component", "create_correction", "create_reflection", "create_pattern", "create_lesson", "create_relationship", "impact_analysis", "blocking_analysis", "architectural_drift", "lookup_patterns", "corrections_ready", "promote_correction"]
  node_types: ["Decision", "Bug", "Feature", "Component", "Correction", "Reflection", "Pattern", "Lesson"]
  keywords: ["graph", "ontology", "neo4j", "decision", "bug", "feature", "component", "relationships", "impact-analysis", "drift-detection", "self-improving"]
allowed-tools: call_mcp_tool
---

# graph-rag Skill

Graph-based operations for the IMS ontology layer. This skill provides tools to create and query software development entities (Decisions, Bugs, Features, Components) and their relationships in a Neo4j knowledge graph.

---

## Identity & Scope

All graph operations are scoped by `project_id`, which identifies the current project (typically `basename($PWD)`).

The graph layer works alongside:
- **memory-core** - Stores memories in Postgres + Qdrant; automatically creates Decision/Bug graph nodes for `kind='decision'`/`'issue'`
- **context-rag** - Hybrid vector + graph context retrieval; can expand vector search results with graph relationships

This skill provides **direct graph manipulation** for advanced workflows that need explicit entity creation, relationship management, and graph analysis.

---

## Ontology Schema Overview

### Node Types

**Core Software Development Entities:**
- **Decision** - Architectural and technical decisions with rationale
- **Bug** - Issues with symptoms, root cause, fix, and lifecycle tracking
- **Feature** - Functionality to be implemented with requirements and status
- **Component** - System components (services, modules) with interfaces and dependencies

**Self-Improving Entities (Future):**
- **Correction** - User corrections of agent behavior
- **Reflection** - Agent self-evaluation after completing work
- **Pattern** - Confirmed behavioral patterns (promoted from corrections)
- **Lesson** - Improvements learned from reflections

### Relationship Types

**Core Relationships:**
- `implements` - Feature implements Decision
- `blocks` - Bug/Feature blocks Feature/Bug
- `affects` - Decision affects Component
- `depends_on` - Component/Feature depends on Component/Decision (acyclic)
- `supersedes` - Decision supersedes prior Decision (acyclic)
- `fixed_by` - Bug fixed by Decision
- `worked_on` - Session worked on Feature/Bug/Component

**Self-Improving Relationships (Future):**
- `BECOMES` - Correction becomes Pattern (after 3+ confirmations)
- `YIELDS` - Reflection yields Lesson
- `APPLIES_TO` - Pattern/Lesson applies to Component/Decision/Bug/Feature
- `IMPROVES` - Lesson improves Decision
- `PREVENTS` - Pattern prevents Bug type

---

## Node Creation Operations

### Operation: graph_create_decision

Create Decision nodes for architectural and technical decisions.

**When to use:**
- Recording architectural choices
- Documenting technical decisions with rationale
- Tracking decision evolution with supersedes relationships

**Parameters:**
- `project_id` (string, required) - Project identifier
- `text` (string, required, min 10 chars) - The decision made
- `rationale` (string, required, min 20 chars) - Why this decision was made
- `alternatives` (array of strings, optional) - Options that were considered
- `consequences` (array of strings, optional) - Expected outcomes and tradeoffs
- `importance` (float, optional, 0.0-1.0, default: 0.5) - Significance for retention tier
- `tags` (array of strings, optional) - Categorization tags

**Returns:** UUID of created Decision node

**Example:**
```python
decision_id = ims_graph_create_decision(
    project_id="my-app",
    text="Use Redis for session state storage",
    rationale="Need atomic operations, TTL support, and multi-instance capability",
    alternatives=["File-based (rejected - no concurrency)"],
    consequences=["Requires Redis deployment", "Enables horizontal scaling"],
    importance=0.9,
    tags=["architecture", "redis", "session-state"]
)
```

**Validation:**
- `text` must be at least 10 characters
- `rationale` must be at least 20 characters
- `importance` must be between 0.0 and 1.0
- `project_id` cannot be empty or whitespace only

---

### Operation: graph_create_bug

Create Bug nodes to track issues with symptoms, root cause, and resolution.

**When to use:**
- Tracking bugs with structured lifecycle
- Linking bugs to blocking relationships (what they block)
- Documenting root cause analysis and fixes
- Integrating with external issue trackers (GitHub, Jira)

**Parameters:**
- `project_id` (string, required) - Project identifier
- `symptoms` (string, required, min 10 chars) - What's broken/wrong
- `status` (string, optional, default: "open") - Bug lifecycle state
  - Allowed values: `open`, `in_progress`, `blocked`, `fixed`, `wont_fix`
- `severity` (string, optional, default: "medium") - Impact level
  - Allowed values: `low`, `medium`, `high`, `critical`
- `root_cause` (string, optional) - Why it's happening
- `fix` (string, optional) - How it was fixed
- `primary_file` (string, optional) - Main file where bug exists
- `line_hint` (int, optional) - Approximate line number
- `external_id` (string, optional) - Link to external system (e.g., "gh-owner/repo-123")
- `external_system` (string, optional) - External system type (e.g., "github", "jira")
- `tags` (array of strings, optional) - Categorization tags

**Returns:** UUID of created Bug node

**Example:**
```python
bug_id = ims_graph_create_bug(
    project_id="my-app",
    symptoms="Server crashes on invalid JWT token",
    status="open",
    severity="high",
    root_cause="Missing null check in token validation",
    primary_file="auth/middleware.py",
    line_hint=42,
    tags=["auth", "crash"]
)
```

**Validation:**
- `symptoms` must be at least 10 characters
- `status` must be one of the allowed enum values
- `severity` must be one of the allowed enum values

---

### Operation: graph_create_feature

Create Feature nodes to track functionality to be implemented.

**When to use:**
- Planning features with requirements and priority
- Tracking feature implementation status
- Linking features to decisions they implement
- Integrating with external task systems

**Parameters:**
- `project_id` (string, required) - Project identifier
- `description` (string, required, min 10 chars) - What to build
- `status` (string, optional, default: "planned") - Feature lifecycle state
  - Allowed values: `planned`, `in_progress`, `completed`, `cancelled`
- `priority` (string, optional, default: "medium") - Implementation priority
  - Allowed values: `low`, `medium`, `high`, `critical`
- `requirements` (array of strings, optional) - Functional requirements
- `file_path` (string, optional) - Primary file to modify
- `line_hint` (int, optional) - Where to start work
- `external_id` (string, optional) - Link to external task (e.g., GitHub Issue)
- `external_system` (string, optional) - External system type
- `tags` (array of strings, optional) - Categorization tags

**Returns:** UUID of created Feature node

**Example:**
```python
feature_id = ims_graph_create_feature(
    project_id="my-app",
    description="Add OAuth 2.0 authentication",
    status="planned",
    priority="high",
    requirements=["Support Google OAuth", "Support GitHub OAuth"],
    file_path="auth/oauth.py",
    tags=["auth", "oauth"]
)
```

**Validation:**
- `description` must be at least 10 characters
- `status` must be one of the allowed enum values
- `priority` must be one of the allowed enum values

---

### Operation: graph_create_component

Create Component nodes to represent system components (services, modules, packages).

**When to use:**
- Modeling system architecture
- Tracking component interfaces and responsibilities
- Establishing dependency relationships between components
- Analyzing impact of architectural decisions on components

**Parameters:**
- `project_id` (string, required) - Project identifier
- `name` (string, required) - Component identifier (alphanumeric + underscore/dash)
- `description` (string, optional) - What it does
- `interface` (string, optional) - Public API/contract
- `responsibilities` (array of strings, optional) - What it's responsible for
- `tags` (array of strings, optional) - Categorization tags

**Returns:** UUID of created Component node

**Example:**
```python
component_id = ims_graph_create_component(
    project_id="my-app",
    name="AuthService",
    description="Handles user authentication and session management",
    interface="POST /auth/login, POST /auth/logout, GET /auth/session",
    responsibilities=["JWT token generation", "Session validation"],
    tags=["service", "auth"]
)
```

**Validation:**
- `name` must contain only alphanumeric characters, underscores, and dashes
- `project_id` cannot be empty or whitespace only

---

### Operation: graph_create_relationship

Create a relationship between two nodes in the ontology graph.

**When to use:**
- Linking features to decisions they implement
- Marking bugs as blocking features
- Showing how decisions affect components
- Establishing component dependencies
- Tracking decision evolution (supersedes)

**Parameters:**
- `from_id` (string, required) - Source node UUID
- `rel_type` (string, required) - Relationship type
  - Allowed values: `implements`, `blocks`, `affects`, `depends_on`, `supersedes`, `fixed_by`, `worked_on`
- `to_id` (string, required) - Target node UUID
- `properties` (object, optional) - Optional relationship properties

**Returns:** Boolean (true if successful)

**Relationship Semantics:**
- `implements` - Feature implements Decision
- `blocks` - Bug/Feature blocks Feature/Bug
- `affects` - Decision affects Component
- `depends_on` - Component/Feature depends on Component/Decision (acyclic)
- `supersedes` - Decision supersedes Decision (acyclic)
- `fixed_by` - Bug fixed by Decision
- `worked_on` - Session worked on Feature/Bug/Component

**Examples:**
```python
# Link feature to decision
ims_graph_create_relationship(
    from_id=feature_id,
    rel_type="implements",
    to_id=decision_id
)

# Link bug to feature (blocking)
ims_graph_create_relationship(
    from_id=bug_id,
    rel_type="blocks",
    to_id=feature_id
)

# Show decision affects component
ims_graph_create_relationship(
    from_id=decision_id,
    rel_type="affects",
    to_id=component_id
)
```

**Validation:**
- `rel_type` must be one of the allowed relationship types
- Backend enforces type compatibility and acyclicity for certain relationships

---

## Analysis Query Operations

### Operation: graph_impact_analysis

Analyze the impact of changing a Decision or Component.

**Use cases:**
- Before modifying an architectural decision: what components are affected?
- Before changing a component: what depends on it downstream?
- Understanding blast radius of changes

**Parameters:**
- `entity_id` (string, required) - Node UUID to analyze
- `entity_type` (string, required) - Type of entity
  - Allowed values: `Decision`, `Component`
- `project_id` (string, optional) - Optional project filter

**Returns:** Dict with affected entities and relationship details

**Example:**
```python
# What components are affected by this decision?
impact = ims_graph_impact_analysis(
    entity_id=decision_id,
    entity_type="Decision"
)
# Returns: {"results": [{"component": "AuthService", "description": "..."}]}

# What depends on this component?
impact = ims_graph_impact_analysis(
    entity_id=component_id,
    entity_type="Component"
)
# Returns: {"results": [{"dependent": "SessionStore", "relationship": "depends_on"}]}
```

**Validation:**
- `entity_type` must be either "Decision" or "Component"

---

### Operation: graph_blocking_analysis

Find what bugs are blocking a feature.

**Use cases:**
- Feature planning - identify blockers before starting work
- Release planning - determine if feature is ready
- Prioritization - understand critical path to feature completion

**Parameters:**
- `feature_id` (string, required) - Feature node UUID

**Returns:** Dict with blocking bugs, sorted by severity

**Example:**
```python
blockers = ims_graph_blocking_analysis(feature_id)
# Returns: {"results": [
#   {"symptoms": "Server crashes on invalid JWT", "severity": "high", "status": "open"},
#   {"symptoms": "Session timeout too short", "severity": "medium", "status": "in_progress"}
# ]}
```

**Workflow:**
1. Before starting feature implementation, check for blocking bugs
2. Review bug severities and statuses
3. Fix critical/high severity bugs first
4. Proceed with feature when blockers are resolved

---

### Operation: graph_architectural_drift

Detect components following superseded decisions.

**Use cases:**
- Technical debt detection - find outdated implementations
- Architecture consistency - ensure components follow current decisions
- Refactoring prioritization - identify which components need updates

**Parameters:**
- `project_id` (string, required) - Project to analyze

**Returns:** Dict with drifted components and decision evolution

**Example:**
```python
drift = ims_graph_architectural_drift("my-app")
# Returns: {"results": [
#   {
#     "component": "SessionStore",
#     "currently_follows": "File-based sessions (Decision A)",
#     "should_follow": "Redis sessions (Decision B, supersedes A)"
#   }
# ]}
```

**Workflow:**
1. Run periodically to detect architectural drift
2. Review components following superseded decisions
3. Create refactoring tasks to align with current architecture
4. Update components to follow latest decisions

---

### Operation: graph_lookup_patterns

Find patterns applicable to a component.

**Use cases:**
- Before implementing features for a component, check for applicable patterns
- Ensuring consistency with established best practices
- Applying organizational learning to current work

**Parameters:**
- `component_name` (string, required) - Component to find patterns for
- `domain` (string, optional) - Optional domain filter (e.g., "python", "auth")

**Returns:** Dict with applicable patterns and confidence scores

**Example:**
```python
patterns = ims_graph_lookup_patterns("AuthService", domain="auth")
# Returns: {"results": [
#   {"description": "Always use rate limiting for auth endpoints", "confidence": 1.0, "usage_count": 15},
#   {"description": "Log all authentication failures", "confidence": 0.9, "usage_count": 8}
# ]}
```

**Workflow:**
1. Before working on a component, lookup applicable patterns
2. Review patterns with high confidence (>0.8)
3. Apply patterns to current work
4. Patterns prevent repeating past mistakes

---

## Self-Improving Operations

### Operation: graph_corrections_ready

Find corrections ready to be promoted to patterns.

**Use cases:**
- Periodic review of user corrections
- Identifying emergent patterns in feedback
- Pattern promotion workflow

**Parameters:**
- `project_id` (string, optional) - Optional project filter

**Returns:** Dict with corrections ready for promotion (usage_count >= 3)

**Example:**
```python
ready = ims_graph_corrections_ready("my-app")
# Returns: {"results": [
#   {"text": "Use TypeScript strict mode", "usage_count": 5, "scope": "global"},
#   {"text": "Add error boundaries to React components", "usage_count": 3, "scope": "project"}
# ]}
```

**Promotion Workflow:**
1. Call `graph_corrections_ready` periodically (weekly/monthly)
2. Review suggestions with user - confirm which should become patterns
3. Use `graph_promote_correction` to create Pattern nodes
4. Patterns become part of project knowledge and are surfaced via `graph_lookup_patterns`

---

### Operation: graph_promote_correction

Promote a correction to a pattern.

**Use cases:**
- Converting confirmed user corrections into organizational patterns
- Formalizing emergent best practices
- Building self-improving knowledge base

**Parameters:**
- `correction_id` (string, required) - Correction node UUID to promote

**Returns:** Dict with newly created Pattern node

**Example:**
```python
pattern = ims_graph_promote_correction(correction_id)
# Returns: {"pattern_id": "uuid-...", "description": "Use TypeScript strict mode", "scope": "global"}
```

**Workflow:**
1. User corrects agent behavior multiple times
2. Each correction creates a Correction node
3. When usage_count reaches 3+, correction appears in `graph_corrections_ready`
4. Agent or user calls `graph_promote_correction` to formalize the pattern
5. Pattern node is created with BECOMES relationship to Correction
6. Pattern is now retrievable via `graph_lookup_patterns` for future work

---

## Usage Patterns and Workflows

### Workflow 1: Recording an Architectural Decision

**Scenario:** You've decided to use Redis for session state storage and need to record this decision with its context.

**Steps:**
```python
# 1. Create the decision node
decision_id = ims_graph_create_decision(
    project_id="my-app",
    text="Use Redis for session state storage",
    rationale="Need atomic operations, TTL support, and multi-instance capability for horizontal scaling",
    alternatives=[
        "File-based storage (rejected - no concurrency support)",
        "Postgres (rejected - overkill for ephemeral session data)"
    ],
    consequences=[
        "Requires Redis deployment and monitoring",
        "Enables horizontal scaling of app servers",
        "Built-in TTL for automatic session cleanup"
    ],
    importance=0.9,
    tags=["architecture", "redis", "session-state", "scalability"]
)

# 2. Link the decision to affected components
component_id = ims_graph_create_component(
    project_id="my-app",
    name="SessionStore",
    description="Session state management layer",
    interface="get_session(session_id), set_session(session_id, data), delete_session(session_id)",
    tags=["session", "storage"]
)

ims_graph_create_relationship(
    from_id=decision_id,
    rel_type="affects",
    to_id=component_id
)

# 3. If there's a prior decision being replaced, link it
if prior_decision_id:
    ims_graph_create_relationship(
        from_id=decision_id,
        rel_type="supersedes",
        to_id=prior_decision_id
    )
```

---

### Workflow 2: Impact Analysis Before Refactoring

**Scenario:** You want to change an architectural decision and need to understand what components will be affected.

**Steps:**
```python
# 1. Find the decision to change
# (Assume you have decision_id from previous context or search)

# 2. Run impact analysis
impact = ims_graph_impact_analysis(
    entity_id=decision_id,
    entity_type="Decision"
)

# 3. Review affected components
for result in impact["results"]:
    print(f"Component: {result['component']}")
    print(f"Description: {result['description']}")
    print(f"Relationship: {result['relationship']}")

# 4. Check for architectural drift
drift = ims_graph_architectural_drift("my-app")

# 5. Create refactoring tasks for affected components
for affected in impact["results"]:
    feature_id = ims_graph_create_feature(
        project_id="my-app",
        description=f"Update {affected['component']} to follow new decision",
        priority="high",
        tags=["refactoring", "technical-debt"]
    )
    
    # Link feature to the new decision
    ims_graph_create_relationship(
        from_id=feature_id,
        rel_type="implements",
        to_id=decision_id
    )
```

---

### Workflow 3: Feature Planning with Blocking Analysis

**Scenario:** You're planning a new OAuth feature and need to identify blockers before starting work.

**Steps:**
```python
# 1. Create the feature node
feature_id = ims_graph_create_feature(
    project_id="my-app",
    description="Add OAuth 2.0 authentication with Google and GitHub providers",
    status="planned",
    priority="high",
    requirements=[
        "Support Google OAuth",
        "Support GitHub OAuth",
        "Store OAuth tokens securely",
        "Refresh token rotation"
    ],
    file_path="auth/oauth.py",
    tags=["auth", "oauth", "security"]
)

# 2. Link to architectural decisions
decision_id = ims_graph_create_decision(
    project_id="my-app",
    text="Use OAuth 2.0 for third-party authentication",
    rationale="Industry standard, delegated authentication, reduces password management burden",
    tags=["auth", "oauth", "security"]
)

ims_graph_create_relationship(
    from_id=feature_id,
    rel_type="implements",
    to_id=decision_id
)

# 3. Check for blocking bugs
blockers = ims_graph_blocking_analysis(feature_id)

if blockers["results"]:
    print("⚠️ Feature is blocked by the following bugs:")
    for bug in blockers["results"]:
        print(f"  - [{bug['severity']}] {bug['symptoms']} (status: {bug['status']})")
else:
    print("✅ No blocking bugs - ready to start implementation")

# 4. Check for applicable patterns
patterns = ims_graph_lookup_patterns("AuthService", domain="auth")
print("\n📋 Applicable patterns:")
for pattern in patterns["results"]:
    print(f"  - {pattern['description']} (confidence: {pattern['confidence']})")
```

---

### Workflow 4: Bug Tracking and Resolution

**Scenario:** You've discovered a bug, need to track it, and eventually link it to the fix.

**Steps:**
```python
# 1. Create bug node
bug_id = ims_graph_create_bug(
    project_id="my-app",
    symptoms="Server returns 500 error when JWT token is expired",
    status="open",
    severity="high",
    primary_file="auth/middleware.py",
    line_hint=42,
    tags=["auth", "jwt", "error-handling"]
)

# 2. If bug blocks a feature, create blocking relationship
if feature_id:
    ims_graph_create_relationship(
        from_id=bug_id,
        rel_type="blocks",
        to_id=feature_id
    )

# 3. Investigate and update root cause
# (After debugging session)
# Note: To update properties, you'd need to call backend API directly
# or use a future graph_update_node operation

# 4. Create decision for the fix
fix_decision_id = ims_graph_create_decision(
    project_id="my-app",
    text="Add null check and graceful error handling for expired JWT tokens",
    rationale="Prevent server crashes, return proper 401 status instead of 500",
    consequences=["Better user experience", "Easier debugging"],
    importance=0.7,
    tags=["auth", "jwt", "error-handling"]
)

# 5. Link bug to fix decision
ims_graph_create_relationship(
    from_id=bug_id,
    rel_type="fixed_by",
    to_id=fix_decision_id
)

# 6. Update bug status to fixed (conceptually - would need update operation)
```

---

## Integration with Other IMS Skills

### With memory-core

**Automatic Graph Node Creation:**
- When you call `memory_core.store_memory(kind='decision', ...)`, the backend automatically creates a Decision node in the graph
- When you call `memory_core.store_memory(kind='issue', ...)`, the backend automatically creates a Bug node in the graph
- Other memory kinds (`note`, `fact`) only create memories, not graph nodes

**When to use memory-core vs graph-rag:**
- Use **memory-core** for simple storage of decisions/issues without explicit relationships
- Use **graph-rag** when you need to:
  - Create relationships between entities
  - Create Features, Components, or other specialized node types
  - Run graph analysis queries (impact, blocking, drift)
  - Manage self-improving patterns

**Example:**
```python
# Simple decision storage (memory-core - auto-creates Decision node)
memory_core.store_memory(
    project_id="my-app",
    text="Use Redis for session state",
    kind="decision",
    tags=["redis", "session"]
)

# Advanced decision with relationships (graph-rag - explicit control)
decision_id = graph_create_decision(
    project_id="my-app",
    text="Use Redis for session state",
    rationale="Need atomic ops and TTL",
    importance=0.9,
    tags=["redis", "session"]
)
graph_create_relationship(decision_id, "affects", component_id)
```

---

### With context-rag

**Hybrid Vector + Graph Retrieval:**
- `context_rag.context_search(expand_graph=True)` automatically enriches vector search results with graph relationships
- When graph expansion is enabled, vector hits for code/docs/memories are supplemented with related graph entities:
  - Related Decisions that affect returned Components
  - Bugs that block returned Features
  - Components that depend on returned Components
  - Superseded decisions (to avoid outdated info)

**When to use context-rag vs graph-rag:**
- Use **context-rag** for discovery and contextual retrieval (semantic search + optional graph expansion)
- Use **graph-rag** for explicit graph queries and analysis (impact, blocking, drift detection)

**Example:**
```python
# Semantic search with automatic graph expansion (context-rag)
results = context_rag.context_search(
    project_id="my-app",
    query="authentication implementation",
    sources=["code", "memories"],
    expand_graph=True,
    graph_depth=2
)
# Returns: vector hits + related graph entities automatically

# Explicit graph analysis (graph-rag)
impact = graph_impact_analysis(decision_id, "Decision")
blockers = graph_blocking_analysis(feature_id)
# Returns: specific graph traversal results
```

---

### With session-memory

**Work Tracking:**
- Session nodes can have `worked_on` relationships to Features, Bugs, and Components
- This creates a history of which sessions touched which entities
- Useful for:
  - Understanding who worked on what
  - Tracking feature implementation progress
  - Auditing bug fix efforts

**Example:**
```python
# After working on a feature in a session
session_state = session_memory.current_state()
session_id = session_state["session_id"]

# Link session to the feature you worked on
graph_create_relationship(
    from_id=session_id,
    rel_type="worked_on",
    to_id=feature_id
)
```

---

## Recommended Usage Pattern

**Before Starting Work:**
1. Use `context-rag` to find relevant prior work (semantic search + graph expansion)
2. Use `graph_lookup_patterns` to find applicable patterns for the component
3. Use `graph_blocking_analysis` if working on a feature (identify blockers)

**During Work:**
1. Create graph nodes (`graph_create_decision`, `graph_create_bug`, `graph_create_feature`, `graph_create_component`) to structure your work
2. Create relationships to link entities (decisions → components, bugs → features, features → decisions)

**After Completing Work:**
1. Use `graph_impact_analysis` to understand effects of changes
2. Use `graph_architectural_drift` to detect any inconsistencies
3. Use `graph_corrections_ready` and `graph_promote_correction` to formalize learned patterns

**Periodic Maintenance:**
1. Run `graph_architectural_drift` to identify technical debt
2. Run `graph_corrections_ready` to promote emergent patterns
3. Review blocking bugs via `graph_blocking_analysis` for release planning

---

## Constraints and Best Practices

### Required Field Lengths
- Decision `text` must be at least 10 characters
- Decision `rationale` must be at least 20 characters
- Bug `symptoms` must be at least 10 characters
- Feature `description` must be at least 10 characters

### Enum Validation
- Bug `status`: `open`, `in_progress`, `blocked`, `fixed`, `wont_fix`
- Bug `severity`: `low`, `medium`, `high`, `critical`
- Feature `status`: `planned`, `in_progress`, `completed`, `cancelled`
- Feature `priority`: `low`, `medium`, `high`, `critical`

### Acyclic Relationships
The following relationships must not create cycles (enforced by backend):
- `depends_on` - Component/Feature dependencies
- `supersedes` - Decision evolution
- `blocks` - Bug blocking chains

### Component Name Format
- Component `name` must contain only alphanumeric characters, underscores, and dashes
- Example: `AuthService`, `session_store`, `api-gateway`

### Importance Scores
- Decision `importance` must be between 0.0 and 1.0
- Higher importance (>0.7) indicates critical architectural decisions
- Used for retention tiering and prioritization

---

## Future Enhancements

**Self-Improving Node Types (Planned):**
The following node types are reserved for future self-improving capabilities:
- **Correction** - User corrections of agent behavior
- **Reflection** - Agent self-evaluation after completing work
- **Pattern** - Confirmed behavioral patterns (promoted from corrections)
- **Lesson** - Improvements learned from reflections

These node types are not yet available but the foundation exists with `graph_corrections_ready` and `graph_promote_correction` operations.

**Additional Planned Features:**
- Graph node update operations (currently only creation is supported)
- Graph node deletion with cascade handling
- Temporal versioning of decisions and components
- Cross-project pattern sharing
- Automated drift detection alerts

---

## Capability Endpoint

The backend exposes `GET /capabilities/graph-rag` which returns structured documentation about:
- Available operations (11 graph tools)
- Node type schemas and validation rules
- Relationship type semantics
- Usage best practices and examples

This endpoint is used by hooks to inject usage documentation into agent context at appropriate times.
