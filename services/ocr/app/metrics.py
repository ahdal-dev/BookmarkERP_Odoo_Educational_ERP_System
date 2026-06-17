# -*- coding: utf-8 -*-
"""
Centralized Prometheus Metrics for the OCR Microservice.

Defines custom business-level counters and histograms that are
registered with the default Prometheus registry and incremented
throughout the application logic.
"""
from prometheus_client import Counter, Histogram, Gauge

# =====================================================================
# Business Metrics — Custom Counters
# =====================================================================

ocr_requests_total = Counter(
    'ocr_requests_total',
    'Total number of OCR processing requests received',
    ['status', 'file_type']
)

student_admissions_total = Counter(
    'student_admissions_total',
    'Total number of student admission documents processed via OCR',
    ['document_type']
)

nid_extractions_total = Counter(
    'nid_extractions_total',
    'Total number of National ID extraction attempts',
    ['result']  # success | failure | empty
)

# =====================================================================
# Performance Metrics — Histograms & Gauges
# =====================================================================

ocr_processing_duration_seconds = Histogram(
    'ocr_processing_duration_seconds',
    'Time spent processing an OCR request end-to-end',
    ['operation'],  # detect | extract | nid_ocr
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

api_requests_total = Counter(
    'api_requests_total',
    'Total API requests to the OCR microservice',
    ['method', 'endpoint', 'http_status']
)

active_ocr_jobs = Gauge(
    'active_ocr_jobs',
    'Number of OCR processing jobs currently in progress'
)
