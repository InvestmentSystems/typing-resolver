__version__ = "0.1.0"

from ._typing_resolver import AmbiguousImportError, get_type_hints

__all__ = ["get_type_hints", "AmbiguousImportError", "__version__"]
