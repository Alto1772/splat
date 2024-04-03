"""
N64 f3dex display list splitter
Dumps out Gfx[] as a .inc.c file.
"""

import re
from typing import Dict, List, Optional, Union

from pathlib import Path

from pygfxd import (
    gfxd_buffer_to_string,
    gfxd_cimg_callback,
    gfxd_dl_callback,
    gfxd_endian,
    gfxd_execute,
    gfxd_input_buffer,
    gfxd_light_callback,
    gfxd_lightsn_callback,
    gfxd_lookat_callback,
    gfxd_macro_dflt,
    gfxd_macro_fn,
    gfxd_mtx_callback,
    gfxd_output_buffer,
    gfxd_printf,
    gfxd_puts,
    gfxd_target,
    gfxd_timg_callback,
    gfxd_tlut_callback,
    gfxd_vp_callback,
    gfxd_vtx_callback,
    gfxd_zimg_callback,
    GfxdEndian,
    gfxd_f3d,
    gfxd_f3db,
    gfxd_f3dex,
    gfxd_f3dexb,
    gfxd_f3dex2,
)
from ..segment import Segment

from ...util import log, options
from ...util.log import error

from ...util import symbols

from ..common.generatedcode import CommonSegGeneratedCode


class N64SegGfx(CommonSegGeneratedCode):
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
        self.in_segment = not isinstance(yaml, dict) or yaml.get("in_segment", True)

    def is_array(self) -> bool:
        return True

    def get_data_type(self) -> str:
        return "Gfx"

    def out_type(self) -> str:
        return "gfx"

    def get_size_per(self) -> int:
        return 8

    def check_length(self):
        segment_length = len(self.data)

        if segment_length % 8 != 0:
            log.error(
                f"Error: gfx segment {self.name} length ({segment_length}) is not a multiple of 8!"
            )

    def get_gfxd_target(self):
        opt = options.opts.gfx_ucode

        if opt == "f3d":
            return gfxd_f3d
        elif opt == "f3db":
            return gfxd_f3db
        elif opt == "f3dex":
            return gfxd_f3dex
        elif opt == "f3dexb":
            return gfxd_f3dexb
        elif opt == "f3dex2":
            return gfxd_f3dex2
        else:
            log.error(f"Unknown target {opt}")

    def tlut_handler(self, addr, idx, count):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def timg_handler(self, addr, fmt, size, width, height, pal):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def cimg_handler(self, addr, fmt, size, width):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def zimg_handler(self, addr):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def dl_handler(self, addr):
        # Look for 'Gfx'-typed symbols first
        sym = self.retrieve_sym_type(symbols.all_symbols_dict, addr, "Gfx")

        if not sym:
            sym = self.create_symbol(
                addr=addr, in_segment=self.in_segment, type="data", reference=True
            )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def mtx_handler(self, addr):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(f"&{self.format_sym_name(sym)}")
        return 1

    def lookat_handler(self, addr, count):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def light_handler(self, addr):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def lightsn_handler(self, addr, count):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(self.format_sym_name(sym))
        return 1

    def vtx_handler(self, addr, count):
        # Look for 'Vtx'-typed symbols first
        sym = self.retrieve_sym_type(symbols.all_symbols_dict, addr, "Vtx")

        if not sym:
            sym = self.create_symbol(
                addr=addr,
                in_segment=self.in_segment,
                type="Vtx",
                size=count * 16,
                reference=True,
                search_ranges=True,
            )

        index = int((addr - sym.vram_start) / 0x10)
        gfxd_printf(f"&{self.format_sym_name(sym)}[{index}]")
        return 1

    def vp_handler(self, addr):
        sym = self.create_symbol(
            addr=addr, in_segment=self.in_segment, type="data", reference=True
        )
        gfxd_printf(f"&{self.format_sym_name(sym)}")
        return 1

    def macro_fn(self):
        gfxd_puts("    ")
        gfxd_macro_dflt()
        gfxd_puts(",\n")
        return 0

    def get_body(self) -> List[str]:
        gfxd_input_buffer(self.data)

        # TODO terrible guess at the size we'll need - improve this
        outb = bytes([0] * len(self.data) * 100)
        outbuf = gfxd_output_buffer(outb, len(outb))

        gfxd_target(self.get_gfxd_target())
        gfxd_endian(
            GfxdEndian.big if options.opts.endianness == "big" else GfxdEndian.little, 4
        )

        # Callbacks
        gfxd_macro_fn(self.macro_fn)

        gfxd_tlut_callback(self.tlut_handler)
        gfxd_timg_callback(self.timg_handler)
        gfxd_cimg_callback(self.cimg_handler)
        gfxd_zimg_callback(self.zimg_handler)
        gfxd_dl_callback(self.dl_handler)
        gfxd_mtx_callback(self.mtx_handler)
        gfxd_lookat_callback(self.lookat_handler)
        gfxd_light_callback(self.light_handler)
        gfxd_lightsn_callback(self.lightsn_handler)
        # gfxd_seg_callback ?
        gfxd_vtx_callback(self.vtx_handler)
        gfxd_vp_callback(self.vp_handler)
        # gfxd_uctext_callback ?
        # gfxd_ucdata_callback ?
        # gfxd_dram_callback ?

        gfxd_execute()

        return [gfxd_buffer_to_string(outbuf).rstrip("\n")]

    @staticmethod
    def estimate_size(yaml: Union[Dict, List]) -> Optional[int]:
        if isinstance(yaml, dict) and "length" in yaml:
            return yaml["length"] * 0x10
        return None
