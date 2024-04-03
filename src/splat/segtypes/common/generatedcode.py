import struct
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...util import options, log

from ..common.codesubsegment import CommonSegCodeSubsegment


class CommonSegGeneratedCode(CommonSegCodeSubsegment):
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
        self.data_only = isinstance(yaml, dict) and yaml.get("data_only", False)

    def get_data_type(self) -> str:
        return ""

    def is_array(self) -> bool:
        return False

    def format_sym_name(self, sym) -> str:
        return sym.name

    def get_linker_section(self) -> str:
        return ".data"

    def out_type(self) -> str:
        return ""

    def out_path(self) -> Path:
        return (
            options.opts.asset_path / self.dir / f"{self.name}.{self.out_type()}.inc.c"
        )

    def get_size_per(self) -> int:
        return 4

    def get_count(self) -> int | None:
        return None

    def scan(self, rom_bytes: bytes):
        assert isinstance(self.rom_start, int)
        assert isinstance(self.rom_end, int)

        self.data = rom_bytes[self.rom_start : self.rom_end]

    def get_body(self) -> List[str]:
        return []

    def check_length(self):
        pass

    def disassemble_data(self) -> str:
        lines = []
        if not self.data_only:
            lines.append(options.opts.generated_c_preamble)
            lines.append("")

        self.check_length()

        assert isinstance(self.vram_start, int)
        sym = self.create_symbol(
            addr=self.vram_start,
            in_segment=True,
            type="data",
            define=True,
            size=len(self.data),
        )

        if not self.data_only:
            decl_head = f"{self.get_data_type()} {self.format_sym_name(sym)}"
            if self.is_array():
                count = self.get_count()
                if count is not None:
                    decl_head += f"[{self.get_count()}] = {{"
                else:
                    decl_head += "[] = {"
            else:
                decl_head += " = "
            lines.append(decl_head)

        body = self.get_body()
        # paste at end of the declaration header with the first line of the body
        if not self.is_array():
            lines[-1] += body[0]
            body.pop(0)
        lines.extend(body)

        if not self.data_only:
            if self.is_array():
                lines.append("};")
            else:
                lines[-1] += ";"

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
        return options.opts.is_mode_active(self.type)

    def should_split(self) -> bool:
        return self.extract and options.opts.is_mode_active(self.type)
