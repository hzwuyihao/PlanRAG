# PlanRAG

PlanRAG is a retrieval-augmented language-model pipeline for extracting structured development attributes from unstructured planning-permission text. It was developed for the paper **“Compliance costs constrain climate-adaptive housing supply in flood-exposed cities”**, which studies how flood-risk regulation shapes residential development in Greater London. The repository is intended to make the code logic transparent for review. It also includes a small demo input file and analysis scripts.

## Repository structure

```text
PlanRAG/
├── analysis/
│   ├── regression_tables.do
│   ├── heterogeneity.do
│   └── adaptation_mechanism.do
├── data/
│   └── demo_input.csv
├── planrag/
│   ├── __init__.py
│   ├── classifier.py
│   ├── pipeline.py
│   └── retrieval.py
├── prompts/
│   ├── classification_schema.json
│   └── system_prompt.txt
├── .gitignore
├── LICENSE
└── README.md
```

## What PlanRAG does

PlanRAG converts free-text planning-application descriptions into structured variables used in application-level analysis of housing development and climate adaptation. The pipeline follows three steps:

1. **Retrieval**: relevant policy and planning-context passages are retrieved for each application description.
2. **Classification**: a language model classifies the proposal using a structured schema.
3. **Output assembly**: the classification results are merged back onto the input application records.

The classification fields are designed to capture development relevance, development type, housing typology, residential unit change, intensification, adaptation language, and related planning attributes.

## Demo data

The repository includes:

```text
data/demo_input.csv
```

This file contains a small set of planning-application descriptions for demonstrating the required input format. The minimum required columns are:

```text
application_reference
description
```

The demo file may also include auxiliary columns such as:

```text
lpa
decision_date
```

These auxiliary fields are preserved in the output but are not required by the core PlanRAG pipeline.

The full application-level dataset used in the paper is not included because it contains large-scale planning records, geocoded site information, flood-risk joins, and validation annotations used during the review process.

## Python requirements

The core Python pipeline uses:

```text
pandas
numpy
tqdm
sentence-transformers
openai
```

A typical installation is:

```bash
pip install pandas numpy tqdm sentence-transformers openai
```

## Running the demo

From the repository root, run:

```python
from planrag.pipeline import run_pipeline

run_pipeline(
    input_csv="data/demo_input.csv",
    output_csv="data/demo_output.csv",
    use_cache=False
)
```

When `use_cache=False`, the pipeline calls the OpenAI API. Before running, set your API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

The output file will be written to:

```text
data/demo_output.csv
```

## Cached responses

The pipeline supports cached LLM responses through:

```text
data/cached_llm_responses.json
```

If `use_cache=True`, each `application_reference` in the input file must already exist in the cache. This is useful for deterministic review runs and for avoiding repeated API calls.

## Retrieval corpus

The retrieval module expects a precomputed corpus-embedding file at:

```text
data/corpus_embeddings.npz
```

The file should contain two arrays:

```text
embeddings
passages
```

The full reference corpus used in the paper is not redistributed in this public repository. Users who wish to run the full retrieval workflow should construct a domain-specific corpus of planning-policy passages, officer reports, decision notices, or related documents, embed the passages, and save them in the expected `.npz` format.

## Analysis scripts

The `analysis/` folder contains Stata scripts corresponding to the main empirical components of the paper:

```text
analysis/regression_tables.do
analysis/heterogeneity.do
analysis/adaptation_mechanism.do
```

These scripts are provided to document the econometric specifications used for the approval, development-scale, heterogeneity, and adaptation-mechanism analyses. They require the restricted analysis dataset constructed from the full planning corpus, geocoded site-level variables, flood-risk overlays, and PlanRAG outputs. 

## Data availability

This repository provides code and a small demo input file for transparency and review. The full planning-application corpus, geocoded application-level dataset, flood-risk spatial joins, and manually coded validation labels are not publicly redistributed here.

## Citation

If using or referring to this code, please cite the associated manuscript:

```text
Wu, Yihao. “Compliance costs constrain climate-adaptive housing supply in flood-exposed cities.”
Working paper.
```

## License

This repository is released under the MIT License.
