from tests.derived_class import BaseClass  # noqa: F401
from tests.derived_class import DerivedClass

class AmbigiousImportsClass(DerivedClass):
    """
    Note that even though BaseClass is not used, when we discover it, the name
    'BaseClass' is related to a module that is different from the module of
    'BaseClass' that was defined in DerivedClass's source module.
    """
