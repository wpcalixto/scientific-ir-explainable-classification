# Reproducibility

- **Executed versions.** The scripts are the files executed for the article; their SHA-256 before and after re-annotation are in `_registo` of the authors and summarized in `metadata/quality_control_report.md`.
- **Re-annotation.** Original comments and module docstrings were removed and the standard header was inserted; the absolute prefix of the
  project directory was replaced by `BIBLIO_BASE`. The abstract syntax tree of every Python file was compared before and after (with the path prefix normalized).
- **Collections.** Web APIs change over time; the archived collections of 2026-11-10 in `dados/` are the inputs of all analyses.
- **LLM outputs.** The labels and judgements returned by the APIs are archived in `resultados/` (F2_rotulacao_v2, F7_painel_llm); re-running the paid calls is not needed.
- **Human judgements.** Pseudonymized grades (assessors K–W for the top-10 census, X–Z for P@100, replication teams) are archived; all human metrics can be recomputed from them.
- **Integrity.** `checksums/checksums_sha256.txt` and `metadata/file_manifest.csv`; `python tests/test_smoke.py --checksums`.
