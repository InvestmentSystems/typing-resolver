from tests.derived_class import DerivedClass
from tests.mixin_class import MixinClass
from tests.objects import Rectangle, Point


class FinalClass(DerivedClass, MixinClass):
    rectangle: Rectangle
    derived_attr_b: int | None
    final_attr: dict[str, float] | Point
