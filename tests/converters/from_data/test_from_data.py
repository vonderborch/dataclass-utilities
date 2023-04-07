import pytest

from dataclass_utilities.converters import from_data
from ._common import MockDataclass, ParentMockDataclass, DictParentMockDataclass, ListParentMockDataclass


def test_from_data():
    data = {"a": 1, "b": None}

    assert MockDataclass(1, None) == from_data(MockDataclass, data)


def test_from_data_type_checking_not_enforced():
    data = {"a": "1", "b": 1}

    assert MockDataclass("1", 1) == from_data(MockDataclass, data)


def test_from_data_type_checking_enforced():
    data = {"a": "1", "b": 1}

    with pytest.raises(TypeError):
        from_data(MockDataclass, data, strict_typing=True)


def test_from_data_extra_fields_not_ignored():
    data = {"a": 1, "b": None, "d": "goodbye world!"}

    expected = MockDataclass(1, None)
    expected.__dict__["d"] = data["d"]

    actual = from_data(MockDataclass, data, ignore_extra_fields=False)
    assert expected.__dict__["d"] == actual.d
    assert expected.d == actual.d
    assert actual.DATACLASS_DYNAMIC_FIELDS == [("d", str)]


def test_from_data_extra_fields_not_ignored_multiple():
    data = {"a": 1, "b": None, "d": "goodbye world!", "e": [1, 2, 3]}

    expected = MockDataclass(1, None)
    expected.__dict__["d"] = data["d"]
    expected.__dict__["e"] = data["e"]

    actual = from_data(MockDataclass, data, ignore_extra_fields=False)
    assert expected.__dict__["d"] == actual.d
    assert expected.__dict__["e"] == actual.e
    assert expected.d == actual.d
    assert expected.e == actual.e
    assert actual.DATACLASS_DYNAMIC_FIELDS == [("d", str), ("e", list)]


def test_from_data_nesting_support():
    data = {"a": 0, "child": {"a": 1, "b": "1"}}

    assert ParentMockDataclass(0, MockDataclass(1, "1")) == from_data(ParentMockDataclass, data)


def test_from_data_dict_nesting_support():
    data = {"a": 0, "child": {"1": {"a": 1, "b": "1"}}}

    assert DictParentMockDataclass(0, {"1": MockDataclass(1, "1")}) == from_data(DictParentMockDataclass, data)


def test_from_data_dict_nesting_support_strict():
    data = {"a": 0, "child": {"1": {"a": 1, "b": 1}}}

    with pytest.raises(TypeError):
        from_data(DictParentMockDataclass, data, strict_typing=True)


def test_from_data_list_nesting_support():
    data = {"a": 0, "child": [{"a": 1, "b": "1"}]}

    assert ListParentMockDataclass(0, [MockDataclass(1, "1")]) == from_data(ListParentMockDataclass, data)


def test_from_data_list_nesting_support_strict():
    data = {"a": 0, "child": [{"a": 1, "b": 1}]}

    with pytest.raises(TypeError):
        from_data(ListParentMockDataclass, data, strict_typing=True)
