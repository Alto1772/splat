"""
N64 Vtx struct splitter
Dumps out Vtx as a .inc.c file.

Originally written by Mark Street (https://github.com/mkst)
"""

import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.generatedcode import CommonSegGeneratedCode


class N64SegVtx(CommonSegGeneratedCode):
    def is_array(self) -> bool:
        return True

    def get_data_type(self) -> str:
        return "Vtx"

    def out_type(self) -> str:
        return "vtx"

    def get_size_per(self) -> int:
        return 16

    def get_count(self) -> int | None:
        return len(self.data) // self.get_size_per()

    def check_length(self):
        segment_length = len(self.data)

        if segment_length % 16 != 0:
            log.error(
                f"Error: Vtx segment {self.name} length ({segment_length}) is not a multiple of 16!"
            )

    def get_body(self) -> List[str]:
        lines = []

        for vtx in struct.iter_unpack(">hhhHhhBBBB", self.data):
            x, y, z, flg, t, c, r, g, b, a = vtx
            vtx_string = f"    {{{{{{ {x:5}, {y:5}, {z:5} }}, {flg}, {{ {t:5}, {c:5} }}, {{ {r:3}, {g:3}, {b:3}, {a:3} }}}}}},"
            if flg != 0:
                self.warn(f"Non-zero flag found in vertex data {self.name}!")
            lines.append(vtx_string)

        return lines

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        if isinstance(yaml, dict) and "length" in yaml:
            return yaml["length"] * 0x10
        return None
