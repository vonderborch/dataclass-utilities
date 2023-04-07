from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional

from timeit import default_timer
from dataclass_utilities.converters import from_data
from ._common import MockDataclass, ParentMockDataclass, DictParentMockDataclass, ListParentMockDataclass


DEFAULT_BATCH_SIZE = 100
MAX_TIME_FOR_DEFAULT_BATCH_SIZE: Dict[str, int] = {
    "test_from_data": 0.005,
    "test_from_data_extra_fields_not_ignored": 0.005,
    "test_from_data_extra_fields_not_ignored_multiple": 0.005,
    "test_from_data_type_checking_not_enforced": 0.005,
    "test_from_data_nesting_support": 0.005,
    "test_from_data_dict_nesting_support": 0.005,
    "test_from_data_list_nesting_support": 0.005,
}
BATCHES = [100, 500, 1000, 5000, 10000]


def test_from_data():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data"]
    data = {"a": 1, "b": None}

    expected = MockDataclass(1, None)

    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(MockDataclass, data)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time
        assert expected == actual


def test_from_data_extra_fields_not_ignored():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_extra_fields_not_ignored"]
    data = {"a": 1, "b": None, "d": "goodbye world!"}

    expected = MockDataclass(1, None)
    expected.__dict__["d"] = data["d"]

    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(MockDataclass, data, ignore_extra_fields=False)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time

    assert expected.__dict__["d"] == actual.d
    assert expected.d == actual.d
    assert actual.DATACLASS_DYNAMIC_FIELDS == [("d", str)]


def test_from_data_extra_fields_not_ignored_multiple():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_extra_fields_not_ignored_multiple"]
    data = {"a": 1, "b": None, "d": "goodbye world!", "e": [1, 2, 3]}

    expected = MockDataclass(1, None)
    expected.__dict__["d"] = data["d"]
    expected.__dict__["e"] = data["e"]

    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(MockDataclass, data, ignore_extra_fields=False)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time

    assert expected.__dict__["d"] == actual.d
    assert expected.__dict__["e"] == actual.e
    assert expected.d == actual.d
    assert expected.e == actual.e
    assert actual.DATACLASS_DYNAMIC_FIELDS == [("d", str), ("e", list)]


def test_from_data_type_checking_not_enforced():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_type_checking_not_enforced"]
    data = {"a": "1", "b": 1}

    expected = MockDataclass("1", 1)
    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(MockDataclass, data)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time
        assert expected == actual


def test_from_data_nesting_support():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_nesting_support"]
    data = {"a": 0, "child": {"a": 1, "b": "1"}}

    expected = ParentMockDataclass(0, MockDataclass(1, "1"))
    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(ParentMockDataclass, data)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time
        assert expected == actual


def test_from_data_dict_nesting_support():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_dict_nesting_support"]
    data = {"a": 0, "child": {"1": {"a": 1, "b": "1"}}}

    expected = DictParentMockDataclass(0, {"1": MockDataclass(1, "1")})
    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(DictParentMockDataclass, data)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time
        assert expected == actual


def test_from_data_list_nesting_support():
    default_time = MAX_TIME_FOR_DEFAULT_BATCH_SIZE["test_from_data_list_nesting_support"]
    data = {"a": 0, "child": [{"a": 1, "b": "1"}]}

    expected = ListParentMockDataclass(0, [MockDataclass(1, "1")])
    for batch_size in BATCHES:
        start = default_timer()
        for _ in range(batch_size):
            actual = from_data(ListParentMockDataclass, data)
        actual_time = default_timer() - start

        expected_time = default_time * (batch_size / DEFAULT_BATCH_SIZE)
        assert expected_time > actual_time
        assert expected == actual
