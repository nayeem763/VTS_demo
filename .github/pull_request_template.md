<!-- Thanks for contributing to CU-VTS. Keep PRs small and focused. -->

## What & why

<!-- What does this change do, and why? Link any issue: Closes #NN -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [ ] Docs / tooling
- [ ] Security fix

## How to test

<!-- Steps for a reviewer to verify locally. -->

## Quality gates

All four must be green locally (CI runs them too):

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy .`
- [ ] `pytest` (added/updated tests for the change)

## Checklist

- [ ] Business logic lives in **services** (writes) / **selectors** (reads), not in views.
- [ ] No secrets, keys, or real `.env` values committed.
- [ ] Model changes include a migration (`makemigrations`), and `migrate` runs clean.
- [ ] The [privacy boundary](../docs/architecture.md#the-privacy-boundary) is preserved — no driver identity leaked to public serializers.
- [ ] Docs updated if behavior, the API contract, or a decision changed.
