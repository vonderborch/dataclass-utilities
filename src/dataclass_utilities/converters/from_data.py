"""Converter for converting a string or dict into a dataclass."""

from dataclasses import Field, field, fields, is_dataclass, dataclass as dataclass_instance, make_dataclass
import json
from os import linesep
from typing import Any, Dict, List, Optional, Tuple, Union

from .._internal import Dataclass


def _has_dataclass(args: tuple) -> Any:
    dataclass_types: List[Dataclass] = []
    for arg in args:
        if is_dataclass(arg):
            dataclass_types.append(arg)
        elif hasattr(arg, "__args__"):
            dataclass_types.extend(_has_dataclass(arg.__args__))
    return dataclass_types


@dataclass_instance
class _InternalField:
    field_details: Field
    name: str = ""
    field_type: Any = None
    is_nullable: bool = False
    is_list: bool = False
    is_dict: bool = False
    child_dataclass_types: Optional[List[Dataclass]] = None

    def __post_init__(self) -> None:
        self.name = self.field_details.name if self.name == "" else self.name
        self.field_type = self.field_details.type if self.field_type is None else self.field_type

        if hasattr(self.field_type, "__args__"):
            self.is_nullable = type(None) in self.field_type.__args__
            self.is_list = any(
                [
                    (hint in (List, list) or (hasattr(hint, "_name") and hint._name.lower() == "list"))
                    for hint in self.field_type.__args__
                ]
            ) or (hasattr(self.field_type, "_name") and self.field_type._name.lower() == "list")
            self.is_dict = any(
                [
                    (hint in (Dict, dict) or (hasattr(hint, "_name") and hint._name.lower() == "dict"))
                    for hint in self.field_type.__args__
                ]
            ) or (hasattr(self.field_type, "_name") and self.field_type._name.lower() == "dict")

            if self.is_list or self.is_dict:
                self.child_dataclass_types = _has_dataclass(self.field_type.__args__)


def _convert_iterable(
    field_type: _InternalField,
    field_data: Dict[str, Any],
    strict_typing: bool,
    ignore_extra_fields: bool,
) -> Any:
    if field_type.is_dict and isinstance(field_data, dict):
        final_values: Dict[str, Dataclass] = {}
        for sub_name, sub_value in field_data.items():
            if sub_value is None:
                final_values[sub_name] = None
            else:
                failures: List[str] = []
                for dataclass_type in field_type.child_dataclass_types:
                    try:
                        final_values[sub_name] = from_data(
                            dataclass_type, sub_value, strict_typing, ignore_extra_fields
                        )
                        break
                    except TypeError as ex:
                        if strict_typing:
                            failures.append(str(ex))
                if sub_name not in final_values:
                    if strict_typing:
                        raise TypeError(linesep.join(failures))
                    final_values[sub_name] = sub_value
        return final_values
    elif field_type.is_list and isinstance(field_data, list):
        final_values: List[Dataclass] = []
        for sub_value in field_data:
            if sub_value is None:
                final_values.append(sub_value)
            else:
                success = False
                failures: List[str] = []
                for dataclass_type in field_type.child_dataclass_types:
                    try:
                        final_values.append(from_data(dataclass_type, sub_value, strict_typing, ignore_extra_fields))
                        success = True
                        break
                    except TypeError as ex:
                        if strict_typing:
                            failures.append(str(ex))
                if not success:
                    if strict_typing:
                        raise TypeError(linesep.join(failures))
                    final_values.append(sub_value)
        return final_values


# Stores field information on the specified dataclasses
_cached_dataclass_metadata: Dict[str, Dict[str, _InternalField]] = {}


def cache_dataclass_metadata(dataclass: Dataclass) -> None:
    """Caches field metadata on the specified dataclass.

    Args:
        dataclass (Dataclass): The dataclass type to cache field information on
    """
    _cached_dataclass_metadata[dataclass] = {field.name: _InternalField(field) for field in fields(dataclass)}


# Stores dynamic dataclasses (when extra fields are allowed)
_cached_dynamic_dataclasses: Dict[str, Dataclass] = {}


def get_or_cache_dynamic_dataclass(base_dataclass: Dataclass, extra_fields: List[Tuple[str, Any]]) -> Dataclass:
    """Returns or caches and returns a dynamic dataclass

    Args:
        base_dataclass (Dataclass): The base dataclass type to use for the dynamic dataclass
        extra_fields (List[Tuple[str, Any]]): A list of extra fields and types

    Returns:
        Dataclass: An updated dataclass definition
    """

    field_names = [field_name for field_name, _ in extra_fields]
    dynamic_class_name = f"{str(base_dataclass)}_{'-'.join(field_names)}"

    if dynamic_class_name not in _cached_dynamic_dataclasses:
        extra_field_definitions = [
            (
                field_name,
                field_type,
                field(init=False),
            )
            for field_name, field_type in extra_fields
        ]
        _cached_dynamic_dataclasses[dynamic_class_name] = make_dataclass(
            dynamic_class_name,
            fields=extra_field_definitions,
            bases=(base_dataclass,),
        )

        _cached_dynamic_dataclasses[dynamic_class_name].DATACLASS_DYNAMIC_FIELDS = extra_fields

    return _cached_dynamic_dataclasses[dynamic_class_name]


def from_data(
    dataclass: Dataclass,
    data: Union[Dict[str, Any], str],
    strict_typing: bool = False,
    ignore_extra_fields: bool = True,
) -> Dataclass:
    """Convert a json string or dict into a dataclass.

    Args:
        dataclass (Dataclass): The dataclass type to convert the data into
        data (Dict[str, Any] | str): The dictionary to convert to the dataclass or the json string to convert into the
            dataclass
        strict_typing (bool, Default False): Whether to enforce strict types when converting to the dataclass (True) or
            not (False)
        ignore_extra_fields (bool, Default True): Whether to ignore extra fields (True) or not (False). Extra fields are
            fields which are not defined in the dataclass.

    Returns:
        Dataclass: An instance of the dataclass object requested
    """
    if dataclass not in _cached_dataclass_metadata:
        cache_dataclass_metadata(dataclass)

    class_fields = _cached_dataclass_metadata[dataclass]
    actual_data: Dict[str, Any] = json.load(data) if isinstance(data, str) else data
    relevant_fields = {name: field_data for name, field_data in actual_data.items() if name in class_fields}

    # nested class support
    bad_typing: List[str] = []
    for name, field_data in relevant_fields.items():
        field_type: _InternalField = class_fields[name]
        if is_dataclass(field_type.field_type):
            relevant_fields[name] = from_data(field_type.field_type, field_data, strict_typing, ignore_extra_fields)
            continue
        # Convert iterables appropriately. Currently only supports lists and dicts
        if field_type.is_dict or field_type.is_list:
            relevant_fields[name] = _convert_iterable(field_type, field_data, strict_typing, ignore_extra_fields)
        if strict_typing and not isinstance(relevant_fields[name], field_type.field_type):
            bad_typing.append(
                f"Field data {relevant_fields[name]} does not match expected type {field_type.field_type} for field {name}."
            )

    if bad_typing:
        raise TypeError(linesep.join(bad_typing))

    instance = dataclass(**relevant_fields)

    if not ignore_extra_fields:
        extra_fields = {name: field_data for name, field_data in actual_data.items() if name not in class_fields}
        if extra_fields:
            extra_fields_names = sorted(extra_fields.keys())
            types_and_names = [(name, type(extra_fields[name])) for name in extra_fields_names]
            new_class_type = get_or_cache_dynamic_dataclass(dataclass, types_and_names)
            instance.__class__ = new_class_type
            for field_name, field_data in extra_fields.items():
                instance.__dict__[field_name] = field_data

    return instance
