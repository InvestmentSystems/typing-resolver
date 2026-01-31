import typing as tp
import dataclasses
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


@dataclasses.dataclass
class Point:
    x: float
    y: float


class Rectangle(tp.NamedTuple):
    width: float
    height: float
