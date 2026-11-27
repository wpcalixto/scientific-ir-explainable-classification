# Prompt de rotulação v2 (para aprovação) — 10/11/2026

## O que muda em relação ao v1 (`04_rotulacao_llm.py`, abril de 2026)

| Aspeto | v1 | v2 |
|---|---|---|
| Classes | Clinico / Metodologico / Geral | **Applied / Methodological / General** (“Clínico” passa a “Aplicado”, definido por domínio) |
| Domínio no pedido | Não | **Sim**: o texto indica o domínio, para “Applied” ter sentido em metamateriais |
| Língua do prompt | Português | **Inglês** (vai ser publicado no artigo/suplemento tal como está) |
| Exemplos (*few-shot*) | Nenhum (o artigo diz que havia: discrepância a corrigir) | Nenhum (*zero-shot*), declarado assim |
| Temperatura | Default da API (1,0), não registada | **0**, registada |
| Resposta inválida | Virava “Geral” em silêncio | Repetida uma vez; se continuar inválida, fica **`INVALID`** e é contada |
| Documentos sem resumo | Ignorados | Rotulados **só pelo título**, com indicador `sem_resumo=1` (as análises podem excluí-los) |
| Truncamento | 3.000 caracteres | 3.000 caracteres (igual) |
| Execução | Chamadas uma a uma | **Batches API** (mesmo modelo, 50% mais barato, respostas brutas guardadas) |
| Modelo | claude-haiku-4-5-20251001 | **claude-haiku-4-5-20251001** (igual) |

Custo estimado: ~23 mil documentos únicos × ~650 tokens ≈ 15 M tokens de entrada → **~US$ 8** com a Batches API.

## Texto do prompt (system)

```
You are an expert in scientometrics. Classify the scientific document below into exactly one of three categories, considering the research domain indicated.

CATEGORIES
- Applied: the central contribution is the use of computational or data-driven methods to solve a concrete problem of the domain.
    * Gene expression (microarray) and radiomics domains: clinical, diagnostic, prognostic or biological applications (e.g., disease classification, outcome prediction, biomarker discovery in patient data).
    * Metamaterials domain: design, fabrication or characterisation of a specific device, structure or engineering application (e.g., an absorber, antenna, metasurface or sensor).
- Methodological: the central contribution is the development, comparison or evaluation of methods themselves (feature selection, machine learning models, evaluation metrics such as AUC-ROC, design/optimisation algorithms), with the application playing a secondary or illustrative role.
- General: reviews, surveys, tutorials, perspectives, bibliometric studies, or documents that fit neither of the other categories.

Answer with exactly one word: Applied, Methodological or General.
```

## Texto do pedido (user)

```
Domain: {Gene expression (microarray) | Radiomics | Metamaterials}
Title: {title}
Abstract: {abstract | "not available"}
```

O texto é cortado em 3.000 caracteres. Documentos que estão em mais de um domínio recebem um rótulo por domínio.

## Depois da rotulação (já no plano)

- **Validação humana nova (F8.4):** a amostra antiga de 54 documentos é do corpus e das classes v1 e não serve para o v2. Proposta: uma amostra estratificada por domínio e classe (balanceada) **mais** uma amostra aleatória com a prevalência real. Os avaliadores W e U avaliam às cegas; calcula-se κ com IC 95% (Haiku × cada especialista e especialista × especialista).
- **Teste-reteste (F7.3):** 1.000 documentos rotulados duas vezes, para medir a estabilidade.
