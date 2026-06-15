"""
PlanRAG: Retrieval-augmented language-model pipeline for extracting
structured development attributes from planning permission text.

Example:
    >>> from planrag import run_pipeline
    >>> run_pipeline(
    ...     input_csv="data/demo_input.csv",
    ...     output_csv="data/demo_output.csv",
    ...     use_cache=True,
    ... )
"""

from planrag.pipeline import run_pipeline
from planrag.retrieval import retrieve
from planrag.classifier import classify

__version__ = "1.0.0"
__all__ = ["run_pipeline", "retrieve", "classify"]
