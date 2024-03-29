import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.codesubsegment import CommonSegCodeSubsegment


class N64SegMtx(CommonSegCodeSubsegment):
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
        return options.opts.asset_path / self.dir / f"{self.name}.mtx.inc.c"

    def scan(self, rom_bytes: bytes):
        assert isinstance(self.vram_start, int)
        assert isinstance(self.rom_start, int)

        self.data = rom_bytes[self.rom_start : self.rom_end]

    def disassemble_data(self) -> str:
        assert isinstance(self.rom_end, int)

        mtx_data = self.data
        if len(mtx_data) != 0x40:
            log.error(
                f"Error: Mtx segment {self.name} expected to be length of 0x40, got 0x{len(mtx_data):X}."
            )

        lines = []

        lines.append(options.opts.generated_c_preamble)
        lines.append("")

        sym = self.create_symbol(
            addr=self.vram_start, in_segment=True, type="data", define=True
        )

        lines.append(f"Mtx {self.format_sym_name(sym)} = {{{{")
        for m1, m2, m3, m4 in struct.iter_unpack(">4I", mtx_data):
            lines.append(f"    {{ 0x{m1:08X}, 0x{m2:08X}, 0x{m3:08X}, 0x{m4:08X} }},")
        lines.append("}};")

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
        return options.opts.is_mode_active("mtx")

    def should_split(self) -> bool:
        return self.extract and options.opts.is_mode_active("mtx")

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        return 0x18
