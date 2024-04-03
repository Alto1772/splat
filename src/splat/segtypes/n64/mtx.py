import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.generatedcode import CommonSegGeneratedCode


class N64SegMtx(CommonSegGeneratedCode):
    def get_size_per(self) -> int:
        return 0x40

    def get_data_type(self) -> str:
        return "Mtx"

    def out_type(self) -> str:
        return "mtx"

    def check_length(self):
        segment_length = len(self.data)
        if segment_length != 0x40:
            log.error(
                f"Error: Mtx segment {self.name} expected to be length of 0x40, got 0x{segment_length:X}."
            )

    def get_body(self) -> str:
        lines = []

        lines.append(f"{{{{")
        for m1, m2, m3, m4 in struct.iter_unpack(">4I", self.data):
            lines.append(f"    {{ 0x{m1:08X}, 0x{m2:08X}, 0x{m3:08X}, 0x{m4:08X} }},")
        lines.append("}};")

        return lines

    def should_scan(self) -> bool:
        return options.opts.is_mode_active("mtx")

    def should_split(self) -> bool:
        return self.extract and options.opts.is_mode_active("mtx")

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        return 0x40
