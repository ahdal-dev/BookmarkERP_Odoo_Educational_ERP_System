# ADR 004: Extract OCR into a Dedicated Microservice

**Date:** 2026-05-03

**Status:** Accepted

## Context

The project includes OCR-based document processing for forms and educational records. OCR workloads have different runtime characteristics from the ERP core: they are CPU-intensive, may require model files, and often have longer execution times.

The repository already contains a separate OCR service under `services/ocr/`, which indicates this concern has already been separated from the main application layer.

## Decision

We will keep OCR as a standalone microservice instead of embedding it inside the FastAPI gateway or the Odoo application.

## Rationale

Separating OCR makes the workload independently deployable, scalable, and replaceable. It also reduces coupling between document processing and the ERP transaction flow.

This design allows the OCR service to evolve around model management, file handling, and performance tuning without affecting the core ERP runtime.

## Alternatives Considered

- Embed OCR in the FastAPI application. Rejected because it would bloat the gateway and complicate scaling.
- Embed OCR in Odoo. Rejected because it would mix a compute-heavy service with the ERP core.
- Use an external SaaS OCR API. Rejected because it adds dependency risk and weakens control over data handling.

## Consequences

Positive consequences:
- Independent scaling and deployment.
- Cleaner responsibility boundaries.
- Easier optimization for OCR-specific dependencies and model files.

Negative consequences:
- Additional service to monitor and deploy.
- Requires explicit API contracts and timeout handling.

## Implementation Notes

- Keep the OCR service stateless where possible.
- Store large or temporary files outside the container filesystem when possible.
- Use explicit health checks and timeouts because OCR tasks may take longer than typical API requests.
