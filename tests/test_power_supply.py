#!/usr/bin/env python3
# Checkmk SNMP checks for Avocent ACS console servers
# License: GNU General Public License v2 - see LICENSE
"""Tests for the 'Power Supply' check."""

from __future__ import annotations

import pytest
from cmk_stub import State
from conftest import load_check_plugin

plugin = load_check_plugin("avocent_acs_power_supply")

# acsPowerSupplyNumber, Pw1, Pw2 as walked on a real ACS 8048 on 2026-09-16,
# with power supply 1 switched off
REAL_DEVICE = [["2", "2", "1"]]


@pytest.fixture
def section():
    return plugin.parse_avocent_acs_power_supply(REAL_DEVICE)


def _check(item, section):
    return list(plugin.check_avocent_acs_power_supply(item, section))


def test_parse_real_device(section):
    assert section == {"1": "2", "2": "1"}


def test_parse_empty():
    assert plugin.parse_avocent_acs_power_supply([]) is None


def test_detect_matches_acs8000():
    detect = plugin.snmp_section_avocent_acs_power_supply.detect
    assert detect.oid == ".1.3.6.1.2.1.1.2.0"
    assert ".1.3.6.1.4.1.10418.26.1.1".startswith(detect.value)


def test_discovery_real_device(section):
    items = [s.item for s in plugin.discover_avocent_acs_power_supply(section)]
    assert items == ["1", "2"]


def test_discovery_skips_not_installed():
    section = plugin.parse_avocent_acs_power_supply([["1", "1", "9999"]])
    items = [s.item for s in plugin.discover_avocent_acs_power_supply(section)]
    assert items == ["1"]


def test_off_is_crit(section):
    (result,) = _check("1", section)
    assert result.state == State.CRIT
    assert result.summary == "Off"


def test_on_is_ok(section):
    (result,) = _check("2", section)
    assert result.state == State.OK
    assert result.summary == "On"


def test_removed_after_discovery_is_crit():
    (result,) = _check("2", {"1": "1", "2": "9999"})
    assert result.state == State.CRIT


def test_unexpected_value_is_unknown():
    (result,) = _check("1", {"1": "7"})
    assert result.state == State.UNKNOWN


def test_missing_item_yields_nothing(section):
    assert _check("3", section) == []
