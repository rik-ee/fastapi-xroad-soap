#
#   European Union Public License 1.2
#
#   Copyright (c) 2024, Centre of Registers and Information Systems
#
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#
#   SPDX-License-Identifier: EUPL-1.2
#
import functools
from typing import Union
from pathlib import Path


__all__ = ["search_upwards", "read_cached_file"]


@functools.lru_cache(maxsize=None)
def search_upwards(
        for_path: Union[Path, str],
        from_path: Union[Path, str] = __file__
) -> Path:
    current = Path(from_path).resolve()
    while current != current.parent:
        new_path = current / for_path
        if new_path.exists():
            return new_path
        current = current.parent
    raise FileNotFoundError(for_path)


@functools.lru_cache(maxsize=None)
def read_cached_file(
        path: str,
        binary: bool = False,
        as_lines: bool = False,
        encoding: str = "UTF-8"
) -> Union[str, bytes]:
    mode = "rb" if binary else "r"
    path_obj = search_upwards(path)
    with path_obj.open(mode, encoding=encoding) as file:
        func = file.readlines if as_lines else file.read
        return func()
