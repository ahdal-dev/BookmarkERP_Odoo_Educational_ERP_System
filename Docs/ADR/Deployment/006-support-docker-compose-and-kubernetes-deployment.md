# ADR 006: Support Docker Compose and Kubernetes for Deployment

**Date:** 2026-05-03

**Status:** Accepted

## Context

The project is moving from a local Docker-based setup toward Kubernetes, but the repository still needs a straightforward local development path. The team also needs a clear deployment story that works for both developer machines and cluster environments.

Docker Compose is already present in the repository, while Kubernetes manifests are being added for the microservices architecture.

## Decision

We will keep Docker Compose for local development and introduce Kubernetes as the production-oriented orchestration platform.

## Rationale

Docker Compose remains the easiest way to bootstrap the stack locally and reproduce the development environment. Kubernetes is better suited to service discovery, health checks, scaling, and high availability in a deployed setting.

Supporting both reduces friction during migration and lets the team validate behavior locally before deploying to a cluster.

## Alternatives Considered

- Replace Docker Compose immediately. Rejected because it would make local development harder.
- Use only Kubernetes for all environments. Rejected because it increases setup complexity for everyday development.
- Stay on Docker Compose only. Rejected because it does not provide the operational model needed for deployment.

## Consequences

Positive consequences:
- Better developer experience locally.
- A clear path to production deployment.
- Easier migration because each environment has a supported execution model.

Negative consequences:
- Two deployment targets must be maintained.
- Environment differences must be documented carefully.

## Implementation Notes

- Keep Docker Compose aligned with the Kubernetes manifests as much as practical.
- Use the same service names and environment concepts across both environments.
- Document the deployment order and service dependencies in the repo.
