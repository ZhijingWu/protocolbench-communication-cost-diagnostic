# Workflow calibration release audit

Prepared 2026-10-11; publication requires separate approval. This is a saved-evidence package, not a new experiment.

## Original evidence and integrity

The full session is recorded as `20261009_full01`, created 2026-10-09T12:49:49Z. The original full-run manifest, seven raw hashes and 14 executed-source hashes were verified. The accepted smoke's manifest linkage, source/input equality and raw hashes agree. All 82 files in the recovered export remained unchanged during preparation. Original private filesystem locations are retained only in the local review record, not in this package.

The six released raw files and three original derived summaries are **byte-identical** copies. Numerical timestamps, durations, protocols, counts, statuses, payload digests and measured outputs were not normalized, replaced or regenerated. Original/public hashes are separate fields even when equal. No synthetic replacement data are included.

## Selection, sanitation and omissions

| Material | Release treatment | Scientific effect |
|---|---|---|
| Six raw record files | Scanned before copying; copied unchanged. | Full timing, receipt, topology, count and order evidence retained. |
| Three processed files | Scanned; copied unchanged, then checked against raw recomputation. | No stored summary replaces missing observations. |
| Original full-run manifest | Not copied; documented descriptive configuration and source hashes exported. Internal command, executable/server paths and dynamic local-port list omitted. | Plans, graphs, payload, counts, date, dependencies, source/input hashes and measurement definitions preserved; no original YAML invented. |
| Original source snapshots | Hashes only; full upstream code not copied. | Source identity traceable; offline reader needs no SDK or server. |
| Console/setup/runtime logs and historical archive | Not copied; failure/smoke/shutdown accounting disclosed in this audit/README. | Setup is outside measured samples; no failures hidden or discarded. |
| Research node IDs and numeric runtime thread IDs | Retained as controlled/opaque research identifiers, not private hostnames, accounts or credentials. | Event correlation and observed runtime metadata unchanged. |
| Historical predictor CSV | Referenced at its existing repository-relative path; not duplicated in this directory. | Frozen data identity verified, no refit. |
| New code/docs/metadata | Authored from audited definitions; scanned for private paths and credentials. | No new measurements or replacement records. |

The package carries no credential values, authorization/cookie headers, access tokens, private IP addresses, personal directories, internal server paths or SSH identities after file-level review. Its observer records contain digests/byte counts and timing metadata, not arbitrary user message content. Public upstream URLs and relative research paths are intentional. A pattern scan is complemented by schema/content inspection; it is not a guarantee against every possible unrecognized secret.

## Publication security and license checklist

- [x] Every candidate source copy scanned before installation.
- [x] Every final package file screened; benign research IDs classified explicitly.
- [x] No original evidence edited; original/public SHA-256 mapping retained.
- [x] No scientifically relevant value sanitized or suppressed silently.
- [x] No original YAML reconstructed as an authentic missing file.
- [x] No full upstream source tree, runtime stores, unscreened archive or unrelated project data.
- [x] Original ProtocolBench/AgentProtocols attribution and repository MIT notice linked and preserved.
- [x] No affiliation, speedup, task-quality or universal-ranking claim.
- [x] No commit, push, homepage change or CV change performed.

## Validation

The offline reader passed publication-hash, raw accounting/timing/receipt/topology, prediction, paired-effect and stored-summary verification. All independently recovered numeric effects and conditional bootstrap intervals reproduce. Four new offline tests passed: complete recalculation from another directory without writes; missing raw data with summaries still present; missing historical profile; and a duration corrupted only in a disposable copy, detected even after its release hash was updated. No corrupt test copy is a publication input.

The original saved-results inspector passed (480 historical measured requests, 80 excluded warmups and unchanged sensitivity results). All 119 legacy release-file hashes passed on a disposable LF snapshot of the intended working tree; the existing Windows checkout converts pre-existing text to CRLF. The package's own exact hashes and offline reader passed directly in the target checkout. Package `.gitattributes` avoids that conversion, while its one historical cost dependency uses declared canonical LF hashing.

A scoped existing-repository offline test run had **35 passing tests (31 existing plus 4 new), 6 existing failures and 2 deselected tests**; 11 official-workflow tests were not run because their external upstream YAML is unavailable. Five failures come from existing `cost_schema.py` using Windows backslash paths to look up forward-slash manifest keys; one router test lacks the separate upstream checkout. Those existing code/tests are unchanged. No claim that the complete legacy suite passes is made; these limitations do not affect the self-contained workflow reader.

The repository-level README received only an appended eight-line section; its prior byte prefix remains intact. The legacy publication manifest refreshes only the README hash and adds explicit old/new amendment provenance. All other legacy hash entries and published numerical evidence remain unchanged. The new package has its own independent release-file map. `git diff --check` passed, and no files were staged. Detailed local preparation output is separate from this publication package.

## Remaining limitations

One local session with deterministic no-op work; historical point prediction; deterministic order confounding; serial paired median interval includes zero; parallel DAG tie and unchanged-stage effects. The package reproduces existing-record calculations, not the original hardware/network/environment execution. Original full console/YAML/environment runtime dependencies are not distributed.
