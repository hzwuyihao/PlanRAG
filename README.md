# PlanRAG

PlanRAG is a retrieval-augmented language-model pipeline for extracting structured development attributes from unstructured planning-permission text. It was developed for the paper **“Compliance costs constrain climate-adaptive housing supply in flood-exposed cities”**, which studies how flood-risk regulation shapes residential development in Greater London. The repository is intended to make the code logic transparent for review. It includes source code, prompt files, a demo input file, an example expected output file, and analysis scripts.

## Repository structure

```text
PlanRAG/
├── analysis/
│   ├── regression_tables.do
│   ├── heterogeneity.do
│   └── adaptation_mechanism.do
├── data/
│   ├── demo_input.csv
│   └── demo_expected_output.csv
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

## System requirements

The code requires Python 3.10 or later. It has been tested on macOS using a standard desktop/laptop environment. No non-standard hardware is required.

The core Python pipeline uses:

```text
pandas
numpy
tqdm
sentence-transformers
openai
```

The empirical scripts in `analysis/` require Stata and user-written table-export commands where applicable.

## Installation

A typical installation is:

```bash
pip install pandas numpy tqdm sentence-transformers openai
```

Typical installation time on a normal desktop computer is approximately 5–15 minutes, depending on internet speed, Python environment, and whether the sentence-transformer model needs to be downloaded for the first time. Installation may take longer on a fresh machine or restricted institutional network.

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

The expected output structure is shown in:

```text
data/demo_expected_output.csv
```

On a normal desktop computer, the demo runtime can range from approximately 10 to 30 minutes, depending primarily on API latency, model availability, internet connection, and whether retrieval embeddings are already available. Runs may take longer on slower networks or when external API responses are delayed.

## Cached responses

The pipeline supports cached LLM responses through:

```text
data/cached_llm_responses.json
```

If `use_cache=True`, each `application_reference` in the input file must already exist in the cache. This is useful for deterministic review runs and for avoiding repeated API calls. A cached run is expected to be substantially faster than a live API run.

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

## Instructions for use on new data

To run PlanRAG on another planning-application file, prepare a CSV with at least the following columns:

```text
application_reference
description
```

Then run:

```python
from planrag.pipeline import run_pipeline

run_pipeline(
    input_csv="path/to/your_input.csv",
    output_csv="path/to/your_output.csv",
    use_cache=False
)
```

Additional columns in the input file are preserved in the output.

## Analysis scripts

The `analysis/` folder contains Stata scripts corresponding to the main empirical components of the paper:

```text
analysis/regression_tables.do
analysis/heterogeneity.do
analysis/adaptation_mechanism.do
```

These scripts are provided to document the econometric specifications used for the approval, development-scale, heterogeneity, and adaptation-mechanism analyses. They require the restricted analysis dataset constructed from the full planning corpus, geocoded site-level variables, flood-risk overlays, and PlanRAG outputs.

## Reproducing manuscript results

This repository documents the code structure and provides a runnable demonstration of the PlanRAG classification workflow. Full reproduction of the manuscript tables and figures requires the restricted application-level analysis dataset, which combines the full planning corpus, geocoded site-level variables, flood-risk spatial joins, and manually validated labels. These restricted data are not publicly redistributed in this repository.

## Data availability

This repository provides code, a small demo input file, and an expected demo output file for transparency and review. The full planning-application corpus, geocoded application-level dataset, flood-risk spatial joins, and manually coded validation labels are not publicly redistributed here.

## Citation

If using or referring to this code, please cite the associated manuscript:

```text
Wu, Y. and Han, F. (2026). Compliance costs constrain climate-adaptive housing supply in flood-exposed cities.
Working paper.
```

## License

This repository is released under the MIT License.
