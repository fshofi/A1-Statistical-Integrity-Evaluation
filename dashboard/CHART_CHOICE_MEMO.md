# A1 Plotly Companion — Chart-choice memo

## Primary decision

Help a reviewer answer: **where did the model discriminate correctly across the matched contrasts, and where do material defects or adjudication risks remain?**

## Selected visuals

1. **KPI strip** — bounded summary before detail.
2. **Matched-pair explorer** — preserves the 12-pair design instead of implying 24 iid cases.
3. **Case-status matrix** — compares requested numeric output, verdict defensibility, and adjudication status.
4. **Defect typology** — localises Q195, Q361, Q976, plus retained Q731 dissent.
5. **Interpretation layers** — separates frozen parser coverage from independent recomputation and semantic/statistical judgement.
6. **Case table** — exact textual inspection route and accessible fallback.

## Rejected alternatives

- Pie/donut charts: weak precision and no benefit for this evidence shape.
- Radar charts: would imply continuous comparable dimensions not established by the adjudication.
- Population confidence intervals: unsupported by the selected matched-case design.
- Dense Sankey diagrams: decorative for the primary decision and likely to obscure evidence.
- Geographic/time-series charts: not relevant to the data-generating structure.

## Governing visual rule

Interaction must reveal evidence, not conceal it. Limitations and retained dissent remain visible in the companion.
