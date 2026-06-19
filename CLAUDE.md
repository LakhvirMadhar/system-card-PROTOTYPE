# Application System Card — Claude Code Guide

## What This Project Is

A small agent system (Google ADK) treated as one big AI artifact, not just the LLM inside it. Everything that shapes its behavior — tool names/docstrings/schemas, the system prompt, the model + generation params, and whatever else we identify along the way — is captured as a versioned **system card**, the way an ML model card documents a model. The card is versioned via trunk-based CI (every merge to `main` that changes card-relevant surface gets a new card version) and tagged onto every OpenTelemetry trace, so you can prove, from real data in Arize Phoenix, whether a change to the system actually changed its behavior.

The problem this solves: OTel traces *that* a tool was called or what the model returned, but not what the tool's docstring said, what the system prompt was, or which model/params were active at that moment — all of which shape the LLM's actual input. The system card makes that surface explicit, versioned, and traceable.

The chain: the system's behavior-defining surface changes → trunk-based CI versions the card and shows the diff → the deployed system carries that card version on every trace → Phoenix lets you prove whether the change helped or hurt.

See `docs/PROJECT_BRIEF.md` for the full design, build order, and open questions.

**This is not a FastAPI app** — there is no HTTP layer here, so there is no `routers/` layer. `models/` is currently a placeholder: it's reserved for system card domain entities (card versions, card diffs, etc.) once that work needs a typed domain layer — do not invent unrelated domain entities for it in the meantime.

## Architecture Principles

These are non-negotiable. Vibe coding gets ugly fast — we've been burned before.

See `docs/CLEAN_CODE_STANDARDS.md` for the full coding standards. The principles below govern architecture specifically.

### Separation of concerns
A change in one file must not silently break another. Every module has one job. If you can't describe what a file does in one sentence, it's doing too much.

### Dependency direction
Inner layers never import from outer layers. `core` knows nothing about the rest of the project. `tools` know nothing about telemetry. `services` know nothing about how the agent is wired together.

```
core/          → (nothing in this project)
models/        → core/                                  (placeholder — reserved for system card domain entities)
schemas/       → core/, models/
tools/         → core/, schemas/
registry/      → core/, schemas/                         (registers tools by dotted path; never statically imports tools/)
observability/ → core/
services/      → core/, models/, schemas/, tools/, registry/
adapters/      → core/, models/
dependencies/  → everything                              (composition root — wires services, adapters, observability together)
scripts/       → everything                              (CLI entrypoints, e.g. compute_system_card_hash.py)
```

`import-linter` enforces all of the above except `dependencies/` and `scripts/`, which are intentionally unconstrained composition/entrypoint layers. It runs on every `poe check`.

### Interfaces over concrete implementations
Where storage or external systems are involved (e.g. the OTel exporter target), define the interface first and inject the concrete implementation. The application layer only ever talks to the interface. Tests use in-memory/fake implementations — no mocking of things that aren't the subject of the test.

### Explicit over implicit
No magic. No global state. Dependencies are injected, not imported from module-level singletons. Settings come from config, not hardcoded values.

### Small, named things
Short functions with intention-revealing names. If a function needs a comment to explain what it does, rename it. If it needs a comment to explain why — write the comment. Fowler's Refactoring is the reference.

### Tests must be honest
Unit tests test domain and application logic with in-memory adapters. Integration tests test infrastructure adapters against real systems (or a real running ADK agent). Never mock something just to make a test pass — that test proves nothing.

## File Structure

```
src/system_card/
  __init__.py
  __main__.py           # entry point: python -m system_card
  core/                  # framework-agnostic shared utilities — importable by all layers
    config.py            # Pydantic Settings, reads from .env
  models/                # placeholder — reserved for system card domain entities
  schemas/               # Pydantic schemas — tool_manifest.py, system card shape, agent I/O contracts
  tools/                 # the toy tools: calculator, dad_joke, shakespearify, coin_flip, word_count
  registry/              # ToolEntry (lazy-loading handle) + ToolRegistry (thread-safe, register/get/list_tools)
  services/              # system_card_service (hash), system_card_diff_service, agent_service
  observability/         # custom OTel span processor — adds agent.* attributes pre-export
  adapters/              # concrete implementations of any storage/external-system interfaces
  dependencies/          # composition root — get_tracer(), get_agent(), wiring
  scripts/               # CLI entrypoints, e.g. compute_system_card_hash.py (used by CI)

tests/
  unit/                  # services/ + tools/ + registry/ only, no infrastructure
  integration/           # real agent runs, real telemetry export

docs/
```

## Key Concepts

**System card manifest** — a diffable JSON structure capturing the application's behavior-defining surface: every tool's name/description/schema today, with the system prompt and model/generation config to follow. The card's hash is derived from this file.

**Custom attribute namespace `agent.*`** — defined once as constants (e.g. `core/attributes.py`), most importantly `agent.system_card_hash`. Standard `gen_ai.*` attributes come from ADK automatically — don't reinvent these.

**Trunk-based card versioning** (`.github/workflows/system-card-diff.yml`) — on every PR (preview) and every push to `main` (the trunk), computes the card hash and compares it to the previously recorded version; if changed, mints the next card version and posts/records a human-readable diff (added/changed/removed tools, prompt changes, etc.).

## Tech Stack

- **Python 3.12+**
- **Poetry** — dependency management
- **Google ADK** — agent framework (`LlmAgent`, tool registration)
- **OpenTelemetry** — tracing, `gen_ai.*` semantic conventions via ADK's native instrumentation
- **Arize Phoenix** — trace backend/frontend; OTel-native, no custom UI
- **Ruff** — linting and formatting
- **Mypy** — strict type checking (`mypy src`)
- **Poethepoet** — task runner
- **Pytest + pytest-cov** — testing and coverage
- **pydeps** — visualise module dependency graph (`poe deps`)
- **import-linter** — enforce architectural layer boundaries (`poe arch`)
- **Pydantic Settings** — config and environment management
- **structlog** — structured logging
- **Docker Compose** — agent + Phoenix services, single `docker compose up` demo
- **PostgreSQL** — if persistence beyond Phoenix's own storage is needed (no SQLite)
- **LLM provider** — not the Anthropic SDK; keep it behind an interface per ADK's model abstraction

## Poe Tasks

```
poe lint       # ruff check src tests
poe format     # ruff format src tests
poe typecheck  # mypy src
poe test       # pytest tests
poe deps       # pydeps — visualise module dependencies
poe arch       # lint-imports — enforce layer boundaries
poe check      # lint + typecheck + arch + test (full suite)
```

## Coding Conventions

Run `poe check` before committing — lint, typecheck, import boundaries, and tests.

**Docstrings:** Google style, required on all public modules, classes, and functions. Test files are exempt.

**Pathlib over os.path:** Always use `Path`. Never `os.path`, raw `open()`, or string-based filesystem calls.

**No naive datetimes:** Always pass `tz=` or use `datetime.now(UTC)`. Never `datetime.now()` without a timezone.

**No print():** Use `structlog` for all output.

**Async blocking calls:** Never call `open()`, `time.sleep()`, or `requests` inside an `async` function. Use `asyncio.to_thread()` or async-native alternatives.

**Type aliases:** Use `type NodeId = str`, not `TypeAlias`. Python 3.12+ syntax only.

**Self for self-referential returns:** Use `Self` from `typing`, not a custom `TypeVar`.

Active rule sets: `E`, `F`, `I`, `N`, `UP`, `TID`, `B`, `A`, `T20`, `T10`, `S`, `SIM`, `G`, `DTZ`, `RET`, `PTH`, `D`, `PYI`, `ASYNC`. See `pyproject.toml` `[tool.ruff.lint]` for the full rule set and ignore list.

## Build Order (do not skip ahead — see docs/PROJECT_BRIEF.md for full detail)

1. Toy tools (calculator, dad_joke, shakespearify, etc.)
2. Basic ADK agent wrapping the tools, no telemetry/hashing yet
3. System card service — manifest + hash, tested standalone; tools first, prompt/model fields next
4. Trunk-based CI versioning workflow
5. Inspect ADK's native OTel output before adding anything custom — OTel is being learned hands-on here, not assumed
6. Custom span processor — `agent.*` attributes, especially `agent.system_card_hash`
7. Wire exporter to Phoenix
8. Dockerize (agent + Phoenix)
9. Demo the thesis end to end

## What Not To Do

- Do not build a "real" complex tool (PDF parsing, etc.) — tools must stay trivial; the system-card/CI/observability machinery is the point
- Do not build a custom frontend — Phoenix replaces this; no `adk web`
- Do not use SQLite — PostgreSQL if persistence beyond Phoenix is needed
- Do not invent domain entities for `models/` unrelated to the system card until that work starts
- Do not write infrastructure code in `core/`
- Do not hardcode storage/exporter targets — always go through config or an interface
- Do not write functions longer than ~20 lines without a strong reason
- Do not add error handling for things that cannot happen
- Do not mock things that are not the subject of the test
- Do not add features beyond what the current task requires
- Do not flatten the architecture to move faster — the slowdown comes later, not now
- Do not use the Anthropic SDK
