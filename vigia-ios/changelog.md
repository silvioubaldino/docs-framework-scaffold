---
id: CHANGELOG
type: changelog
title: Changelog
status: approved
updated: 2026-08-23
parents: []
related: []
---

# Changelog

<!--
Format: Keep a Changelog (https://keepachangelog.com) · SemVer.
Entries in ENGLISH (project convention), even though the docs are in Portuguese.
Log here every change to a living doc (REQ / ARCH / ROAD / AYD) and every new ADR/SPEC.
-->

## [Unreleased]

### Added
- Initial documentation set for **Vigia**: requirements + glossary (REQ-001), living
  architecture with the three candidate topologies (ARCH), roadmap (ROAD-001).
- AYD-001 camera protocol discovery, AYD-002 live streaming, AYD-003 PTZ control,
  AYD-004 remote access.
- ADR-001 native iOS app, ADR-002 remote access over mesh VPN, ADR-003 video stack
  (draft, blocked on the probe).
- SPEC-001 camera protocol probe, with `tools/probe_camera.py` as its executable form.
- Simplified single-repo variant of the specs-driven docs framework (`CLAUDE.md`).
