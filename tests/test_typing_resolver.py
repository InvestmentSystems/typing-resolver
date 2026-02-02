import typing as tp
from pathlib import Path

import pytest

from src.typing_resolver._typing_resolver import (AmbiguousImportError,
                                                  _get_import_namespace,
                                                  _ImportSniffer,
                                                  get_type_hints)
from tests import non_top_level_imports
from tests.base_class import BaseClass
from tests.class_with_ambigious_imports import AmbigiousImportsClass
from tests.derived_class import DerivedClass
from tests.final_class import FinalClass
from tests.mixin_class import MixinClass
from tests.module_with_relative_import import (
    ClassWithRelativeImportHint,
    ClassWithRelativeImportHintAndTYPE_CHECKINGHint, SpecialType)
from tests.objects import Color, Point, Rectangle


def test_get_import_namespace_ambiguous_import() -> None:
    with pytest.raises(AmbiguousImportError):
        _get_import_namespace(AmbigiousImportsClass)


def test_get_import_namespace_nothing_to_do() -> None:
    ns = _get_import_namespace(DerivedClass)
    assert ns["BaseClass"] is BaseClass


def test_get_import_namespace_non_top_level_imports() -> None:
    ns = _get_import_namespace(non_top_level_imports.Class)
    assert "DerivedClass" not in ns

    og = _ImportSniffer.NODES_WITH_RUNTIME_SCOPE_NOT_EXECUTED_AT_IMPORT
    try:
        _ImportSniffer.NODES_WITH_RUNTIME_SCOPE_NOT_EXECUTED_AT_IMPORT = ()
        ns = _get_import_namespace(non_top_level_imports.Class)
        assert ns["DerivedClass"] is DerivedClass
    finally:
        _ImportSniffer.NODES_WITH_RUNTIME_SCOPE_NOT_EXECUTED_AT_IMPORT = og


def test_get_type_hints_a() -> None:
    t1 = get_type_hints(BaseClass)
    t2 = get_type_hints(DerivedClass)
    t3 = get_type_hints(MixinClass)
    t4 = get_type_hints(FinalClass)

    assert t1 == dict(age=int, name=str, color=Color)
    assert t2 == dict(
        age=int,
        name=str,
        color=Color | str,
        derived_attr_a=bool | None,
        derived_attr_b=float,
    )
    assert t3 == dict(mixin_a=int, mixin_b=Point, mixin_c=list[str])
    assert t4 == dict(
        age=int,
        name=str,
        color=Color | str,
        derived_attr_a=bool | None,
        derived_attr_b=int | None,
        mixin_a=int,
        mixin_b=Point,
        mixin_c=list[str],
        rectangle=Rectangle,
        final_attr=dict[str, float] | Point,
    )


def test_get_type_hints_ambiguous_import() -> None:
    with pytest.raises(AmbiguousImportError):
        get_type_hints(AmbigiousImportsClass)


def test_get_type_hints_relative_imports() -> None:
    assert ClassWithRelativeImportHintAndTYPE_CHECKINGHint.__annotations__ == dict(
        unique_to_another="SpecialType", file_path="Path"
    )
    assert ClassWithRelativeImportHint.__annotations__ == dict(
        unique_to_another="SpecialType", file_path="pathlib.Path"
    )

    with pytest.raises(NameError, match="Path"):
        get_type_hints(ClassWithRelativeImportHintAndTYPE_CHECKINGHint)

    with pytest.raises(NameError, match="Path"):
        tp.get_type_hints(ClassWithRelativeImportHintAndTYPE_CHECKINGHint)

    hints1 = get_type_hints(ClassWithRelativeImportHint)
    hints2 = tp.get_type_hints(ClassWithRelativeImportHint)

    assert hints1 == hints2 == dict(unique_to_another=SpecialType, file_path=Path)
