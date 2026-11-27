# Changelog

## v1.0.0 — 2026-11-27
- First public version of the reproducibility package of the article *Protocol for scientific information retrieval with explainable text classification: design and cross-domain evaluation*.
- Replaces the unpublished draft of 2026-04-26 (record 19791096; scripts of the earlier pipeline and a single enriched CSV), which was never published.
- Code: stages F2–F21 and F008 of the final pipeline (`codigo/adequacao_20261110/`) and the F10 re-execution scripts (`resultados/adequacao_20261110/F10_reexec/`).
- Data: OpenAlex, Semantic Scholar, Scopus, Web of Science and Elicit collections of 2026-11-10, facet experiment and public screening benchmarks (`dados/`).
- Results: all result tables, LLM labels and judgements, pseudonymized human judgements and figures (`resultados/`).
- Standard header inserted, comments removed and machine-specific absolute paths replaced by the `BIBLIO_BASE` base directory; the abstract syntax tree of every Python file was compared before and after (see `metadata/quality_control_report.md`).
- Assessors pseudonymized (letters K–W, X–Z); original sheets and manuscript-writing code not included; blinding maps included (no assessor data).
