# Installation

1. Python 3.12 (the pipeline was executed with Python 3.12.3 on Linux).
2. `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt` (pinned versions; `environment/criar_venv_gpu5070.sh` does the same).
3. Set the base directory: `export BIBLIO_BASE=$(pwd)` (optional; scripts default to the package root).
4. API keys are needed only to re-run the collection and LLM stages: place them, one per file, in `~/.config/bibliogenre/`
   (`openalex`, `s2_api_key`, `scopus_api_key`, `wos_starter_api_key`, `elicit_api_key`, `anthropic_api_key`) and
   `~/.config/bibliometria/` (`openai_api_key`, `gemini_api_key`). Keys are never stored in the package.
5. Minimal check: `python tests/test_smoke.py` (add `--checksums` to verify every file).
