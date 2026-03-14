# AGENTS.md

Practical instructions for coding agents working in this repository.

## Scope

This file defines repository working rules for coding agents.

Focus on:
- making minimal, correct changes
- keeping responsibilities separated
- preserving existing project conventions
- validating changed behavior before finalizing

## General Rules

- Keep changes small and local.
- Prefer adapting existing patterns over introducing new ones.
- Do not perform broad refactors unless explicitly requested.
- Do not add infrastructure or abstraction layers without a direct need.
- Preserve async style, typing, and existing naming conventions.
- Keep user-visible behavior explicit and debuggable.

## Responsibility Rules

- Keep transport-layer code thin.
- Put orchestration and business flow into services.
- Keep persistence logic in repository layer.
- Keep provider-specific LLM logic isolated.
- Keep config loading centralized.
- Do not move durable-state rules into runtime FSM handling.
- Do not treat LLM output as durable truth without validation.

## Change Rules

When changing behavior:
- update only the layers that are actually affected
- keep boundaries clear between handlers, services, repositories, and integration code
- avoid duplicating logic across Telegram flow, API flow, and service layer
- reuse existing mappers, DTOs, enums, and exceptions where appropriate

When changing persistence:
- update schema, ORM, repositories, and migrations together
- do not change old migrations unless explicitly required

When changing commands or chat flow:
- keep handler changes minimal
- move non-trivial branching and orchestration into services

When changing LLM-related behavior:
- keep prompt construction and output parsing centralized
- do not scatter parsing or fallback behavior across unrelated modules

## Consistency Rules

- Preserve clear separation between transport, orchestration, persistence, and external integrations.
- Do not put business decisions into handlers.
- Do not put high-level flow logic into repositories.
- Do not bypass existing service-level coordination without a strong reason.
- Keep cross-module data flow explicit.
- Prefer existing typed contracts over ad-hoc dictionaries when data crosses boundaries repeatedly.

## Safety Rules

- Never commit secrets or `.env` values.
- Never hardcode tokens, API keys, or DSNs.
- Do not silently change runtime behavior unrelated to the task.
- Do not introduce Redis, queues, workers, vector storage, or new service decomposition unless explicitly requested.
- Do not replace simple working flows with generic frameworks.

## Validation Rules

Before finalizing:
- run formatting and lint checks expected by the repository
- run tests affected by the change
- verify imports and startup-critical paths if bootstrap/config changed
- verify migrations if schema changed

Typical baseline:

```bash
make pre-commit
make test
```

If commands differ, use the commands actually defined in the repository.

## Change Checklist

For behavior changes, verify:
- request/command flow still reaches the correct service path
- changed logic is covered in the right layer
- persistence remains consistent
- fallback/error paths still behave clearly
- config changes are reflected in docs or setup files when relevant

For schema changes, verify:
- models match migrations
- repositories match schema
- dependent contracts are updated

For LLM changes, verify:
- request assembly still works
- parsing is robust to invalid output
- failure handling remains explicit
- partial or degraded behavior does not crash the app

## Commit Rules

- Use Conventional Commits.
- Keep one logical change per commit.
- Include migrations with related schema changes.
- Include tests with behavior changes when possible.
- Include docs/setup updates when configuration or developer workflow changes.

Examples:
- `feat(chat): add assistant response streaming`
- `fix(memory): deduplicate facts by normalized key`
- `refactor(bot): move chat turn orchestration into service`
- `test(commands): cover reset flow`

## Anti-Patterns

Avoid:
- broad refactors inside a feature task
- business logic in handlers
- direct persistence orchestration from transport layer
- duplicated LLM prompt logic
- duplicated fallback logic in multiple layers
- unvalidated storage of parsed external output
- introducing abstractions that solve no current problem

## Decision Rule

When several implementations are possible, prefer the one that:
1. changes the fewest moving parts
2. keeps responsibilities clear
3. matches existing conventions
4. is easier to validate locally
5. avoids unnecessary complexity