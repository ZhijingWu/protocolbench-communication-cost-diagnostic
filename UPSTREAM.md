# Upstream attribution

- Upstream repository: https://github.com/ulab-uiuc/AgentProtocols
- Upstream project: **ProtocolBench / AgentProtocols**
- Audited baseline commit: **6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f**
- License: MIT; the upstream license text and `Copyright (c) 2025 Hongyi-Du` notice are preserved in [LICENSE](LICENSE).

This repository contains an **independent experimental extension / diagnostic**. It is **not an official ProtocolBench repository** and does not imply affiliation with UIUC or the ProtocolBench authors. Original upstream authors retain attribution for upstream code and design.

Only the isolated `experiments/topology_aware_protocol` extension is packaged here. A compatible separate upstream checkout supplies the released pure UTE/converters, GAIA fallback router, official workflow YAML, and original client/server implementations when those execution paths are used. No large upstream source subtree is copied.

Set `AGENTPROTOCOLS_ROOT` to that checkout, or place it beside this artifact as `AgentProtocols`. Use the audited commit for exact source/config compatibility. Read-only result inspection is independent of upstream. [README.md](README.md) distinguishes saved-result inspection, offline tests, optional profiling, and optional workflow sensitivity.

Historical audit references prefixed `E/` denote this artifact root; other repository-relative source references denote the upstream checkout at the audited commit. Line numbers in historical audits refer to the original upstream/experiment source before standalone packaging changes. Public source hashes and the original-to-public file map are recorded in [notes/publication_manifest.json](notes/publication_manifest.json).
