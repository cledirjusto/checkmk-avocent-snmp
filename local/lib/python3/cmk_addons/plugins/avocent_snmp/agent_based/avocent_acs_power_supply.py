#!/usr/bin/env python3
# Checkmk SNMP checks for Avocent ACS console servers
# License: GNU General Public License v2 - see LICENSE
"""Service: 'Power Supply 1' and 'Power Supply 2'.

The ACS 8000 reports one scalar per power supply below
ACS8000-MIB::acsPowerSupply (.1.3.6.1.4.1.10418.26.2.1.8):

    .1.0  acsPowerSupplyNumber     number of power supplies
    .2.0  acsPowerSupplyStatePw1   1 = on, 2 = off, 9999 = not installed
    .3.0  acsPowerSupplyStatePw2   same values
"""

from collections.abc import Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    startswith,
)

STATE_ON = "1"
STATE_OFF = "2"
STATE_NOT_INSTALLED = "9999"

# power supply number -> raw state
Section = Mapping[str, str]


def parse_avocent_acs_power_supply(string_table: StringTable) -> Section | None:
    if not string_table:
        return None
    _number, *states = string_table[0]
    return {str(index): state for index, state in enumerate(states, start=1)}


snmp_section_avocent_acs_power_supply = SimpleSNMPSection(
    name="avocent_acs_power_supply",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.10418.26"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.10418.26.2.1.8",
        oids=["1", "2", "3"],
    ),
    parse_function=parse_avocent_acs_power_supply,
)


def discover_avocent_acs_power_supply(section: Section) -> DiscoveryResult:
    for item, state in section.items():
        if state != STATE_NOT_INSTALLED:
            yield Service(item=item)


def check_avocent_acs_power_supply(item: str, section: Section) -> CheckResult:
    if (state := section.get(item)) is None:
        return
    if state == STATE_ON:
        yield Result(state=State.OK, summary="On")
    elif state == STATE_OFF:
        yield Result(state=State.CRIT, summary="Off")
    elif state == STATE_NOT_INSTALLED:
        yield Result(state=State.CRIT, summary="Not installed")
    else:
        yield Result(state=State.UNKNOWN, summary=f"Unknown state {state!r}")


check_plugin_avocent_acs_power_supply = CheckPlugin(
    name="avocent_acs_power_supply",
    service_name="Power Supply %s",
    discovery_function=discover_avocent_acs_power_supply,
    check_function=check_avocent_acs_power_supply,
)
