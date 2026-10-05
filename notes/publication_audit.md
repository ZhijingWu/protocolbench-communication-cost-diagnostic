# Publication preparation audit

Date: 2026-10-05 (Asia/Shanghai). Source baseline: `6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f`.

The standalone artifact content passed scientific-integrity, offline-test, privacy, licensing, and documentation checks. Git staging is performed only after this preparation gate; its actual status and final staged-diff check are recorded in the separately delivered preparation report. No commit or push is part of this task.

## Checks actually performed

- Source experiment: all 118 source file hashes, file inventory, HEAD, tracked diff, and detailed Git status verified unchanged.
- All 19 scientific CSV files remain byte-identical, including current and historical measurements and sensitivity tables.
- All 23,302 numeric, Boolean, and null leaves in copied source JSON files remain unchanged.
- All 20 original Python files have equivalent ASTs after only the documented namespace, path bootstrap, upstream-location, and generated documentation path changes. Config files and the scientific objective/oracle remain unchanged.
- Existing offline suite: `python -m pytest -q -p no:cacheprovider tests`; **50 passed in 1.34s**, using the compatible existing Python 3.11.13 environment and separate upstream checkout. Bytecode and pytest cache writing were disabled. Disposable fixture regression checks do not overwrite saved evidence.
- `python scripts/inspect_saved_results.py`: PASS. Independently checked 560 recorded request intervals, 16 condition statistics, 480 measured successes, 80 excluded warmups, 37/144 controlled reversals, 144 workflow cases, and both analysis witnesses from saved files.
- No real protocol profiling, GAIA task, LLM call, or workflow/graph experiment rerun was performed. Unit tests exercise pure functions and disposable regression fixtures only.
- Recursive security/privacy scan: no credential value, private machine path, credential-bearing URL, proxy credential configuration, or private API endpoint detected. Harmless keyword matches are individually classified in `security_scan.json`.
- Binary inspection: both PDFs checked with Poppler text/metadata; final note additionally inspected with pypdf for metadata/annotations/attachments (no attachments), rendered and visually reviewed on both A4 pages. PPTX XML and relationships checked (no external relationships). PNG metadata contains only DPI and sRGB.
- Author name, Sichuan University affiliation, email, and public author website in the final note are intentional outreach details from the source; retained. Loopback addresses and ephemeral local server ports retain transport provenance.
- Upstream MIT LICENSE copied byte-for-byte, preserving the original 2025 Hongyi-Du copyright notice; UPSTREAM.md states independent diagnostic status and no implied UIUC/ProtocolBench affiliation.
- Relative Markdown links and fences checked across public Markdown. Both external README destinations returned HTTP 200: upstream repository and exact audited commit.
- Root README rendered with Marked GFM and existing headless Edge; visually reviewed. One H1, five H2 sections, six code blocks, 18 links, no page-width overflow. Rendering is a QA approximation of GitHub styling.
- Exact requested large-file check: `find . -type f -size +25M -print`; exit 0, no output. No file exceeds 25 MiB.
- Whitespace preflight identified one extra EOF blank line in each of two ANP diagnostic text logs; only those redundant blank lines were removed in the artifact. No log event or numeric field changed. The final Git staged-diff check is reported separately.

## Claim and limits

Strongest README claim: “The audited released GAIA assignment path does not directly condition protocol assignment on explicit graph/edge-demand inputs. Using measured local request costs, controlled communication demand, and explicit synthetic local preference margins, the declared sensitivity objective can admit assignment reversals.”

The README discloses synthetic local margins, controlled demand, template-instantiation conventions, implementation-specific local latency, the retained ANP outlier, absent calibrated suitability/validated feasible masks, and lack of task-quality, makespan, GAIA/ProtocolRouter improvement, superiority, universal rankings, or novelty evidence. Eligible no-Agora reversal and whole-assignment gain are explicitly separated.

## Exact included public files

```text
.gitignore
LICENSE
PUBLICATION.md
README.md
UPSTREAM.md
configs/microbench.yaml
configs/topology_cases.yaml
notes/change_report.md
notes/cost_interface_before.json
notes/cost_interface_validation.txt
notes/cost_interface_verification.json
notes/experiment_design.md
notes/final_audit.md
notes/final_audit_tests.txt
notes/findings.md
notes/gaia_workflow_before.json
notes/gaia_workflow_run.txt
notes/gaia_workflow_validation.txt
notes/gaia_workflow_verification.json
notes/integrity_checks.json
notes/local_preference_signal_audit.md
notes/publication_audit.md
notes/publication_manifest.json
notes/real_environment_freeze.txt
notes/real_existing_27_tests.txt
notes/real_joint_assignment_run.txt
notes/real_microbench.md
notes/real_profiler_run.txt
notes/real_validation.txt
notes/real_validation_all.txt
notes/security_scan.json
notes/source_readme.md
notes/validation.txt
outreach/README.md
outreach/claim_check.md
outreach/v2/README_v2.md
outreach/v2/claim_check_v2.md
outreach/v2/figures/protocol_assignment_mechanism.png
outreach/v2/figures/protocol_assignment_mechanism.pptx
outreach/v2/figures/protocol_latency_v2.pdf
outreach/v2/technical_note_v2.pdf
outreach/v2/technical_note_v2.tex
requirements-test.txt
results/figures/.gitkeep
results/processed/decision_reversal.csv
results/processed/gaia_workflow_reversal.csv
results/processed/gaia_workflow_summary.json
results/processed/protocol_costs.csv
results/processed/protocol_costs_conversion-only.csv
results/processed/protocol_costs_real.csv
results/processed/real_protocol_costs.csv
results/processed/reversal_summary.json
results/processed/reversal_thresholds.csv
results/processed/topology_blindness.csv
results/raw/cost_interface_archive/5071d5f2d4fbaa17e4206cf1450defedf9b7ced1e2aa79ae0f3a465cdf5bb898/protocol_costs_real.csv
results/raw/cost_interface_archive/9d72fe3c741a18b2c0c8924d3f643c229b2232507ec53a4fc1fb13d74d53dd09/protocol_costs.csv
results/raw/cost_interface_manifest.json
results/raw/joint_manifest.json
results/raw/joint_output_archive/1233150d85156166f5aaacac0221b3df99017840ad1eb41e66e5ebe1a66df523/joint_manifest.json
results/raw/joint_output_archive/237a11fadb06fec17043f6c695605e3d07cd1a7db0f34f8748b6ccecc3e27dc3/reversal_thresholds.csv
results/raw/joint_output_archive/a2eefdc97afa4f569a4dda4eddeed51aab546aa5a4f00d08a9b3140ec05b04cc/decision_reversal.csv
results/raw/joint_output_archive/aa0edd44c80a585788e5170945f06068b67cbc8c653e27fb953a72ef3e8b9f79/findings.md
results/raw/local_router_output.json
results/raw/profile_manifest_conversion-only.json
results/raw/profile_manifest_real.json
results/raw/protocol_profile_conversion-only.csv
results/raw/protocol_profile_conversion-only.json
results/raw/protocol_profile_real.csv
results/raw/protocol_profile_real.json
results/raw/real_diagnostic_observer_v1/real_protocol_costs.csv
results/raw/real_diagnostic_observer_v1/real_protocol_manifest.json
results/raw/real_diagnostic_observer_v1/real_protocol_profile.csv
results/raw/real_diagnostic_observer_v1/real_protocol_profile_failures.json
results/raw/real_diagnostic_observer_v1/real_protocol_setup.csv
results/raw/real_diagnostic_observer_v1/workers/A2A.json
results/raw/real_diagnostic_observer_v1/workers/A2A.txt
results/raw/real_diagnostic_observer_v1/workers/ACP.json
results/raw/real_diagnostic_observer_v1/workers/ACP.txt
results/raw/real_diagnostic_observer_v1/workers/ANP.json
results/raw/real_diagnostic_observer_v1/workers/ANP.txt
results/raw/real_diagnostic_observer_v1/workers/Agora.json
results/raw/real_diagnostic_observer_v1/workers/Agora.txt
results/raw/real_protocol_manifest.json
results/raw/real_protocol_profile.csv
results/raw/real_protocol_profile_failures.json
results/raw/real_protocol_run_config.json
results/raw/real_protocol_setup.csv
results/raw/real_workers/A2A.json
results/raw/real_workers/A2A.txt
results/raw/real_workers/ACP.json
results/raw/real_workers/ACP.txt
results/raw/real_workers/ANP.json
results/raw/real_workers/ANP.txt
results/raw/real_workers/Agora.json
results/raw/real_workers/Agora.txt
results/raw/topology_cases.json
results/raw/topology_manifest.json
scripts/inspect_saved_results.py
scripts/run_gaia_workflow_assignment.py
scripts/run_joint_assignment.py
scripts/run_protocol_profile.py
scripts/run_topology_blindness.py
scripts/verify_artifact.py
src/__init__.py
src/cost_schema.py
src/gaia_workflow.py
src/gaia_workflow_experiment.py
src/graph_aware_oracle.py
src/io_utils.py
src/local_protocol_microbench.py
src/local_router_adapter.py
src/objective.py
src/protocol_cost_profiler.py
src/topology_generator.py
tests/test_cost_schema.py
tests/test_gaia_workflow.py
tests/test_graph_aware_oracle.py
tests/test_objective.py
tests/test_real_microbench.py
tests/test_topology_generator.py
```

The source README is preserved as `notes/source_readme.md`; the root README is new. Source-to-public hashes, paths, and modifications are fully recorded in `publication_manifest.json`.

## Exact excluded source files

- `notes/real_dependency_install.txt`: Transient package-install log; package versions and environment freeze are retained.
- `outreach/README.md`: Superseded packaging instructions; replaced by a public index to the final v2 note.
- `outreach/figures/diagnostic_pipeline.png`: Superseded v1 visual; final v2 mechanism visual is retained.
- `outreach/figures/diagnostic_pipeline.pptx`: Superseded v1 visual source; final v2 editable visual is retained.
- `outreach/figures/protocol_latency.pdf`: Superseded v1 chart; final v2 chart is retained.
- `outreach/technical_note.pdf`: Superseded v1 PDF; final v2 PDF and both claim audits are retained.
- `outreach/technical_note.tex`: Superseded v1 TeX; final v2 editable source is retained.
- `outreach/v2/previews/page_1.png`: QA preview duplicates a page in the final PDF.
- `outreach/v2/previews/page_2.png`: QA preview duplicates a page in the final PDF.
- `results/raw/agora_runtime/receiver.json`: Empty transient Agora receiver runtime state; no measurement or claim provenance.

No cache, bytecode, editor temporary, package-cache, environment file, secret file, unrelated private trajectory, or symlink was found among the 118 source files; none is added to the artifact.

## Every private-path redaction group

Each row specifies the public file, category, occurrence count, and original source line numbers. Only public-safe replacement labels are published. JSON traceback instances are all enumerated, rather than silently discarded. Original source hashes and current public hashes are mapped separately; historical source-time hashes are retained in scientific records.

| Public file | Change category | Count | Source lines |
|---|---|---:|---|
| `notes/source_readme.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 94 |
| `notes/source_readme.md` | Private Python executable path generalized; replacement `python` | 6 | 31, 34, 55, 57, 84, 96 |
| `notes/change_report.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 3 |
| `notes/change_report.md` | Unused private environment prefix generalized; replacement `<UNUSED_PYTHON_ENV>` | 1 | 35 |
| `notes/final_audit.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 2 | 4, 332 |
| `notes/final_audit.md` | Private Python executable path generalized; replacement `python` | 1 | 334 |
| `notes/findings.md` | Private Python executable path generalized; replacement `python` | 1 | 96 |
| `notes/local_preference_signal_audit.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 4 |
| `notes/real_microbench.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 91 |
| `notes/real_microbench.md` | Private Python executable path generalized; replacement `python` | 4 | 3, 93, 97, 98 |
| `outreach/claim_check.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 9 |
| `outreach/v2/README_v2.md` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 1 | 9 |
| `outreach/v2/README_v2.md` | Private Python executable path generalized; replacement `python` | 1 | 98 |
| `outreach/v2/README_v2.md` | Private Windows authoring output path generalized; replacement `<LATEX_OUTPUT_DIR>` | 1 | 73 |
| `outreach/v2/README_v2.md` | Machine-specific TeX executable generalized; replacement `xelatex` | 1 | 71 |
| `outreach/v2/claim_check_v2.md` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 10 |
| `results/processed/gaia_workflow_summary.json` | Private upstream absolute path replaced by upstream-root placeholder; replacement `<UPSTREAM_ROOT>` | 1 | 1815 |
| `results/raw/joint_manifest.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 1 | 84 |
| `results/raw/joint_manifest.json` | Private Python executable path generalized; replacement `python` | 1 | 88 |
| `results/raw/joint_output_archive/1233150d85156166f5aaacac0221b3df99017840ad1eb41e66e5ebe1a66df523/joint_manifest.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 1 | 84 |
| `results/raw/joint_output_archive/1233150d85156166f5aaacac0221b3df99017840ad1eb41e66e5ebe1a66df523/joint_manifest.json` | Unused private environment prefix generalized; replacement `<UNUSED_PYTHON_ENV>` | 1 | 87 |
| `results/raw/profile_manifest_conversion-only.json` | Unused private environment prefix generalized; replacement `<UNUSED_PYTHON_ENV>` | 1 | 35 |
| `results/raw/profile_manifest_real.json` | Unused private environment prefix generalized; replacement `<UNUSED_PYTHON_ENV>` | 1 | 56 |
| `results/raw/real_diagnostic_observer_v1/real_protocol_manifest.json` | Private Python executable path generalized; replacement `python` | 1 | 30 |
| `results/raw/real_diagnostic_observer_v1/real_protocol_profile_failures.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 420 | 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 201, 211, 221, 231, 241, 251, 261, 271, 281, 291, 301, 311, 321, 331, 341, 351, 361, 371, 381, 391, 401, 411, 421, 431, 441, 451, 461, 471, 481, 491, 501, 511, 521, 531, 541, 551, 561, 571, 581, 591, 601, 611, 621, 631, 641, 651, 661, 671, 681, 691, 701, 711, 721, 731, 741, 751, 761, 771, 781, 791, 801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 921, 931, 941, 951, 961, 971, 981, 991, 1001, 1011, 1021, 1031, 1041, 1051, 1061, 1071, 1081, 1091, 1101, 1111, 1121, 1131, 1141, 1151, 1161, 1171, 1181, 1191, 1201, 1211, 1221, 1231, 1241, 1251, 1261, 1271, 1281, 1291, 1301, 1311, 1321, 1331, 1341, 1351, 1361, 1371, 1381, 1391, 1401, 1411, 1421, 1431, 1441, 1451, 1461, 1471, 1481, 1491, 1501, 1511, 1521, 1531, 1541, 1551, 1561, 1571, 1581, 1591, 1601, 1611, 1621, 1631, 1641, 1651, 1661, 1671, 1681, 1691, 1701, 1711, 1721, 1731, 1741, 1751, 1761, 1771, 1781, 1791, 1801, 1811, 1821, 1831, 1841, 1851, 1861, 1871, 1881, 1891, 1901, 1911, 1921, 1931, 1941, 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2021, 2031, 2041, 2051, 2061, 2071, 2081, 2091, 2101, 2111, 2121, 2131, 2141, 2151, 2161, 2171, 2181, 2191, 2201, 2211, 2221, 2231, 2241, 2251, 2261, 2271, 2281, 2291, 2301, 2311, 2321, 2331, 2341, 2351, 2361, 2371, 2381, 2391, 2401, 2411, 2421, 2431, 2441, 2451, 2461, 2471, 2481, 2491, 2501, 2511, 2521, 2531, 2541, 2551, 2561, 2571, 2581, 2591, 2601, 2611, 2621, 2631, 2641, 2651, 2661, 2671, 2681, 2691, 2701, 2711, 2721, 2731, 2741, 2751, 2761, 2771, 2781, 2791, 2801, 2811, 2821, 2831, 2841, 2851, 2861, 2871, 2881, 2891, 2901, 2911, 2921, 2931, 2941, 2951, 2961, 2971, 2981, 2991, 3001, 3011, 3021, 3031, 3041, 3051, 3061, 3071, 3081, 3091, 3101, 3111, 3121, 3131, 3141, 3151, 3161, 3171, 3181, 3191, 3201, 3211, 3221, 3231, 3241, 3251, 3261, 3271, 3281, 3291, 3301, 3311, 3321, 3331, 3341, 3351, 3361, 3371, 3381, 3391, 3401, 3411, 3421, 3431, 3441, 3451, 3461, 3471, 3481, 3491, 3501, 3511, 3521, 3531, 3541, 3551, 3561, 3571, 3581, 3591, 3601, 3611, 3621, 3631, 3641, 3651, 3661, 3671, 3681, 3691, 3701, 3711, 3721, 3731, 3741, 3751, 3761, 3771, 3781, 3791, 3801, 3811, 3821, 3831, 3841, 3851, 3861, 3871, 3881, 3891, 3901, 3911, 3921, 3931, 3941, 3951, 3961, 3971, 3981, 3991, 4001, 4011, 4021, 4031, 4041, 4051, 4061, 4071, 4081, 4091, 4101, 4111, 4121, 4131, 4141, 4151, 4161, 4171, 4181, 4191, 4201 |
| `results/raw/real_diagnostic_observer_v1/workers/A2A.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 140 | 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 201, 211, 221, 231, 241, 251, 261, 271, 281, 291, 301, 311, 321, 331, 341, 351, 361, 371, 381, 391, 401, 411, 421, 431, 441, 451, 461, 471, 481, 491, 501, 511, 521, 531, 541, 551, 561, 571, 581, 591, 601, 611, 621, 631, 641, 651, 661, 671, 681, 691, 701, 711, 721, 731, 741, 751, 761, 771, 781, 791, 801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 921, 931, 941, 951, 961, 971, 981, 991, 1001, 1011, 1021, 1031, 1041, 1051, 1061, 1071, 1081, 1091, 1101, 1111, 1121, 1131, 1141, 1151, 1161, 1171, 1181, 1191, 1201, 1211, 1221, 1231, 1241, 1251, 1261, 1271, 1281, 1291, 1301, 1311, 1321, 1331, 1341, 1351, 1361, 1371, 1381, 1391, 1401 |
| `results/raw/real_diagnostic_observer_v1/workers/A2A.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/real_diagnostic_observer_v1/workers/ACP.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 140 | 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 201, 211, 221, 231, 241, 251, 261, 271, 281, 291, 301, 311, 321, 331, 341, 351, 361, 371, 381, 391, 401, 411, 421, 431, 441, 451, 461, 471, 481, 491, 501, 511, 521, 531, 541, 551, 561, 571, 581, 591, 601, 611, 621, 631, 641, 651, 661, 671, 681, 691, 701, 711, 721, 731, 741, 751, 761, 771, 781, 791, 801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 921, 931, 941, 951, 961, 971, 981, 991, 1001, 1011, 1021, 1031, 1041, 1051, 1061, 1071, 1081, 1091, 1101, 1111, 1121, 1131, 1141, 1151, 1161, 1171, 1181, 1191, 1201, 1211, 1221, 1231, 1241, 1251, 1261, 1271, 1281, 1291, 1301, 1311, 1321, 1331, 1341, 1351, 1361, 1371, 1381, 1391, 1401 |
| `results/raw/real_diagnostic_observer_v1/workers/ACP.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/real_diagnostic_observer_v1/workers/ANP.json` | Historical experiment absolute path replaced by artifact-root placeholder; replacement `<ARTIFACT_ROOT>` | 140 | 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 201, 211, 221, 231, 241, 251, 261, 271, 281, 291, 301, 311, 321, 331, 341, 351, 361, 371, 381, 391, 401, 411, 421, 431, 441, 451, 461, 471, 481, 491, 501, 511, 521, 531, 541, 551, 561, 571, 581, 591, 601, 611, 621, 631, 641, 651, 661, 671, 681, 691, 701, 711, 721, 731, 741, 751, 761, 771, 781, 791, 801, 811, 821, 831, 841, 851, 861, 871, 881, 891, 901, 911, 921, 931, 941, 951, 961, 971, 981, 991, 1001, 1011, 1021, 1031, 1041, 1051, 1061, 1071, 1081, 1091, 1101, 1111, 1121, 1131, 1141, 1151, 1161, 1171, 1181, 1191, 1201, 1211, 1221, 1231, 1241, 1251, 1261, 1271, 1281, 1291, 1301, 1311, 1321, 1331, 1341, 1351, 1361, 1371, 1381, 1391, 1401 |
| `results/raw/real_diagnostic_observer_v1/workers/ANP.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 9 | 1, 159, 161, 164, 167, 172, 174, 177, 180 |
| `results/raw/real_diagnostic_observer_v1/workers/Agora.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/real_protocol_manifest.json` | Private Python executable path generalized; replacement `python` | 1 | 30 |
| `results/raw/real_workers/A2A.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/real_workers/ACP.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/real_workers/ANP.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 9 | 1, 159, 161, 164, 167, 172, 174, 177, 180 |
| `results/raw/real_workers/Agora.txt` | Private environment prefix generalized in tracebacks; replacement `<PYTHON_ENV>` | 1 | 1 |
| `results/raw/topology_manifest.json` | Unused private environment prefix generalized; replacement `<UNUSED_PYTHON_ENV>` | 1 | 86 |
| `scripts/run_joint_assignment.py` | Private Python executable path generalized; replacement `python` | 1 | 199 |

Documentation path migration, historical-record labels, .gitignore replacement, standalone import/location adaptation, and the two EOF whitespace fixes are additional packaging edits documented per file in the manifest; they are not scientific edits.

## Hash semantics

Historical hashes describe original source-time bytes, including superseded versions. Public manifests/tracebacks with paths generalized have different byte hashes. The publication manifest retains the exact original hashes and maps the public equivalents; its release hash map covers public files excluding itself. Some archive-directory names therefore remain identifiers of original bytes. Raw current request/summary hashes consumed by the code remain valid because those CSVs are unchanged.
