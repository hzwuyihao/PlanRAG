import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)
LLM_MODEL_NAME = "gpt-4o"
LLM_TEMPERATURE = 0.0        # deterministic generation
LLM_MAX_OUTPUT_TOKENS = 800
LLM_REQUEST_TIMEOUT = 60     # seconds


def classify(
    description: str,
    context: str,
    schema: dict,
    system_prompt: str,
    application_reference: str,
    cache: dict,
    use_cache: bool = True,
) -> dict:
  
    if use_cache:
        if application_reference not in cache:
            raise KeyError(
                f"Application reference '{application_reference}' not "
                "found in the LLM response cache. To classify "
                "applications outside the cached set, run with "
                "use_cache=False and provide an OpenAI API key."
            )
        raw_response = cache[application_reference]
    else:
        prompt = _build_prompt(description, context, schema)
        raw_response = _call_llm(system_prompt, prompt)

    classification = _parse_response(raw_response, schema)
    return classification

def _build_prompt(description: str, context: str, schema: dict) -> str:
    
    return prompt


# ---------------------------------------------------------------------------
# Language model call
# ---------------------------------------------------------------------------

def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call the OpenAI API and return the raw response text.

    Reads the API key from the OPENAI_API_KEY environment variable.
    Requires the `openai` Python package; not imported at module level
    to keep the import-time cost low for cache-only usage.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable not set. Either set "
            "the variable or run with use_cache=True to use cached "
            "responses."
        )

    from openai import OpenAI
    client = OpenAI(api_key=api_key, timeout=LLM_REQUEST_TIMEOUT)

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Response parsing and validation
# ---------------------------------------------------------------------------

def _parse_response(raw_response: str, schema: dict) -> dict:
    """
    Parse the LLM's raw response into a structured classification.

    Validates that the response is valid JSON and contains every
    expected field from the schema. Missing fields are filled with
    None and logged; unexpected fields are retained but flagged.
    """
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model response is not valid JSON: {e}\n"
            f"Raw response: {raw_response[:500]}"
        )

    expected_fields = set(schema.get("categories", {}).keys())
    received_fields = set(parsed.keys()) - {"chain_of_thought"}

    missing = expected_fields - received_fields
    extra = received_fields - expected_fields

    if missing:
        logger.warning(
            f"LLM response missing expected fields: {missing}. "
            "Filling with None."
        )
        for field in missing:
            parsed[field] = None
    if extra:
        logger.warning(f"LLM response contains unexpected fields: {extra}.")

    return parsed
