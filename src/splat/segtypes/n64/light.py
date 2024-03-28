import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.codesubsegment import CommonSegCodeSubsegment

# TODO: support other light structures (Lights0, Lights1..7, LookAt)


class N64SegLight(CommonSegCodeSubsegment):
    def __init__(
        self,
        rom_start: Optional[int],
        rom_end: Optional[int],
        type: str,
        name: str,
        vram_start: Optional[int],
        args: list,
        yaml,
    ):
        super().__init__(
            rom_start,
            rom_end,
            type,
            name,
            vram_start,
            args=args,
            yaml=yaml,
        )
        self.data = None
        self.file_text: Optional[str] = None

    def format_sym_name(self, sym) -> str:
        return sym.name

    def get_linker_section(self) -> str:
        return ".data"

    def out_path(self) -> Path:
        return options.opts.asset_path / self.dir / f"{self.name}.light.inc.c"

    def scan(self, rom_bytes: bytes):
        assert isinstance(self.vram_start, int)
        assert isinstance(self.rom_start, int)

        self.data = rom_bytes[self.rom_start : self.rom_end]

    def disassemble_data(self) -> str:
        assert isinstance(self.rom_end, int)

        light_data = self.data
        if len(light_data) < 0x14 or len(light_data) > 0x20:
            log.error(
                f"Error: Light segment {self.name} expected to be length of 0x14, got 0x{len(light_data):X}."
            )

        lines = []

        lines.append(options.opts.generated_c_preamble)
        lines.append("")

        sym = self.create_symbol(
            addr=self.vram_start, in_segment=True, type="data", define=True
        )

        lines.append(f"Lights1 {self.format_sym_name(sym)} = gdSPDefLights1(")

        (
            acolr,
            acolg,
            acolb,
            lcolr,
            lcolg,
            lcolb,
            lcolx,
            lcoly,
            lcolz,
        ) = struct.unpack(">3Bx4x 3Bx4x3Bx", light_data[:0x14])
        lines.append(f"    0x{acolr:02x}, 0x{acolg:02x}, 0x{acolb:02x},")
        lines.append(
            f"    0x{lcolr:02x}, 0x{lcolg:02x}, 0x{lcolb:02x}, 0x{lcolx:02x}, 0x{lcoly:02x}, 0x{lcolz:02x}"
        )

        lines.append(");")

        # enforce newline at end of file
        lines.append("")
        return "\n".join(lines)

    def split(self, rom_bytes: bytes):
        self.file_text = self.disassemble_data()

    def write(self):
        if self.file_text and self.out_path():
            self.out_path().parent.mkdir(parents=True, exist_ok=True)

            with open(self.out_path(), "w", newline="\n") as f:
                f.write(self.file_text)

    def should_scan(self) -> bool:
        return options.opts.is_mode_active("light")

    def should_split(self) -> bool:
        return self.extract and options.opts.is_mode_active("light")

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        return 0x18
