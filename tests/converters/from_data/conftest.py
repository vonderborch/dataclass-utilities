#   ---------------------------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""
This is a configuration file for pytest containing customizations and fixtures.

In VSCode, Code Coverage is recorded in config.xml. Delete this file to reset reporting.
"""

from dataclass_utilities.converters.from_data import cache_dataclass_metadata, get_or_cache_dynamic_dataclass
from ._common import MockDataclass, ParentMockDataclass, DictParentMockDataclass, ListParentMockDataclass

# pre-cache dataclass metadata to make performance tests more reliable
cache_dataclass_metadata(MockDataclass)
cache_dataclass_metadata(ParentMockDataclass)
cache_dataclass_metadata(DictParentMockDataclass)
cache_dataclass_metadata(ListParentMockDataclass)

get_or_cache_dynamic_dataclass(MockDataclass, [("d", str)])
get_or_cache_dynamic_dataclass(MockDataclass, [("d", str), ("e", list)])
