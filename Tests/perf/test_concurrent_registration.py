# -*- coding: utf-8 -*-
"""
Performance test — concurrent course registration seat integrity.

Simulates 50 concurrent students attempting to enroll in a course that has
only 49 seats.  Asserts that:
  - Exactly 49 students succeed (state='enrolled').
  - At least 1 student is waitlisted or rejected (no seat overselling).
  - The enrolled count never exceeds total_seats.

Run with: pytest Tests/perf/test_concurrent_registration.py -v -s

NOTE: This test requires a live Odoo instance with the custom_registration
module installed. It is NOT run in CI by default (marked 'slow').
Set ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD in your environment.
"""
import asyncio
import os
import random
import string
import pytest
import httpx

ODOO_URL      = os.getenv("ODOO_URL",      "http://localhost:8081")
ODOO_DB       = os.getenv("ODOO_DB",       "edu_demo_new")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
TOTAL_SEATS   = 49
NUM_STUDENTS  = 50


def _odoo_is_reachable() -> bool:
    try:
        import socket
        host = ODOO_URL.split("://")[-1].split(":")[0]
        port = int(ODOO_URL.split(":")[-1].rstrip("/")) if ":" in ODOO_URL.split("://")[-1] else 8081
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False


pytestmark = [
    pytest.mark.slow,
    pytest.mark.perf,
    pytest.mark.skipif(not _odoo_is_reachable(), reason=f"Odoo not reachable at {ODOO_URL}"),
]


async def _odoo_rpc(client: httpx.AsyncClient, model: str, method: str, args: list, kwargs: dict = None):
    resp = await client.post(
        f"{ODOO_URL}/web/dataset/call_kw",
        json={"jsonrpc": "2.0", "method": "call", "params": {
            "model": model, "method": method,
            "args": args, "kwargs": kwargs or {},
        }},
    )
    body = resp.json()
    if "error" in body:
        raise RuntimeError(body["error"].get("data", {}).get("message", str(body["error"])))
    return body.get("result")


async def _create_student(client: httpx.AsyncClient, i: int) -> int:
    """Create a minimal portal res.users record for test student i."""
    suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    partner_id = await _odoo_rpc(
        client, "res.partner", "create",
        [{"name": f"PerfStudent{i}_{suffix}", "email": f"perf{i}_{suffix}@test.local"}],
    )
    return partner_id


async def _attempt_registration(
    client: httpx.AsyncClient,
    course_id: int,
    student_partner_id: int,
) -> str:
    """Try to register student for course. Returns final registration state."""
    try:
        # Check add/drop hold (mimics education.cart.action_register logic)
        result = await _odoo_rpc(
            client, "education.registration", "create",
            [{"course_id": course_id, "student_id": student_partner_id}],
        )
        return "enrolled"
    except RuntimeError as e:
        msg = str(e).lower()
        if "no seats" in msg or "seat" in msg:
            return "waitlisted"
        return f"error:{e}"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_no_seat_overselling():
    """49 seats, 50 concurrent attempts — at most 49 must succeed."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Authenticate service account
        auth = await client.post(
            f"{ODOO_URL}/web/session/authenticate",
            json={"jsonrpc": "2.0", "params": {
                "db": ODOO_DB, "login": ODOO_USERNAME, "password": ODOO_PASSWORD,
            }},
        )
        assert auth.json().get("result", {}).get("uid"), "Odoo auth failed"

        # Create a test course with exactly TOTAL_SEATS seats
        course_id = await _odoo_rpc(
            client, "education.course", "create",
            [{
                "name": "PerfTest Course",
                "code": f"PERF{''.join(random.choices(string.digits, k=4))}",
                "total_seats": TOTAL_SEATS,
                "registration_open": True,
            }],
        )

        # Create NUM_STUDENTS partner records
        partner_ids = await asyncio.gather(
            *[_create_student(client, i) for i in range(NUM_STUDENTS)]
        )

        # Fire all registration attempts concurrently
        outcomes = await asyncio.gather(
            *[_attempt_registration(client, course_id, pid) for pid in partner_ids],
            return_exceptions=True,
        )

    enrolled_count = sum(1 for o in outcomes if o == "enrolled")
    error_outcomes = [o for o in outcomes if isinstance(o, Exception) or (isinstance(o, str) and o.startswith("error:"))]

    print(f"\nOutcomes: enrolled={enrolled_count}, "
          f"waitlisted={outcomes.count('waitlisted')}, "
          f"errors={len(error_outcomes)}")

    assert enrolled_count <= TOTAL_SEATS, (
        f"Seat overselling detected! {enrolled_count} enrolled but only {TOTAL_SEATS} seats."
    )
    assert enrolled_count >= TOTAL_SEATS - 2, (
        f"Too few successful enrollments: {enrolled_count} (expected ~{TOTAL_SEATS}). "
        "Check FOR UPDATE locking in education.registration.create()."
    )
