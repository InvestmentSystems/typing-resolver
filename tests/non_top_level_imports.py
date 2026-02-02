class Class:
    pass


def func() -> str:
    from tests.derived_class import DerivedClass

    return str(DerivedClass)
