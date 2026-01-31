from __future__ import annotations

import ast
import builtins
import importlib
import inspect
import typing as tp
from types import MappingProxyType


def _as_name(node: ast.alias) -> str:
    if node.asname:
        return f"{node.name} as {node.asname}"
    return node.name


class _Import(tp.NamedTuple):
    key: str
    """pathlib, Path, etc..."""

    stmt: str
    module: str
    bases: tuple[type, ...] = ()

    @classmethod
    def from_import_alias(cls, node: ast.alias) -> tp.Self:
        return cls(
            key=node.asname or node.name,
            stmt=f"import {_as_name(node)}",
            module=node.name,
        )

    @classmethod
    def from_import_from_alias(cls, node: ast.alias, from_module: str) -> tp.Self:
        return cls(
            key=node.asname or node.name,
            stmt=f"from {from_module} import {_as_name(node)}",
            module=from_module,
        )

    def add_base(self, base: type) -> tp.Self:
        return self._replace(bases=self.bases + (base,))


class _ImportSniffer(ast.NodeVisitor):

    # If one of these is removed in a future release of Python, we will need to
    # add future-handling. As of now, these nodes exist in all supported versions
    # of Python and are exceptionally unlikely to be removed.
    NODES_WITH_RUNTIME_SCOPE_NOT_EXECUTED_AT_IMPORT = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.Lambda,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )

    def __init__(self) -> None:
        super().__init__()
        self.imports: list[_Import] = []

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, self.NODES_WITH_RUNTIME_SCOPE_NOT_EXECUTED_AT_IMPORT):
            return

        super().visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.extend(map(_Import.from_import_alias, node.names))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        from_module = ("." * node.level) + (node.module or "")
        for name in node.names:
            self.imports.append(_Import.from_import_from_alias(name, from_module))

        self.generic_visit(node)


class AmbiguousImportError(RuntimeError):
    pass


class NamespaceConstructionError(RuntimeError):
    pass


def _get_import_namespace(obj: type) -> tp.Mapping[str, tp.Any]:
    # From examing the AST, find all import statements in the module of each base class
    statements: dict[str, _Import] = {}

    for base in reversed(obj.__mro__):
        module = importlib.import_module(base.__module__)

        # Cannot inspect source of builtins. Plus, we don't want private Python internal imports!
        if module is builtins:
            continue

        sniffer = _ImportSniffer()
        source = inspect.getsource(module)
        sniffer.visit(ast.parse(source))

        for import_ in sniffer.imports:
            import_ = import_.add_base(base)
            curr_import = statements.get(import_.key)

            if curr_import is None:
                statements[import_.key] = import_

            elif curr_import._replace(bases=()) == import_._replace(bases=()):
                statements[import_.key].add_base(base)

            else:
                raise AmbiguousImportError(
                    f"Ambiguous import for '{import_.key}'!\n"
                    f"  Existing: {curr_import.stmt} {tuple(b.__name__ for b in curr_import.bases)}\n"
                    f"  New:      {import_.stmt} {tuple(b.__name__ for b in import_.bases)}"
                    "\nPlease resolve the ambiguity by importing from the same place!"
                )

    to_exec = "\n".join(import_.stmt for import_ in statements.values())
    ns = {}
    try:
        exec(to_exec, ns)
    except NameError as e:
        raise NamespaceConstructionError(
            f"Failed to exec import statements for type '{obj.__name__}':\n{to_exec}"
        ) from e
    return MappingProxyType(ns)


def get_type_hints(obj: type) -> dict[str, tp.Any]:
    """
    Given a type, return its resolved typehints like ``tp.get_type_hints``, with
    the namesapce of mappable objects including ALL imports in the module, not
    just those that exist in the namespace of the imported object

    Example:

        import typing as tp

        if tp.TYPE_CHECKING:
            from some_module import SomeType

        class MyClass:
            my_attr: SomeType

        # This would fail because SomeType is not in the namespace
        tp.get_type_hints(MyClass)

        # This would work because SomeType is imported into the namespace
        assert get_type_hints(MyClass) == {'my_attr': SomeType}

    """
    try:
        localns = _get_import_namespace(obj)
    except AmbiguousImportError:
        raise
    except:  # pragma: no cover
        localns = None

    return tp.get_type_hints(obj=obj, globalns=None, localns=localns)
