# Avocent ACS console servers via SNMP – Checkmk extension

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](LICENSE)
![Checkmk 2.3+](https://img.shields.io/badge/Checkmk-2.3%2B-green)

Checkmk SNMP check plug-ins for Avocent ACS 8000 console servers. Checkmk ships
no checks for this device family, so without this extension a failed power
supply goes unnoticed.

Verified against an **ACS 8048 with dual power supply (firmware 2.28.4)** on a
**Checkmk 2.3.0p49** site. It uses only `cmk.agent_based.v2`, which is identical
on 2.3, 2.4 and 2.5, but 2.4 and 2.5 have not been tested.

## Services

| Service | What it does |
| --- | --- |
| `Power Supply <n>` | OK when the power supply is on, CRIT when it is off. One service per installed power supply |

A power supply that has no input power reports as off, so a loose cable or a
tripped circuit shows up here. The ACS web interface shows the same condition
under *Voltages*, as a `Power Supply <n>` reading far below its 11.06–12.98 V
range.

## Requirements

* Checkmk 2.3.0 or newer.
* SNMP enabled on the ACS, v2c or v3, reachable from the Checkmk site.

## Installation

1. Download the latest `avocent_snmp-<version>.mkp` from the
   [releases page](../../releases), or build it yourself (see below).
2. Install it on the central site:

   ```
   OMD[mysite]:~$ mkp add avocent_snmp-0.1.0.mkp
   OMD[mysite]:~$ mkp enable avocent_snmp 0.1.0
   ```

   or use *Setup → Maintenance → Extension packages* in the commercial editions.

3. Check that it loaded: `cmk-validate-plugins` should report success.

## Configuration

1. Create one host per ACS with the management IP as address. Set *Checkmk
   agent / API integrations* to **"No API integrations, no Checkmk agent"** and
   *SNMP* to the version you use.
2. For SNMPv3, add the credentials with the rule *Setup → Agents → SNMP rules →
   SNMP credentials of monitored hosts*.
3. Activate and run a service discovery.

The plug-in is selected by `sysObjectID`, which must start with
`.1.3.6.1.4.1.10418.26` (ACS 8000). Other hosts are never queried for it.

## Reporting a problem

If a service is missing or its state looks wrong, attach an SNMP walk of the
relevant subtrees, taken as the site user:

```
OMD[mysite]:~$ cmk --snmpwalk --oid .1.3.6.1.2.1.1 --oid .1.3.6.1.4.1.10418.26.2.1 <host>
OMD[mysite]:~$ cat ~/var/check_mk/snmpwalks/<host>
```

It uses the credentials already configured for the host. The output contains
the hostname and serial number of the device, so edit those out before posting.

## How it works

| OID | ACS8000-MIB name | Values |
| --- | --- | --- |
| `.1.3.6.1.4.1.10418.26.2.1.8.1.0` | `acsPowerSupplyNumber` | number of power supplies |
| `.1.3.6.1.4.1.10418.26.2.1.8.2.0` | `acsPowerSupplyStatePw1` | `1` on, `2` off, `9999` not installed |
| `.1.3.6.1.4.1.10418.26.2.1.8.3.0` | `acsPowerSupplyStatePw2` | same |

A power supply that reports `9999` at discovery gets no service. One that
reports it after discovery is CRIT, since it was there before.

## Development

Nothing in this section ships to a site: the `.mkp` contains only the files
under `local/`.

```
python3 -m venv .venv && .venv/bin/pip install pytest ruff
.venv/bin/python -m pytest -q
.venv/bin/ruff check . && .venv/bin/ruff format --check .
python3 scripts/build_mkp.py --update-manifest   # -> dist/avocent_snmp-<version>.mkp
```

The check functions run against `tests/cmk_stub.py`, a stand-in for
`cmk.agent_based.v2` that keeps the real API's validation rules.

To release, bump `version` in `package.manifest` and `pyproject.toml`, update
`CHANGELOG.md` and tag `v<version>`. The GitHub workflow builds the `.mkp` and
attaches it to the release.

## License

GNU General Public License v2 (GPL-2.0-or-later), see [LICENSE](LICENSE).

Avocent is a trademark of Vertiv. This project is not affiliated with or
endorsed by Vertiv or Checkmk GmbH.
