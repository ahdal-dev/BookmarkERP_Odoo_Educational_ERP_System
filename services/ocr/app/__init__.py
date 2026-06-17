from fastapi import FastAPI

def create_app():

    app = FastAPI(
        title="OCR Microservice",
        description="Optical Character Recognition service for Educational ERP",
        version="1.0.0",
    )

    app.state.UPLOAD_FOLDER = "uploads"

    # ================================================================
    # Prometheus Instrumentation
    # ================================================================
    # Automatically exposes /metrics endpoint with:
    #   - http_request_duration_seconds (histogram)
    #   - http_requests_total (counter)
    #   - http_request_size_bytes / http_response_size_bytes
    # ================================================================
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=False,
            excluded_handlers=["/health", "/docs", "/openapi.json"],
            env_var_name="ENABLE_METRICS",
        )
        instrumentator.instrument(app).expose(
            app,
            endpoint="/metrics",
            include_in_schema=False,
            tags=["monitoring"],
        )
    except ImportError:
        import logging
        logging.getLogger(__name__).warning(
            "prometheus-fastapi-instrumentator not installed. "
            "Metrics endpoint will not be available."
        )

    from app.routes import router
    app.include_router(router)

    return app


app = create_app()