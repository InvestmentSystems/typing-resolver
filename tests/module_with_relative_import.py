from __future__ import annotations

import pathlib
import typing as tp

from .base_class import BaseClass

if tp.TYPE_CHECKING:
    from pathlib import Path


class SpecialType:
    pass


class ClassWithRelativeImportHintAndTYPE_CHECKINGHint(BaseClass):
    unique_to_another: SpecialType
    file_path: Path


class ClassWithRelativeImportHint(BaseClass):
    unique_to_another: SpecialType
    file_path: pathlib.Path
