import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.generatedcode import CommonSegGeneratedCode

# TODO: support other light structures (Lights0, Lights1..7, LookAt)


class N64SegLight(CommonSegGeneratedCode):
    def get_size_per(self) -> int:
        return 0x18

    def get_data_type(self) -> str:
        return "Lights1"

    def out_type(self) -> str:
        return "light"

    def check_length(self):
        light_data = self.data
        if len(light_data) < 0x14 or len(light_data) > 0x20:
            log.error(
                f"Error: Light segment {self.name} expected to be length of 0x14, got 0x{len(light_data):X}."
            )

    def get_body(self) -> str:
        lines = []

        lines.append("gdSPDefLights1(")
        (
            acolr,
            acolg,
            acolb,
            lcolr,
            lcolg,
            lcolb,
            ldirx,
            ldiry,
            ldirz,
        ) = struct.unpack(">3Bx4x 3Bx4x3Bx", self.data[:0x14])
        lines.append(f"    0x{acolr:02x}, 0x{acolg:02x}, 0x{acolb:02x},")
        lines.append(
            f"    0x{lcolr:02x}, 0x{lcolg:02x}, 0x{lcolb:02x}, 0x{ldirx:02x}, 0x{ldiry:02x}, 0x{ldirz:02x}"
        )

        lines.append(")")

        return lines

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        return 0x18
