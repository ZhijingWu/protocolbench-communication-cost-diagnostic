# Outreach technical note v2 — scientific schematic and two-page layout

> Historical source-study record, made public-safe during packaging. Use the root README for current standalone commands. Source-time hashes and execution statements retain their original meaning; see PUBLICATION.md. Superseded outreach previews/v1 documents described here remain in the original study checkout; they are omitted from this artifact.


Date: 2026-10-05. Author: Zhijing Wu, Sichuan University, CS undergraduate.
This is a visual/typographic redesign of the audited outreach note. No scientific
experiment, model/API call, measurement recomputation or result change occurred.
No email was sent. The original v1 note and figures are preserved byte-for-byte.

Destination:
`<ARTIFACT_ROOT>/outreach/v2/`.
Source commit: `6349eb97f0ca83db9cbfd44dea0bbdbb3ea9d37f`.
Public repository: [ulab-uiuc/AgentProtocols](https://github.com/ulab-uiuc/AgentProtocols).

## Package

```text
v2/
  technical_note_v2.tex
  technical_note_v2.pdf
  claim_check_v2.md
  README_v2.md
  figures/
    protocol_assignment_mechanism.pptx
    protocol_assignment_mechanism.png
    protocol_latency_v2.pdf
  previews/
    page_1.png
    page_2.png
```

The PDF has exactly two A4 pages with 17 mm margins. Page 1 centers the agent/edge
mechanism and before/after witness; page 2 uses a fixed two-column grid for costs
and the objective, then a full-width interpretation and one open question.

## What changed visually

- Replaced the four-card pipeline with native agent circles, protocol tags,
  meaningful communication edges, a measured-cost dot bank, and two versions of
  the same analysis template. Only the changed agent receives a halo.
- Moved the full latency plot to page 2; used direct endpoint labels, restrained
  marks and light gridlines, retaining every stored mean and the ANP outlier.
- Used one primary family, **Arial**, across the document, equation, editable
  PowerPoint and vector chart. The installed Windows Arial files were used;
  no font or dependency was installed.
- Used four primary text levels: title 22 pt, subtitle/headings 13 pt, body 11 pt,
  contact/captions/footer/math indices 9.5 pt. The sum operator is a larger Arial
  mathematical glyph. Figure labels are at least about 9.6 pt when embedded.
- Removed repeated wording and excessive paragraph/section spacing instead of
  shrinking important text. Evidence items align on a shared hanging baseline.
- Used the same protocol colors throughout: A2A blue `#356E97`, ACP muted amber
  `#B58235`, ANP teal `#167C80`, Agora muted purple `#7F648D`; neutral ink `#203642`.
  No gradients, shadows, decorative icons or panel containers.

## Compile the editable source

From this directory, with an existing XeLaTeX installation and Arial installed:

```bash
xelatex -interaction=nonstopmode -halt-on-error technical_note_v2.tex
xelatex -interaction=nonstopmode -halt-on-error technical_note_v2.tex
```

Keep `figures/` beside the `.tex`. No absolute data paths, BibTeX database, custom
class, shell escape, model/API access or experiment rerun is needed. Packages:
`fix-cm`, `geometry`, `fontspec`, `graphicx`, `xcolor`, `array`, `enumitem`, `hyperref`.
`fix-cm` avoids unused LaTeX internal math-size warnings; all actual visible glyphs
are Arial. Membership is written “in E” in the equation, without a fallback font.

Actual compilation used preinstalled MiKTeX XeLaTeX with installation disabled:

```powershell
& 'xelatex' --disable-installer `
  -interaction=nonstopmode -halt-on-error `
  '-output-directory=<LATEX_OUTPUT_DIR>' `
  technical_note_v2.tex
```

The v2 source was opened in the built-in LaTeX editor. That compiler still reports
`Unable to find standard directories for platform`. The source remains editable;
the delivered PDF was successfully compiled with the existing external XeLaTeX,
then rendered and inspected. No plugin or TeX installation was added.

## Figure editability and numerical provenance

`protocol_assignment_mechanism.pptx` contains one landscape scientific figure,
1400×1030 CSS-pixel canvas, with native circles, shapes, text, protocol tags,
connectors and lines; no screenshot/image assembly. It was authored with the
provided Artifact Tool runtime, structurally validated and imported again, then
rendered at scale 3 to a 4200×3090 PNG. At the final 176 mm figure width this is
about 606 dpi, exceeding the 300 dpi requirement. Its height is about 129.5 mm,
49% of page 1's available height. Edit the native objects in PowerPoint and export
a new PNG to update the LaTeX note. Microsoft PowerPoint itself was not executed.

The native cost-bank dots show the exact saved 10 KB means on a labeled logarithmic
axis; no visual bar lengths or ranking precision are invented. The latency chart
uses all 16 exact saved means. Matplotlib 3.10.0 in the existing local Anaconda
Python 3.13.5 was used solely for chart authoring, with installed Arial and PDF
font embedding. These authoring tools do not replace the scientific experiment
environment `python`; the prohibited gtd Python
was never used. No package was installed and no scientific program was rerun.

Plot source: `../../results/processed/real_protocol_costs.csv` from this directory.
All exact strings are retained in `claim_check_v2.md`. Connecting lines are visual
guides, not new observations; direct endpoint-label leaders attach to the correct
stored points. No error bar or statistical-superiority annotation was fabricated.

A minimal saved-data plot can be regenerated with an existing Arial/Matplotlib
installation, without recomputing a measurement:

```python
import csv
import matplotlib.pyplot as plt
from pathlib import Path

rows = list(csv.DictReader(Path('../../results/processed/real_protocol_costs.csv')
                          .open(encoding='utf-8')))
colors = {'A2A':'#356E97', 'ACP':'#B58235', 'ANP':'#167C80', 'Agora':'#7F648D'}
plt.rcParams.update({'font.family':'Arial', 'font.size':10, 'pdf.fonttype':42})
for protocol, color in colors.items():
    group = sorted((r for r in rows if r['protocol'] == protocol),
                   key=lambda r: int(r['payload_size_bytes']))
    plt.plot([int(r['payload_size_bytes'])/1024 for r in group],
             [float(r['mean_latency_ms']) for r in group],
             marker='o', color=color, label=protocol)
plt.yscale('log')
plt.xticks([1,10,50,100])
plt.xlabel('Payload (KB; 1 KB = 1024 bytes)')
plt.ylabel('Mean local request latency (ms; log axis)')
plt.legend()
plt.tight_layout()
plt.savefig('latency_reconstructed.pdf')
```

This reproduces the unchanged numerical inputs, not the exact v2 visual styling.
The delivered PDF already contains the complete vector plot and can be reused.

## Scientific boundary preserved

Authoritative sources are the unchanged final audit, focused local-preference
audit, findings, microbenchmark note and saved processed results, plus the v1
claim check. Full source/result links and sentence checks are in
`claim_check_v2.md` (55/55 SAFE).

Baseline remains `{0:Agora,1:A2A,2:ACP,3:A2A}`. The all-four analysis witness remains
`{0:Agora,1:ANP,2:ACP,3:A2A}` at 10 KB, per-edge demand 100, λ=0.1 and unit synthetic
replacement loss. The declared additive destination-cost objective is unchanged
and separable by incoming demand. Protocol-preference metadata does not enter loss.
The final marker is terminal, not an extra agent or cost-bearing edge.

Global Agora exclusion forces agent 0 to change. Agent 1's eligible reversal
persists, but the restricted analysis has **no whole-assignment gain versus the
original, now-infeasible baseline** after the forced replacement penalty:
original-reference delta `+0.4350270000000016`, feasible-seed delta
`-0.5649729999999984`. The note retains this qualification.

No scientific claim was strengthened. V2 newly displays the already-audited
37/144 controlled statistic and a miniature view of existing 10 KB means; neither
is a new result. The expanded supported/not-established section restates v1's
boundaries. The final constraint-preserving question is conditional future work,
not a claim that present alternatives satisfy validated task requirements.

No GAIA task-quality or makespan improvement, calibrated utility/margin,
observed GAIA traffic, intrinsic ranking, new router superiority, defect or
novelty is claimed. No scientific source, result, measured latency/byte value,
baseline, objective, margin, topology, candidate semantics or workflow changed.

## Reference

Hongyi Du et al., “ProtocolBench: Which LLM MultiAgent Protocol to Choose?”,
ICML 2026. [Official ICML listing](https://icml.cc/Downloads/2026);
[OpenReview](https://openreview.net/forum?id=GZRiXE2zBe).
V1's recorded primary metadata verification remains the reference check; its
direct-OpenReview browser-verification limitation is preserved. No new external
scientific claim or copied published figure was introduced.

## Visual QA

- Both final PDF pages rendered at **200 dpi** to `previews/page_1.png` and
  `previews/page_2.png`; both inspected individually.
- Both pages also rendered at **100 dpi**, corresponding to approximately 50%
  of the QA preview scale, and inspected individually for hierarchy/readability.
- Final hero figure inspected independently and within page 1; latency plot
  inspected within page 2.
- Figure arrows terminate at agent boundaries, terminal flow is dashed, only
  agent 1 is highlighted, and explanatory leaders do not invent message edges.
- No clipping, overlap, orphaned footer, tiny important text or awkward line break
  remains. Caption and paragraph spacing were checked at both scales.
- PDF visible text uses only Arial regular/bold/italic subsets; no second visual
  family. Minimum document size is 9.5 TeX pt (about 9.4645 PDF pt); the embedded
  chart minimum is about 9.64 PDF pt and hero label minimum about 9.62 PDF pt.
  Rotated-axis character bounding heights are not mistaken for font sizes.
- Final external LaTeX log has no missing-glyph, overfull, underfull or font-size
  substitution warning. Native PPTX integrity, shape/font geometry and import
  validation passed. No native PowerPoint rendering was claimed.
- No commit, push, source edit, scientific experiment rerun or outreach send.

<!-- final-integrity-and-delivery -->

## Final verified integrity and delivery

All **607 existing protected files**, including all seven v1 outreach files, have identical before/after content hashes. All 16 saved latency strings match the figure inputs. Scientific claims/results and original source files were unchanged; no experiment rerun, commit or push occurred. All nine v2 files matched the remote mirror.

Actual `git status --short`:

```text
?? experiments/
```

`git diff --check`: exit 0, no output. HEAD remains the baseline; tracked and staged diffs are empty.

Native hero: 91 shapes, 24 connectors, zero image shapes, one slide. Visible PDF fonts: Arial-BoldMT, Arial-ItalicMT, ArialMT.

PDF: exactly 2 A4 pages, 623,330 bytes. Intended minimum text size: 9.5 pt; embedded hero labels: about 9.62 PDF pt. All 55 claim entries SAFE. Both 200 dpi previews and 50% scale views were checked visually; no final rendering issue.

| File | Bytes |
|---|---:|
| `claim_check_v2.md` | 15,895 |
| `figures/protocol_assignment_mechanism.png` | 587,388 |
| `figures/protocol_assignment_mechanism.pptx` | 19,873 |
| `figures/protocol_latency_v2.pdf` | 27,539 |
| `previews/page_1.png` | 506,406 |
| `previews/page_2.png` | 537,775 |
| `technical_note_v2.pdf` | 623,330 |
| `technical_note_v2.tex` | 8,187 |

README size changes with this appendix; the final source package contains the updated file.
