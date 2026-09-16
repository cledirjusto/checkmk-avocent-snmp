# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-16

### Added

- `Power Supply <n>` for Avocent ACS 8000, read from ACS8000-MIB
  `acsPowerSupplyStatePw1` and `acsPowerSupplyStatePw2`.

  It replaces an MRPE script that ran `snmpwalk` on the monitoring server. That
  script added the two raw values and alarmed only when the sum was 0 or 1.
  Since off is `2`, one supply off summed to 3 and both off to 4, so it never
  alarmed. On `hq-avocent01` power supply 1 had been without input power
  (1.24 V on a 12 V rail) while the service stayed OK. The script also passed
  the SNMPv3 password on the command line and left the decrypted secrets file
  on disk when the device did not answer. The plug-in uses the credentials
  configured for the host instead.
