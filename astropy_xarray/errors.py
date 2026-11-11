# Copyright 2014-2024, xarray developers
# Copyright 2025, Callan Gray

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

if sys.version_info >= (3, 13, 0):
    from builtins import ExceptionGroup
else:
    from exceptiongroup import ExceptionGroup
from collections.abc import Hashable
from typing import Any


def format_error_message(mapping, op):
    sep = "\n    " if len(mapping) == 1 else "\n -- "
    if op == "attach":
        message = "Cannot attach units:"
        message = sep.join(
            [message]
            + [
                f"cannot attach units to variable {key!r}: {unit} (reason: {str(e)})"
                for key, (unit, e) in mapping.items()
            ]
        )
    elif op == "parse":
        message = "Cannot parse units:"
        message = sep.join(
            [message]
            + [
                f"invalid units for variable {key!r}: {unit} ({type}) (reason: {str(e)})"
                for key, (unit, type, e) in mapping.items()
            ]
        )
    elif op == "convert":
        message = "Cannot convert variables:"
        message = sep.join(
            [message]
            + [
                f"incompatible units for variable {key!r}: {error}"
                for key, error in mapping.items()
            ]
        )
    elif op == "convert_indexers":
        message = "Cannot convert indexers:"
        message = sep.join(
            [message]
            + [
                f"incompatible units for indexer for {key!r}: {error}"
                for key, error in mapping.items()
            ]
        )
    else:
        raise ValueError("invalid op")

    return message


class AstropyExceptionGroup(ExceptionGroup, ValueError):
    """Exception group for errors related to unit operations

    Raised whenever there's the possibility of multiple errors.
    """

    pass


def _add_note_310(exc: Exception, note: str) -> Exception:
    """Exception add_note backwards compatibility for python 3.10"""
    if hasattr(exc, "add_note"):
        exc.add_note(note)
    elif exc.args:
        exc.args = (f"{exc.args[0]}\n{note}", *exc.args[1:])
    else:
        exc.args = (note,)
    return exc


def create_exception_group(mapping: dict[Hashable, Any], op: str) -> ExceptionGroup:
    match op:
        case "attach":
            message = "Cannot attach units"
            errors = [
                _add_note_310(e, f"cannot attach units to variable {key!r}: {unit}")
                for key, (unit, e) in mapping.items()
            ]
        case "parse":
            message = "Cannot parse units"
            errors = [
                _add_note_310(e, f"invalid units for variable {key!r}: {unit} ({type})")
                for key, (unit, type, e) in mapping.items()
            ]
        case "convert":
            message = "Cannot convert variables"
            errors = [
                _add_note_310(e, f"incompatible units for variable {key!r}")
                for key, e in mapping.items()
            ]
        case "convert_indexers":
            message = "Cannot convert indexers"
            errors = [
                _add_note_310(e, f"incompatible units for indexer for {key!r}")
                for key, e in mapping.items()
            ]
        case _:  # pragma: no cover
            raise ValueError("invalid op")

    return AstropyExceptionGroup(message, errors)
