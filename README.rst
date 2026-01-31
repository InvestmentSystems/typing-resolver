.. image:: https://img.shields.io/pypi/pyversions/typing-resolver.svg
  :target: https://pypi.org/project/typing-resolver

.. image:: https://img.shields.io/pypi/v/typing-resolver.svg
  :target: https://pypi.org/project/typing-resolver

.. image:: https://img.shields.io/codecov/c/github/InvestmentSystems/typing-resolver.svg
  :target: https://codecov.io/gh/InvestmentSystems/typing-resolver

.. image:: https://img.shields.io/github/workflow/status/InvestmentSystems/typing-resolver/Test?label=tests&logo=Github
  :target: https://github.com/InvestmentSystems/typing-resolver/actions?query=workflow%3ATest

.. image:: https://img.shields.io/pypi/status/typing-resolver.svg
  :target: https://pypi.org/project/typing-resolver

Overview
========

typing-resolver provides a more helpful alternative to ``typing.get_type_hints()`` by resolving type annotations using a reconstructed import namespace. It is intended for codebases that rely on ``TYPE_CHECKING`` imports, conditional imports, or inherited annotations that might not be present at runtime.

Problem
=======

``typing.get_type_hints()`` evaluates annotations in a limited namespace. If an annotation references a name that is not imported at runtime (for example, under ``if TYPE_CHECKING:``), resolution fails with ``NameError``.

Solution
========

This package rebuilds a local namespace by collecting ALL import statements from inside ALL module(s) in an type object's MRO and uses that namespace when resolving type hints.
