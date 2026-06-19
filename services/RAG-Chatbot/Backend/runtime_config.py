"""Runtime configuration overrides pushed from the Odoo custom_chatbot_admin module.

Most config values (GEMINI_API_KEY, RAG_TOP_K, RAG_LLM_SNIPPETS) are read from the
environment at call-time, so updating ``os.environ`` is enough for them to take
effect live. Two values are captured in module-level constants at import time
(the model name and the system prompts), so they are kept here and read at
call-time by the relevant call sites.
"""
import os

_overrides = {
    "llm_model": None,        # overrides GEMINI_MODEL
    "system_prompt": None,    # overrides the agent system prompt
}


def set_overrides(llm_model=None, system_prompt=None):
    """Store live overrides. Empty/None values clear the corresponding override."""
    _overrides["llm_model"] = llm_model or None
    _overrides["system_prompt"] = system_prompt or None


def get_model_name():
    """Effective LLM model name: override > env GEMINI_MODEL > built-in default."""
    return _overrides["llm_model"] or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_system_prompt(default):
    """Effective agent system prompt: override if set, else the provided default."""
    return _overrides["system_prompt"] or default
