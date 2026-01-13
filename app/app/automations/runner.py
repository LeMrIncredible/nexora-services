"""
Nexora Automation Runner

- Dynamically imports each automation module
- Passes client + payload + credentials
- Returns a normalized result dict

Each automation package must expose:
  automation.py with a function: run(**kwargs) -> dict
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, Optional

AUTOMATION_SLUG_TO_MODULE = {
    "lead-capture": "app.app.automations.lead_capture.automation",
    "estimate-generator": "app.app.automations.estimate_generator.automation",
    "invoice-tracking": "app.app.automations.invoice_tracking.automation",
    "reputation-followup": "app.app.automations.reputation_followup.automation",
    "smart-booking": "app.app.automations.smart_booking.automation",
}


def run_automation(slug: str, *, client: Any, payload: Optional[Dict[str, Any]] = None, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    credentials = credentials or {}

    if slug not in AUTOMATION_SLUG_TO_MODULE:
        return {"ok": False, "slug": slug, "error": f"Unknown automation slug: {slug}"}

    module_path = AUTOMATION_SLUG_TO_MODULE[slug]
    try:
        mod = importlib.import_module(module_path)
    except Exception as e:
        return {"ok": False, "slug": slug, "error": f"Import failed: {e}", "module": module_path}

    if not hasattr(mod, "run"):
        return {"ok": False, "slug": slug, "error": "Module missing run() function", "module": module_path}

    try:
        import inspect

        # Standardized inputs (only pass what the automation supports)
        candidate_kwargs = {
            # base context
            "client_name": getattr(client, "name", None),
            "client_slug": getattr(client, "slug", None),

            # raw passthroughs (some automations use these)
            "payload": payload,
            "credentials": credentials,

            # --- common lead fields (mapped from payload) ---
            "lead_name": payload.get("lead_name") or payload.get("name") or payload.get("full_name"),
            "lead_email": payload.get("lead_email") or payload.get("email"),
            "lead_phone": payload.get("lead_phone") or payload.get("phone"),
            "source": payload.get("source") or payload.get("lead_source"),

            # --- common job fields ---
            "job_title": payload.get("job_title") or payload.get("job") or payload.get("service") or payload.get("title"),
            "job_id": payload.get("job_id"),
        }

        # If this is a test run and required fields are missing,
        # provide safe placeholder values so tests always execute.
        if payload.get("test") is True:
            candidate_kwargs.setdefault("lead_name", candidate_kwargs["lead_name"] or "Test Lead")
            candidate_kwargs.setdefault("lead_email", candidate_kwargs["lead_email"] or "test@example.com")
            candidate_kwargs.setdefault("job_title", candidate_kwargs["job_title"] or "Test Job")

        sig = inspect.signature(mod.run)
        allowed = set(sig.parameters.keys())
        safe_kwargs = {k: v for k, v in candidate_kwargs.items() if k in allowed}

        result = mod.run(**safe_kwargs)

        if isinstance(result, dict):
            result.setdefault("ok", True)
            result.setdefault("slug", slug)
            return result
        return {"ok": True, "slug": slug, "result": result}
    except Exception as e:
        return {"ok": False, "slug": slug, "error": str(e)}
