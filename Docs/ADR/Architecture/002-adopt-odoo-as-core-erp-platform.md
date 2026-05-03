# ADR 002: Adopt Odoo as the Core ERP Platform

**Date:** 2026-05-03

**Status:** Accepted

## Context

The project is an educational ERP for a graduation project, not a general-purpose business ERP. It needs a stable transactional core that can be extended with custom student, admission, attendance, exam, library, and portal workflows.

The repository already contains a substantial Odoo codebase with custom addons under `addons/` and an existing Odoo runtime under `odoo/`. Replacing that stack would increase delivery risk and divert effort from the domain-specific features that matter most.

## Decision

We will use Odoo as the primary ERP platform and implement education-specific behavior through custom addons rather than building a new ERP core from scratch.

## Rationale

Odoo provides a mature ORM, modular add-on model, authentication, views, and workflow patterns that fit the project well. It reduces time spent on foundational platform work and lets the project focus on education domain requirements.

The custom addon approach keeps the domain logic isolated from the upstream framework, which makes upgrades, maintenance, and testing more manageable.

## Alternatives Considered

- Build a custom ERP from scratch. Rejected because it would take significantly longer and introduce more risk.
- Use another ERP platform. Rejected because the repository is already centered on Odoo and its customization model.
- Keep all custom logic in a single monolith. Rejected because it would reduce maintainability and make future changes harder.

## Consequences

Positive consequences:
- Faster delivery of core academic workflows.
- Reuse of Odoo authentication, ORM, and UI patterns.
- Clear separation between platform behavior and education-specific modules.

Negative consequences:
- The system inherits Odoo’s conventions and upgrade constraints.
- Addon compatibility must be maintained carefully across updates.

## Implementation Notes

- Keep custom features inside dedicated education modules under `addons/`.
- Avoid editing upstream Odoo core unless absolutely required.
- Prefer module-level overrides, extension classes, and views over direct framework modification.
