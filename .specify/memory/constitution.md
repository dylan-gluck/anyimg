# AnyImg Constitution

<!--
Constitution Sync Impact Report:
- Version change: NEW → 1.0.0
- Principles established:
  1. CLI-First Design (NEW)
  2. Single Purpose Focus (NEW)
  3. External API Reliability (NEW)
  4. Environment-Based Configuration (NEW)
  5. Simple File I/O (NEW)
- Templates requiring updates:
  ✅ plan-template.md (references constitution check)
  ✅ spec-template.md (no changes required)
  ✅ tasks-template.md (no changes required)
  ✅ agent-file-template.md (no changes required)
- Follow-up TODOs: None
-->

## Core Principles

### I. CLI-First Design
Every feature MUST be accessible via command-line interface. The tool MUST accept arguments via flags (--in, --out, --batch) and positional parameters. Output MUST go to stdout for success messages and stderr for errors. Exit codes MUST be 0 for success, non-zero for failures.

**Rationale**: As a CLI tool, the primary interface is the command line. Users expect standard Unix conventions for arguments, output streams, and exit codes.

### II. Single Purpose Focus
This tool has one job: generate images using Google Gemini 2.5 Flash API. New features MUST directly support image generation workflows (batch processing, input/output handling, prompt engineering). Features unrelated to image generation MUST be rejected.

**Rationale**: Scope creep dilutes maintainability. A focused tool that does one thing well is more valuable than a Swiss Army knife.

### III. External API Reliability
All API calls to Gemini MUST handle network failures gracefully with clear error messages. Rate limiting MUST be respected. API responses MUST be validated before processing. Timeout values MUST be configurable or sensible defaults.

**Rationale**: External API dependencies are the primary failure point. Users need clear feedback when things go wrong, not cryptic stack traces.

### IV. Environment-Based Configuration
Sensitive data (GEMINI_API_KEY) MUST be provided via environment variables, never hardcoded or committed. The tool MUST check for required environment variables at startup and fail fast with helpful messages if missing.

**Rationale**: API keys in version control are a security vulnerability. Environment variables are the standard secure configuration method for CLI tools.

### V. Simple File I/O
Input images MUST be specified as comma-separated paths (--in). Output paths MUST support both absolute and relative paths with sensible defaults (anyimg_$timestamp.png). File operations MUST validate paths exist and are readable before API calls. File write failures MUST be reported clearly.

**Rationale**: Users interact with files. Clear error messages about file issues prevent wasted API calls and user frustration.

## Testing Standards

### Test Coverage Requirements
- Unit tests MUST cover argument parsing logic
- Integration tests MUST cover API interaction (use mocks for CI/CD)
- Error handling MUST be explicitly tested (missing API key, invalid files, network failures)
- Batch processing MUST have dedicated tests for edge cases (n=0, n=1, n=large)

### Test-First Development
Tests MUST be written before implementation for new features. Tests MUST fail initially. Implementation proceeds only after tests are approved and failing.

**Rationale**: TDD prevents over-engineering and ensures testable code. For a tool with external dependencies, testing error paths is critical.

## Code Quality Standards

### Python Style
- Follow PEP 8 for code style
- Type hints MUST be used for all function signatures
- Docstrings MUST explain the "why" for non-obvious logic
- Functions SHOULD do one thing (Single Responsibility Principle)

### Dependencies
- Minimize dependencies; prefer standard library when possible
- External dependencies MUST be justified (what problem does it solve?)
- Pin dependency versions in pyproject.toml

### Error Messages
- Error messages MUST tell users what went wrong AND how to fix it
- Example: "GEMINI_API_KEY environment variable not found. Set it with: export GEMINI_API_KEY=your_key"
- Avoid technical jargon in user-facing messages

## Governance

### Amendment Process
Constitution changes MUST be documented in the sync impact report at the top of this file. Version MUST be incremented following semantic versioning:
- MAJOR: Principle removal or backward-incompatible governance change
- MINOR: New principle or section added
- PATCH: Clarification or wording improvement

### Compliance Verification
All feature specifications and implementation plans MUST include a "Constitution Check" section verifying alignment with these principles. Violations MUST be justified in the "Complexity Tracking" section of plan.md.

### Tooling
Use `.specify/scripts/bash/update-agent-context.sh claude` to maintain the agent context file incrementally as the project evolves.

**Version**: 1.0.0 | **Ratified**: 2025-09-30 | **Last Amended**: 2025-09-30