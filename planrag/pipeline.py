import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

from planrag.retrieval import retrieve
from planrag.classifier import classify

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

CACHE_PATH = DATA_DIR / "cached_llm_responses.json"
SCHEMA_PATH = PROMPTS_DIR / "classification_schema.json"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.txt"

TOP_K_RETRIEVAL = 50         
TOP_K_AFTER_RERANK = 8       
CONTEXT_WINDOW_TOKENS = 4000 

def _load_cache(cache_path: Path) -> dict:
    """Load the cached LLM responses keyed by application reference."""
    if not cache_path.exists():
        return {}
    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_schema(schema_path: Path) -> dict:
    """Load the classification schema (categorical labels and definitions)."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_system_prompt(prompt_path: Path) -> str:
    """Load the system prompt used to instruct the language model."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def run_pipeline(
    input_csv: str,
    output_csv: str,
    use_cache: bool = True,
    cache_path: Optional[Path] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    cache_path = cache_path or CACHE_PATH

    # ---- Load configuration and inputs -----------------------------------
    if verbose:
        logger.info("Loading inputs and configuration")

    df_input = pd.read_csv(input_csv)
    schema = _load_schema(SCHEMA_PATH)
    system_prompt = _load_system_prompt(SYSTEM_PROMPT_PATH)
    cache = _load_cache(cache_path) if use_cache else {}

    required_cols = {"application_reference", "description"}
    missing = required_cols - set(df_input.columns)
    if missing:
        raise ValueError(
            f"Input CSV is missing required columns: {missing}. "
            f"Found columns: {list(df_input.columns)}"
        )

    if verbose:
        logger.info(f"Processing {len(df_input)} applications "
                    f"(cache_enabled={use_cache})")

    # ---- Process each application ---------------------------------------
    classifications = []
    iterator = tqdm(df_input.itertuples(index=False), total=len(df_input)) \
        if verbose else df_input.itertuples(index=False)

    for row in iterator:
        ref = row.application_reference
        description = row.description

        # Stage 1: Retrieval
        retrieved_context = retrieve(
            query=description,
            top_k=TOP_K_RETRIEVAL,
            top_k_after_rerank=TOP_K_AFTER_RERANK,
            max_tokens=CONTEXT_WINDOW_TOKENS,
        )

        # Stage 2: Classification
        result = classify(
            description=description,
            context=retrieved_context,
            schema=schema,
            system_prompt=system_prompt,
            application_reference=ref,
            cache=cache,
            use_cache=use_cache,
        )

        # Stage 3: Output assembly
        classifications.append({"application_reference": ref, **result})

    # ---- Write output ---------------------------------------------------
    df_output = pd.DataFrame(classifications)
    df_output = df_input.merge(
        df_output, on="application_reference", how="left"
    )

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df_output.to_csv(output_csv, index=False)

    if verbose:
        logger.info(f"Wrote {len(df_output)} classifications to {output_csv}")

    return df_output
