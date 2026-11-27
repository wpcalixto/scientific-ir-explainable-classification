# Parameters

Frozen values are written in the code of each stage; the main ones are:

- **Queries:** `codigo/adequacao_20261110/consultas_v2.json` (strategies A, B and C in microarrays, metamaterials and radiomics).
- **Collection date:** 2026-11-10 for OpenAlex and all external platforms.
- **Labelling prompt:** `codigo/adequacao_20261110/prompt_rotulacao_v2.md` (classes Applied, Methodological, General).
- **LLM judges:** Claude Haiku 4.5, GPT-5.4-mini and Gemini Flash (requested `gemini-3.5-flash`; the API responses record `gemini-3.6-flash`), temperature 0, without reasoning.
- **Cross-validation:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`; bootstrap seeds as written in F13d, F15b and F15e.
- **Standard deviations:** classifier table with `ddof=0` (NumPy, F10c); ablation table with `ddof=1` (pandas, F13d).
- Symbols and the adopted values of the protocol parameters are listed in the Results section of the article.
