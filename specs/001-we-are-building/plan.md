
# Implementation Plan: Gemini 2.5 Flash Image Generation CLI

**Branch**: `001-we-are-building` | **Date**: 2025-09-30 | **Spec**: /home/d/workspace/projects/anyimg/specs/001-we-are-building/spec.md
**Input**: Feature specification from `/specs/001-we-are-building/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
A Python CLI tool for generating images using Google Gemini 2.5 Flash API. Accepts text prompts and up to 3 input images, saves generated images to user-specified or default timestamped paths, supports batch generation with automatic file naming.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: google-genai (Gemini SDK), rich (terminal output styling), pydantic (type validation), pillow (image I/O)
**Storage**: File system (PNG output, JPEG/PNG input)
**Testing**: pytest (unit/integration tests), pyright (type checking), ruff (linting)
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: single (CLI tool)
**Performance Goals**: 60-second API timeout per request, responsive batch processing
**Constraints**: Gemini 2.5 Flash API rate limits, max 3 input images per request
**Scale/Scope**: Single-user CLI tool, local file system operations, external API calls

**Additional Implementation Details**:
- Use UV for dependency management and virtual environment
- All source code in `src/` folder (replace existing main.py)
- Separation of concerns: small, single-responsibility files
- Use rich library for styled CLI output
- Type safety with Pydantic models throughout
- Configuration via environment variables (GEMINI_API_KEY)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with AnyImg Constitution v1.0.0:

**I. CLI-First Design**
- [x] Feature accessible via command-line flags/arguments (--in, --out, --batch, plus prompt as positional/flag)
- [x] Output uses stdout (success) and stderr (errors) - rich library writes to appropriate streams
- [x] Exit codes: 0 for success, non-zero for failures - spec requires clear error reporting

**II. Single Purpose Focus**
- [x] Feature directly supports image generation workflow - core feature is image generation via Gemini
- [x] No scope creep into unrelated functionality - focused solely on image generation with batch support

**III. External API Reliability**
- [x] Network failures handled with clear error messages - FR-012 and constitution requirement
- [x] API responses validated before processing - required by constitution and spec
- [x] Timeouts configured appropriately - FR-017 specifies 60-second timeout

**IV. Environment-Based Configuration**
- [x] No hardcoded API keys or secrets - GEMINI_API_KEY from environment
- [x] Required env vars checked at startup with helpful errors - fail fast with clear messages

**V. Simple File I/O**
- [x] File paths validated before API calls - FR-004 validates input images exist before API request
- [x] File operations have clear error messages - FR-014, FR-015, FR-016 specify file error handling
- [x] Supports both absolute and relative paths - spec mentions current directory default, custom paths

**Testing Standards**
- [x] Tests written before implementation (TDD) - contract tests must be generated and fail initially
- [x] Error handling explicitly tested - batch failures, network errors, file errors
- [x] Integration tests use mocks for external APIs - constitution requires mocks for CI/CD

**Result**: PASS - All constitutional requirements align with feature specification

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/           # Pydantic models for config, requests, responses
├── services/         # Core business logic (image generation, file I/O)
├── cli/             # CLI argument parsing and main entry point
└── utils/           # Helper functions (path validation, timestamp generation)

tests/
├── contract/        # API contract tests (Gemini API interaction mocks)
├── integration/     # End-to-end workflow tests
└── unit/           # Unit tests for individual modules

pyproject.toml       # UV project configuration with dependencies
README.md           # Usage examples and setup instructions
```

**Structure Decision**: Single project structure selected. This is a CLI tool with no web/mobile components. The `src/` folder replaces the existing `main.py` file. Small, focused modules promote maintainability and testability. UV manages the virtual environment and dependencies.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)

**Task Categories**:

1. **Setup Tasks** (Priority: Critical, must complete first):
   - Initialize UV project structure
   - Configure pyproject.toml with dependencies
   - Set up directory structure (src/, tests/)
   - Create __init__.py files

2. **Data Model Tasks** (Priority: High, can be parallelized):
   - Create Pydantic models from data-model.md [P]
     - GenerationConfig model
     - ImageGenerationRequest model
     - ImageGenerationResponse model
     - GenerationResult model
   - Create custom exception hierarchy [P]
   - Unit tests for each model [P]

3. **Contract Test Tasks** (Priority: High, TDD approach):
   - Create contract test fixtures (mock Gemini client) [P]
   - Implement contract tests from gemini_api_contract.md [P]
   - All tests must FAIL initially (no implementation yet)

4. **Service Layer Tasks** (Priority: Medium, make tests pass):
   - Create API client service (Gemini integration)
   - Create file I/O service (path validation, auto-rename logic)
   - Create image service (PIL integration, format validation)
   - Unit tests for each service [P]

5. **CLI Layer Tasks** (Priority: Medium):
   - Create argument parser (--prompt, --in, --out, --batch)
   - Create main entry point with error handling
   - Integrate rich Console for styled output
   - CLI unit tests

6. **Integration Test Tasks** (Priority: Medium):
   - Implement quickstart scenarios as integration tests
   - Each scenario from quickstart.md → one test
   - Use mocks for API calls in CI/CD

7. **Documentation Tasks** (Priority: Low):
   - Create README.md with usage examples from quickstart.md
   - Add inline docstrings to all public functions
   - Create example .env.example file

8. **Quality Assurance Tasks** (Priority: Low, run before completion):
   - Run pyright type checking, fix all errors
   - Run ruff linting, fix all issues
   - Run full test suite, ensure 100% pass rate
   - Manual smoke test with real API key

**Ordering Strategy**:
- TDD order: Contract tests → Models → Service implementation → CLI
- Dependency order: Models → Services → CLI → Integration tests
- Mark [P] for parallel execution (independent files/modules)
- Setup tasks must complete before all others

**Task Dependencies**:
```
Setup → Models → Contract Tests
             ↓
          Services (makes contract tests pass)
             ↓
           CLI (integrates services)
             ↓
     Integration Tests → QA → Documentation
```

**Estimated Output**: 30-35 numbered, dependency-ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, CLAUDE.md created
- [x] Phase 2: Task planning complete (/plan command - approach described)
- [ ] Phase 3: Tasks generated (/tasks command) - NEXT STEP: Run /tasks
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (all principles aligned)
- [x] Post-Design Constitution Check: PASS (no violations introduced)
- [x] All NEEDS CLARIFICATION resolved (via research.md)
- [x] Complexity deviations documented (none - no violations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
