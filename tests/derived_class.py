from tests.base_class import BaseClass
from tests.objects import Color

class DerivedClass(BaseClass):
    color: Color | str
    derived_attr_a: bool | None
    derived_attr_b: float
