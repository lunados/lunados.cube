"""VP-08 Sequence Views (P2-VP-SEQUENCE/0.8.0). Additive to the frozen P2-VP/1.0.0-rc1 facade and VP-07."""
from .common import PROFILE, VP08Error
from .source import validate_source
from .sequence import SequencePrinter, render_sequence
from .panels import print_panels, check_panels

__all__ = ['PROFILE', 'VP08Error', 'validate_source', 'SequencePrinter', 'render_sequence', 'print_panels', 'check_panels']
