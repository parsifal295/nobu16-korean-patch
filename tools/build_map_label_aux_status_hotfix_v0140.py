#!/usr/bin/env python3
"""Build the reviewed v0.14.0 auxiliary map-indicator alignment candidate.

Patch 006 already aligns the primary map status icon after the dynamically
sized horizontal castle-name plate.  This follow-up chains a small helper from
the existing 006 wrapper epilogue and fixes two independent children without
changing the published 006 definition:

* the battle-ready numeric child preserves its native 20-pixel horizontal
  offset from the moved primary status icon and is bottom-aligned to it; and
* the no-castle-lord warning (status ID 0x10DE5) is placed at the right edge of
  the rendered plate and vertically centered using its special 32-pixel image
  height stored at widget offset 0xA0.

The castle crest and the ordinary troop-count group below it remain untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_map_label_hotfix_v0121 as pe_tools
import build_map_label_status_icon_hotfix_v0131 as status_tools


EXPECTED_V0140_SHA256 = (
    "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF"
)
# Pinned after deterministic rebuild and before permanent installer QA.
EXPECTED_CANDIDATE_SHA256 = (
    "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D"
)

IMAGE_BASE = 0x140000000
TARGET_SIZE = 67_024_384
CODE_SECTION = ".mlbd"
EXPECTED_SECTION_VIRTUAL_SIZE = 35_275_522
EXPECTED_SECTION_RAW_SIZE = 35_275_776
IMAGE_SCN_MEM_EXECUTE = 0x20000000

EXISTING_006_WRAPPER_VA = 0x1447BF260
EXISTING_006_EPILOGUE_VA = 0x1447BF2FD
EXISTING_006_EPILOGUE_BEFORE = bytes.fromhex("48 83 C4 58 C3")

LABEL_PLATE_WIDGET_OFFSET = 0x140
PRIMARY_STATUS_WIDGET_OFFSET = 0x248
BATTLE_READY_NUMBER_WIDGET_OFFSET = 0x260
NO_CASTLE_LORD_WARNING_WIDGET_OFFSET = 0x270

PRIMARY_STATUS_NATIVE_X_BITS = 0x41F00000  # 30.0f
BATTLE_READY_NUMBER_NATIVE_X_BITS = 0x42480000  # 50.0f
BATTLE_READY_NUMBER_STATUS_X_OFFSET_BITS = 0x41A00000  # 20.0f = 50.0 - 30.0
NO_CASTLE_LORD_WARNING_NATIVE_X_BITS = 0x41E00000  # 28.0f
NO_CASTLE_LORD_WARNING_IMAGE_HEIGHT_OFFSET = 0xA0


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def build_injected_code(code_va: int) -> tuple[bytes, dict[str, int]]:
    """Return the helper entered before the 006 wrapper releases its frame."""
    code = status_tools.CodeBuilder(code_va)
    code.label("aux_alignment")

    # Patch 006 saved the label object at [rsp+0x40].  Its original epilogue is
    # replaced by a jump here, so the 0x58-byte frame is still live.
    code.emit("48 8B 4C 24 40")       # mov rcx, [rsp+0x40]
    code.emit("48 85 C9")             # test rcx, rcx
    code.branch32(0x84, "return")

    code.emit("48 8B 81 40 01 00 00") # mov rax, [rcx+0x140] (name plate)
    code.emit("48 85 C0")             # test rax, rax
    code.branch32(0x84, "number")

    # Status ID 0x10DE5 uses child +0x270.  Its ordinary width/height fields are
    # both zero; FUN_140F4A820 stores the actual 32px image height at +0xA0.
    code.emit("48 8B 91 70 02 00 00") # mov rdx, [rcx+0x270]
    code.emit("48 85 D2")             # test rdx, rdx
    code.branch8(0x74, "number")
    code.emit("81 7A 08 00 00 E0 41") # cmp dword [rdx+8], 28.0f
    code.branch8(0x75, "number")

    # warning X = plate X + rendered plate width
    code.emit("F3 0F 10 40 08")       # movss xmm0, [rax+0x08]
    code.emit("F3 0F 58 40 10")       # addss xmm0, [rax+0x10]
    code.emit("F3 0F 11 42 08")       # movss [rdx+0x08], xmm0

    # warning Y = plate Y + (plate height - special image height) / 2
    code.emit("F3 0F 10 40 0C")       # movss xmm0, [rax+0x0c]
    code.emit("F3 0F 10 50 14")       # movss xmm2, [rax+0x14]
    code.emit("F3 0F 5C 92 A0 00 00 00") # subss xmm2, [rdx+0xa0]
    code.emit("41 BA 00 00 00 3F")    # mov r10d, 0.5f
    code.emit("66 41 0F 6E DA")       # movd xmm3, r10d
    code.emit("F3 0F 59 D3")          # mulss xmm2, xmm3
    code.emit("F3 0F 58 C2")          # addss xmm0, xmm2
    code.emit("F3 0F 11 42 0C")       # movss [rdx+0x0c], xmm0

    code.label("number")
    code.emit("48 8B 91 60 02 00 00") # mov rdx, [rcx+0x260] (number)
    code.emit("48 85 D2")             # test rdx, rdx
    code.branch8(0x74, "return")
    code.emit("81 7A 08 00 00 48 42") # cmp dword [rdx+8], 50.0f
    code.branch8(0x75, "return")
    code.emit("4C 8B 81 48 02 00 00") # mov r8, [rcx+0x248] (moved status)
    code.emit("4D 85 C0")             # test r8, r8
    code.branch8(0x74, "return")

    # Require the primary status child to have been moved by patch 006.  This
    # prevents the ordinary troop-count child below the castle crest from ever
    # becoming an accidental anchor.
    code.emit("F3 41 0F 10 40 08")    # movss xmm0, [r8+0x08]
    code.emit("41 BA 00 00 F0 41")    # mov r10d, 30.0f
    code.emit("66 41 0F 6E CA")       # movd xmm1, r10d
    code.emit("0F 2F C1")             # comiss xmm0, xmm1
    code.branch8(0x76, "return")      # jbe return

    # Preserve the native horizontal relationship after patch 006 has moved
    # the icon by the dynamic label width: number X = status X + (50 - 30).
    code.emit("41 BA 00 00 A0 41")    # mov r10d, 20.0f
    code.emit("66 41 0F 6E CA")       # movd xmm1, r10d
    code.emit("F3 0F 58 C1")          # addss xmm0, xmm1
    code.emit("F3 0F 11 42 08")       # movss [rdx+0x08], xmm0

    # number Y = status Y + status height - number height
    code.emit("F3 41 0F 10 40 0C")    # movss xmm0, [r8+0x0c]
    code.emit("F3 41 0F 58 40 14")    # addss xmm0, [r8+0x14]
    code.emit("F3 0F 5C 42 14")       # subss xmm0, [rdx+0x14]
    code.emit("F3 0F 11 42 0C")       # movss [rdx+0x0c], xmm0

    code.label("return")
    code.emit("48 83 C4 58 C3")       # release the original 006 frame; ret

    injected = code.finish()
    labels = {name: code_va + offset for name, offset in code.labels.items()}
    return injected, labels


def build(source_path: Path, output_path: Path, manifest_path: Path) -> dict[str, object]:
    source = source_path.read_bytes()
    source_hash = sha256(source)
    if len(source) != TARGET_SIZE or source_hash != EXPECTED_V0140_SHA256:
        raise RuntimeError(
            f"unexpected v0.14.0 candidate: size={len(source)} sha256={source_hash}"
        )

    pe = pe_tools.parse_pe(source)
    if pe["image_base"] != IMAGE_BASE:
        raise RuntimeError("unexpected image base")
    sections = [section for section in pe["sections"] if section["name"] == CODE_SECTION]
    if len(sections) != 1:
        raise RuntimeError(f"expected exactly one {CODE_SECTION} section")
    section = sections[0]
    if section["virtual_size"] != EXPECTED_SECTION_VIRTUAL_SIZE:
        raise RuntimeError("unexpected pre-008 .mlbd virtual size")
    if section["raw_size"] != EXPECTED_SECTION_RAW_SIZE:
        raise RuntimeError("unexpected .mlbd raw size")
    if (section["characteristics"] & IMAGE_SCN_MEM_EXECUTE) == 0:
        raise RuntimeError("patch 006 executable section flag is missing")

    unaligned_file_offset = section["raw_pointer"] + section["virtual_size"]
    code_file_offset = (unaligned_file_offset + 15) & ~15
    code_padding = code_file_offset - unaligned_file_offset
    code_va = IMAGE_BASE + section["rva"] + section["virtual_size"] + code_padding
    injected, labels = build_injected_code(code_va)
    raw_end = section["raw_pointer"] + section["raw_size"]
    if code_file_offset + len(injected) > raw_end:
        raise RuntimeError("patch 008 helper exceeds .mlbd raw tail")
    if source[unaligned_file_offset : code_file_offset + len(injected)] != b"\0" * (
        code_padding + len(injected)
    ):
        raise RuntimeError("patch 008 helper destination is not empty")

    epilogue_offset = pe_tools.va_to_file(source, pe, EXISTING_006_EPILOGUE_VA)
    epilogue_before = source[epilogue_offset : epilogue_offset + 5]
    if epilogue_before != EXISTING_006_EPILOGUE_BEFORE:
        raise RuntimeError(
            "published patch 006 wrapper epilogue changed: "
            + epilogue_before.hex(" ").upper()
        )
    epilogue_after = b"\xE9" + status_tools.rel32(
        EXISTING_006_EPILOGUE_VA + 5, labels["aux_alignment"]
    )

    candidate = bytearray(source)
    candidate[code_file_offset : code_file_offset + len(injected)] = injected
    candidate[epilogue_offset : epilogue_offset + 5] = epilogue_after
    virtual_size_offset = section["header_offset"] + 8
    new_virtual_size = section["virtual_size"] + code_padding + len(injected)
    candidate[virtual_size_offset : virtual_size_offset + 4] = new_virtual_size.to_bytes(
        4, "little"
    )
    checksum_offset = status_tools.pe_checksum_offset(candidate)
    status_tools.set_pe_checksum(candidate)

    result = bytes(candidate)
    result_hash = sha256(result)
    if EXPECTED_CANDIDATE_SHA256 and result_hash != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(f"v0.14.0 patch-008 candidate hash changed: {result_hash}")

    reviewed_offsets = set(range(code_file_offset, code_file_offset + len(injected)))
    reviewed_offsets.update(range(epilogue_offset, epilogue_offset + 5))
    reviewed_offsets.update(range(virtual_size_offset, virtual_size_offset + 4))
    reviewed_offsets.update(range(checksum_offset, checksum_offset + 4))
    changed_offsets = {
        offset
        for offset, (before, after) in enumerate(zip(source, result, strict=True))
        if before != after
    }
    if not changed_offsets or not changed_offsets <= reviewed_offsets:
        raise RuntimeError("candidate changed outside reviewed patch 008 sites")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    manifest: dict[str, object] = {
        "schema": "nobu16.map-label-auxiliary-alignment.v1",
        "release": "v0.14.0",
        "input": {"path": str(source_path), "size": len(source), "sha256": source_hash},
        "output": {"path": str(output_path), "size": len(result), "sha256": result_hash},
        "alignment": {
            "battle_ready_number": {
                "widget": "label object +0x260",
                "anchor": "moved primary status widget +0x248",
                "x_formula": "status X + native number-to-status offset (50 - 30 = 20)",
                "y_formula": "status Y + status height - number height",
            },
            "no_castle_lord_warning": {
                "status_id": "0x10DE5",
                "widget": "label object +0x270",
                "x_formula": "plate X + rendered plate width",
                "y_formula": "plate Y + (plate height - warning image height at +0xA0) / 2",
            },
            "excluded": ["castle crest", "ordinary troop count below castle crest"],
        },
        "chain": {
            "existing_006_wrapper_va": f"0x{EXISTING_006_WRAPPER_VA:X}",
            "existing_006_epilogue_va": f"0x{EXISTING_006_EPILOGUE_VA:X}",
            "before": epilogue_before.hex(" ").upper(),
            "after": epilogue_after.hex(" ").upper(),
            "helper_va": f"0x{code_va:X}",
        },
        "injected_code": {
            "section": CODE_SECTION,
            "file_offset": f"0x{code_file_offset:X}",
            "size": len(injected),
            "padding": code_padding,
            "new_section_virtual_size": new_virtual_size,
        },
        "changed_byte_count": len(changed_offsets),
        "runtime_restart_required": True,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    print(build(args.source, args.output, args.manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
