# ADR 003: Introduce FastAPI and NGINX as the API Gateway Layer

**Date:** 2026-05-03

**Status:** Accepted

## Context

The platform needs a single external entry point for browser traffic and API requests, plus a place to centralize routing, request validation, orchestration, and cross-service communication.

The repository already contains a FastAPI gateway and an NGINX reverse proxy. The gateway layer is also important for separating public-facing traffic from internal ERP and OCR services.

## Decision

We will expose the application through NGINX and use FastAPI as the internal orchestration and API layer for the microservices.

## Rationale

NGINX is a proven reverse proxy for TLS termination, routing, buffering, and basic traffic control. FastAPI adds a lightweight Python API layer for composing backend service calls and returning consistent responses to the frontend.

This split keeps browser-facing concerns out of the ERP core and gives the project a clean place for authentication, aggregation, and service coordination.

## Alternatives Considered

- Expose Odoo directly to users. Rejected because it couples public access too tightly to the ERP core.
- Use only NGINX without FastAPI. Rejected because the project needs application-level orchestration and domain APIs.
- Use a heavier gateway platform. Rejected because it adds operational complexity without clear benefit for this project.

## Consequences

Positive consequences:
- Clear external entry point.
- Better separation of concerns.
- Easier to evolve API behavior independently of Odoo.

Negative consequences:
- Adds an extra network hop.
- Requires maintaining routing and health checks across multiple services.

## Implementation Notes

- Keep NGINX responsible for proxying and traffic management.
- Keep FastAPI responsible for orchestration, validation, and integration calls.
- Route internal service calls through Kubernetes service discovery when deployed on cluster.
