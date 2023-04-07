from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional

from timeit import default_timer
from dataclass_utilities.converters import from_data
from ._common import MockDataclass, ParentMockDataclass, DictParentMockDataclass, ListParentMockDataclass


MAX_TIME_TO_CONVERT: Dict[str, int] = {
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
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data"]
    data = {"a": 1, "b": None}

    for batch_size in BATCHES:
        for i in range(batch_size):
            start = default_timer()
            _ = from_data(MockDataclass, data)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_extra_fields_not_ignored():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_extra_fields_not_ignored"]
    data = {"a": 1, "b": None, "d": "goodbye world!"}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(MockDataclass, data, ignore_extra_fields=False)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_extra_fields_not_ignored_multiple():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_extra_fields_not_ignored_multiple"]
    data = {"a": 1, "b": None, "d": "goodbye world!", "e": [1, 2, 3]}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(MockDataclass, data, ignore_extra_fields=False)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_type_checking_not_enforced():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_type_checking_not_enforced"]
    data = {"a": "1", "b": 1}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(MockDataclass, data, strict_typing=False)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_nesting_support():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_nesting_support"]
    data = {"a": 0, "child": {"a": 1, "b": "1"}}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(ParentMockDataclass, data)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_dict_nesting_support():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_dict_nesting_support"]
    data = {"a": 0, "child": {"1": {"a": 1, "b": "1"}}}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(DictParentMockDataclass, data)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time


def test_from_data_list_nesting_support():
    time_to_convert = MAX_TIME_TO_CONVERT["test_from_data_list_nesting_support"]
    data = {"a": 0, "child": [{"a": 1, "b": "1"}]}

    for batch_size in BATCHES:
        for _ in range(batch_size):
            start = default_timer()
            __ = from_data(ListParentMockDataclass, data)
            actual_time = default_timer() - start
            assert time_to_convert > actual_time
