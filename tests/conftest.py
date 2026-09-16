#!/usr/bin/env python3
# Checkmk SNMP checks for Avocent ACS console servers
# License: GNU General Public License v2 - see LICENSE
"""Shared test helpers."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "local/lib/python3/cmk_addons/plugins/avocent_snmp"


def load_check_plugin(name: str) -> types.ModuleType:
    """Import one agent_based plug-in against the cmk API stand-in."""
    import cmk_stub

    cmk_stub.install()
    path = PLUGIN_ROOT / "agent_based" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"plugin_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"plugin_{name}"] = module
    spec.loader.exec_module(module)
    return module
