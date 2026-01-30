__version__ = "0.1.0"

from ._typing_resolver import get_type_hints, AmbiguousImportError

__all__ = ["get_type_hints", "AmbiguousImportError", "__version__"]
