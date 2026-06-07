# ADR 005: Standardize on PostgreSQL for Persistence

**Date:** 2026-05-03

**Status:** Accepted

## Context

The project needs a reliable relational database for student records, admissions, grading, attendance, and ERP transactions. Odoo also expects a PostgreSQL backend as part of its standard deployment model.

The repository and deployment work already point toward PostgreSQL as the primary persistence layer.

## Decision

We will standardize on PostgreSQL as the primary database for the educational ERP system.

## Rationale

PostgreSQL is a strong fit for transactional ERP workloads. It provides ACID guarantees, mature indexing, good tooling, and compatibility with Odoo.

Using a single primary relational database simplifies the data model and avoids introducing unnecessary storage technologies for the project’s current scope.

## Alternatives Considered

- Use MySQL or MariaDB. Rejected because PostgreSQL is the best match for the Odoo stack and the project’s relational needs.
- Split the application across multiple databases. Rejected because it adds complexity without a clear benefit at this stage.
- Use a document database as the primary store. Rejected because the core domain is relational.

## Consequences

Positive consequences:
- Consistent storage model for ERP data.
- Better compatibility with Odoo.
- Simpler backup and restore procedures.

Negative consequences:
- Database administration must be handled carefully.
- The platform depends on strong relational schema design.

## Implementation Notes

- Keep schema and migration changes coordinated with Odoo module updates.
- Use secrets for database credentials.
- Prefer persistent storage in production instead of ephemeral volumes.
