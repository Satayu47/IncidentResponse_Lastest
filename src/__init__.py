# src/__init__.py
"""
Phase-1 incident classification and entity extraction modules.
"""

from .llm_adapter import LLMAdapter
from .extractor import SecurityExtractor, ExtractedEntities
from .dialogue_state import DialogueState, Turn
from .explicit_detector import ExplicitDetector
from .classification_rules import ClassificationRules
from .nvd import NVDClient
from .lc_retriever import KnowledgeBaseRetriever
from .owasp_display import (
    get_owasp_display_name,
    get_owasp_description,
    format_confidence_badge,
)

__all__ = [
    "LLMAdapter",
    "SecurityExtractor",
    "ExtractedEntities",
    "DialogueState",
    "Turn",
    "ExplicitDetector",
    "ClassificationRules",
    "NVDClient",
    "KnowledgeBaseRetriever",
    "get_owasp_display_name",
    "get_owasp_description",
    "format_confidence_badge",
]
