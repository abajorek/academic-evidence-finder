"""Core Academic Evidence Finder package."""

from .config_loader import UnsupportedConfigFormatError, load_rules_config
from .provenance import ProvenanceScorer

__all__ = ["ProvenanceScorer", "load_rules_config", "UnsupportedConfigFormatError"]
