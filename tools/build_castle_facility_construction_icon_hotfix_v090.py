#!/usr/bin/env python3
"""Build the v0.90 horizontal castle-facility construction-icon hotfix.

The castle label update path restores an active castle-town construction icon
at label-object child offset 0x268 to the original vertical coordinates
(30, 92).  The horizontal layout uses the live name-plate width, so this
helper chains from the existing patch-008 epilogue and changes only that exact
active-coordinate sentinel:

    X = 30 + rendered name-plate width
    Y = 189

Inactive construction icons and every other map-label child are left alone.
The helper is shared by the normal and XInput horizontal recipes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


EXPECTED_HORIZONTAL_SHA256 = (
    "7A0DF96C72A93F551F283EF14F06159F50E6A265A3BAC9C14151A1C2895D4DA0"
)
EXPECTED_XINPUT_HORIZONTAL_SHA256 = (
    "6EDB65ECFBEBC73C4211E86A3E6BD286F075DD4AD8CECB16E58448612877AF6A"
)
# Pinned after deterministic build and loader verification.
EXPECTED_PATCHED_HORIZONTAL_SHA256 = (
    "EDE0483A3128A406915BDFAE1C022572A91A9BE1A04132B04B57BD0FE539E042"
)
EXPECTED_PATCHED_XINPUT_HORIZONTAL_SHA256 = (
    "C74C099CF4FBC0A7CC183B361416EB7B40C4860668EABB5B7C596EA94CFD43B6"
)

IMAGE_BASE = 0x140000000
CODE_SECTION = ".mlbd"
EXPECTED_SOURCE_SIZE = 67_024_896
EXPECTED_SECTION_RAW_SIZE = 0x021A4600
EXPECTED_HORIZONTAL_VIRTUAL_SIZE = 0x021A45E7
EXPECTED_XINPUT_VIRTUAL_SIZE = 0x021A4600
APPEND_SIZE = 0x200

PATCH_ID = "014"
PATCH_NAME = "Keep castle-facility construction icons on horizontal labels"
PAYLOAD_NAME = "014.append.bin"

LABEL_WIDTH_WIDGET_OFFSET = 0x140
CONSTRUCTION_ICON_WIDGET_OFFSET = 0x268
WIDGET_X_OFFSET = 0x08
WIDGET_Y_OFFSET = 0x0C
WIDGET_WIDTH_OFFSET = 0x10
ACTIVE_VERTICAL_X_BITS = 0x41F00000  # 30.0f
ACTIVE_VERTICAL_Y_BITS = 0x42B80000  # 92.0f
HORIZONTAL_Y_BITS = 0x433D0000  # 189.0f

AUX_HELPER_EPILOGUE_VA = 0x1447BF3DD
AUX_HELPER_EPILOGUE_BEFORE = bytes.fromhex("48 83 C4 58 C3")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rel32(source_next_va: int, target_va: int) -> bytes:
    displacement = target_va - source_next_va
    if not -(1 << 31) <= displacement < (1 << 31):
        raise RuntimeError("rel32 target out of range")
    return struct.pack("<i", displacement)


def pe_checksum_offset(data: bytes) -> int:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    optional = pe + 24
    if data[pe : pe + 4] != b"PE\0\0" or struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise RuntimeError("input is not PE32+")
    return optional + 64


def set_pe_checksum(data: bytearray) -> None:
    checksum_offset = pe_checksum_offset(data)
    data[checksum_offset : checksum_offset + 4] = b"\0" * 4
    total = 0
    for offset in range(0, len(data), 2):
        if checksum_offset <= offset < checksum_offset + 4:
            word = 0
        else:
            high = data[offset + 1] if offset + 1 < len(data) else 0
            word = data[offset] | high << 8
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    struct.pack_into("<I", data, checksum_offset, (total + len(data)) & 0xFFFFFFFF)


def parse_pe(data: bytes) -> dict[str, object]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    optional = pe + 24
    if data[pe : pe + 4] != b"PE\0\0" or struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise RuntimeError("input is not PE32+")
    image_base = struct.unpack_from("<Q", data, optional + 24)[0]
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    section_table = optional + optional_size
    sections: list[dict[str, int | str]] = []
    for index in range(section_count):
        header = section_table + index * 40
        name = data[header : header + 8].split(b"\0", 1)[0].decode("ascii")
        sections.append(
            {
                "name": name,
                "header_offset": header,
                "virtual_size": struct.unpack_from("<I", data, header + 8)[0],
                "rva": struct.unpack_from("<I", data, header + 12)[0],
                "raw_size": struct.unpack_from("<I", data, header + 16)[0],
                "raw_pointer": struct.unpack_from("<I", data, header + 20)[0],
            }
        )
    return {"image_base": image_base, "sections": sections}


def file_offset_to_va(pe: dict[str, object], file_offset: int) -> int:
    for section in pe["sections"]:
        assert isinstance(section, dict)
        start = int(section["raw_pointer"])
        end = start + int(section["raw_size"])
        if start <= file_offset < end:
            return int(pe["image_base"]) + int(section["rva"]) + file_offset - start
    raise RuntimeError(f"file offset 0x{file_offset:X} is outside PE sections")


def va_to_file(pe: dict[str, object], va: int) -> int:
    rva = va - int(pe["image_base"])
    for section in pe["sections"]:
        assert isinstance(section, dict)
        start = int(section["rva"])
        end = start + max(int(section["virtual_size"]), int(section["raw_size"]))
        if start <= rva < end:
            return int(section["raw_pointer"]) + rva - start
    raise RuntimeError(f"VA 0x{va:X} is outside PE sections")


class CodeBuilder:
    def __init__(self, base_va: int) -> None:
        self.base_va = base_va
        self.code = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, int, str]] = []

    def emit(self, raw: bytes | str) -> None:
        self.code += bytes.fromhex(raw) if isinstance(raw, str) else raw

    def label(self, name: str) -> None:
        self.labels[name] = len(self.code)

    def branch8(self, opcode: int, label: str) -> None:
        self.emit(bytes((opcode, 0)))
        self.fixups.append((len(self.code) - 1, 1, label))

    def branch32(self, opcode: int, label: str) -> None:
        self.emit(bytes((0x0F, opcode)) + b"\0\0\0\0")
        self.fixups.append((len(self.code) - 4, 4, label))

    def finish(self) -> bytes:
        for offset, size, label in self.fixups:
            target = self.labels[label]
            displacement = target - (offset + size)
            if size == 1:
                if not -128 <= displacement <= 127:
                    raise RuntimeError(f"short branch out of range: {label}")
                struct.pack_into("<b", self.code, offset, displacement)
            else:
                struct.pack_into("<i", self.code, offset, displacement)
        return bytes(self.code)


def build_injected_code(code_va: int) -> bytes:
    del code_va  # The helper contains no absolute or RIP-relative references.
    code = CodeBuilder(0)

    # The patch-006 wrapper keeps its 0x58-byte stack frame allocated and
    # stores the label object at [rsp+0x40].  Patch 008 deliberately jumps
    # here before restoring that frame.
    code.emit("48 8B 4C 24 40")       # mov rcx, [rsp+0x40]
    code.emit("48 85 C9")             # test rcx, rcx
    code.branch32(0x84, "return")

    code.emit("48 8B 81 40 01 00 00") # mov rax, [rcx+0x140] (name plate)
    code.emit("48 85 C0")             # test rax, rax
    code.branch32(0x84, "return")
    code.emit("F3 0F 10 48 10")       # movss xmm1, [rax+0x10] (rendered width)
    code.emit("0F 57 C0")             # xorps xmm0, xmm0
    code.emit("0F 2F C8")             # comiss xmm1, xmm0
    code.branch32(0x86, "return")      # jbe return (zero, negative, or NaN)

    code.emit("48 8B 91 68 02 00 00") # mov rdx, [rcx+0x268] (construction icon)
    code.emit("48 85 D2")             # test rdx, rdx
    code.branch8(0x74, "return")
    code.emit("81 7A 08 00 00 F0 41") # cmp dword [rdx+8], 30.0f
    code.branch8(0x75, "return")
    code.emit("81 7A 0C 00 00 B8 42") # cmp dword [rdx+0xc], 92.0f
    code.branch8(0x75, "return")

    code.emit("F3 0F 10 42 08")       # movss xmm0, [rdx+8] (30.0f)
    code.emit("F3 0F 58 C1")          # addss xmm0, xmm1
    code.emit("F3 0F 11 42 08")       # movss [rdx+8], xmm0
    code.emit("C7 42 0C 00 00 3D 43") # mov dword [rdx+0xc], 189.0f

    code.label("return")
    code.emit("48 83 C4 58 C3")       # add rsp, 0x58; ret
    return code.finish()


def materialize_patched_xinput(horizontal: bytes, xinput_recipe_path: Path) -> bytes:
    if sha256(horizontal) != EXPECTED_PATCHED_HORIZONTAL_SHA256:
        raise RuntimeError("patched horizontal source hash gate failed")
    recipe = json.loads(xinput_recipe_path.read_text(encoding="utf-8-sig"))
    patches = [patch for patch in recipe["patches"] if patch["id"] == "013"]
    if len(patches) != 1 or "append" in patches[0]:
        raise RuntimeError("expected one non-appending XInput tail patch 013")
    if recipe["patches"][-1]["id"] != "013":
        raise RuntimeError("XInput patch 013 must remain the tail patch")
    output = bytearray(horizontal)
    for site in patches[0]["sites"]:
        offset = int(site["offset"])
        before = bytes.fromhex(site["before_hex"])
        after = bytes.fromhex(site["after_hex"])
        if len(before) != len(after) or output[offset : offset + len(before)] != before:
            raise RuntimeError(f"XInput tail patch 013 preimage mismatch: {site['name']}")
        output[offset : offset + len(before)] = after
    set_pe_checksum(output)
    result = bytes(output)
    observed = sha256(result)
    if observed != EXPECTED_PATCHED_XINPUT_HORIZONTAL_SHA256:
        raise RuntimeError(f"patched XInput horizontal hash changed: {observed}")
    return result


def apply_static_recipe(recipe_path: Path, material_root: Path) -> bytes:
    """Mirror the Rust patcher's ordered site/append recipe application."""
    recipe = json.loads(recipe_path.read_text(encoding="utf-8-sig"))
    base_path = material_root / Path(recipe["base_relative_path"])
    output = bytearray(base_path.read_bytes())
    if (
        len(output) != int(recipe["base_size"])
        or sha256(output) != recipe["base_sha256"]
    ):
        raise RuntimeError(f"static recipe base gate failed: {recipe_path.name}")
    for patch in recipe["patches"]:
        for site in patch["sites"]:
            offset = int(site["offset"])
            before = bytes.fromhex(site["before_hex"])
            after = bytes.fromhex(site["after_hex"])
            if (
                not before
                or len(before) != len(after)
                or before == after
                or output[offset : offset + len(before)] != before
            ):
                raise RuntimeError(
                    f"static recipe site mismatch: {recipe_path.name}/"
                    f"{patch['id']}/{site['name']}"
                )
            output[offset : offset + len(before)] = after
        append = patch.get("append")
        if append is None:
            continue
        if len(output) != int(append["base_size"]):
            raise RuntimeError(
                f"static recipe append base mismatch: {recipe_path.name}/{patch['id']}"
            )
        payload = (material_root / Path(append["relative_path"])).read_bytes()
        if (
            len(payload) != int(append["payload_size"])
            or sha256(payload) != append["payload_sha256"]
        ):
            raise RuntimeError(
                f"static recipe append gate failed: {recipe_path.name}/{patch['id']}"
            )
        output.extend(payload)
        if len(output) != int(append["target_size"]):
            raise RuntimeError(
                f"static recipe append target mismatch: {recipe_path.name}/{patch['id']}"
            )
    set_pe_checksum(output)
    return bytes(output)


def apply_hotfix(source: bytes) -> tuple[bytes, bytes, dict[str, object]]:
    source_hash = sha256(source)
    if len(source) != EXPECTED_SOURCE_SIZE or source_hash != EXPECTED_HORIZONTAL_SHA256:
        raise RuntimeError(
            f"horizontal source gate failed: size={len(source)} sha256={source_hash}"
        )

    pe = parse_pe(source)
    if pe["image_base"] != IMAGE_BASE:
        raise RuntimeError("unexpected image base")
    sections = [section for section in pe["sections"] if section["name"] == CODE_SECTION]
    if len(sections) != 1:
        raise RuntimeError(f"expected exactly one {CODE_SECTION} section")
    section = sections[0]
    expected_virtual_size = EXPECTED_HORIZONTAL_VIRTUAL_SIZE
    if section["virtual_size"] != expected_virtual_size:
        raise RuntimeError("unexpected horizontal .mlbd virtual size")
    if section["raw_size"] != EXPECTED_SECTION_RAW_SIZE:
        raise RuntimeError("unexpected .mlbd raw size")
    if section["raw_pointer"] + section["raw_size"] != len(source):
        raise RuntimeError(".mlbd is not the final raw section")

    code_file_offset = len(source)
    code_va = IMAGE_BASE + section["rva"] + section["raw_size"]
    injected = build_injected_code(code_va)
    if len(injected) > APPEND_SIZE:
        raise RuntimeError("construction-icon helper exceeds append payload")
    payload = injected + b"\0" * (APPEND_SIZE - len(injected))

    epilogue_offset = va_to_file(pe, AUX_HELPER_EPILOGUE_VA)
    if source[epilogue_offset : epilogue_offset + 5] != AUX_HELPER_EPILOGUE_BEFORE:
        raise RuntimeError("patch-008 epilogue preimage mismatch")
    chain_after = b"\xE9" + rel32(AUX_HELPER_EPILOGUE_VA + 5, code_va)

    virtual_size_offset = section["header_offset"] + 8
    raw_size_offset = section["header_offset"] + 16
    new_virtual_size = section["raw_size"] + len(injected)
    new_raw_size = section["raw_size"] + APPEND_SIZE

    candidate = bytearray(source)
    struct.pack_into("<I", candidate, virtual_size_offset, new_virtual_size)
    struct.pack_into("<I", candidate, raw_size_offset, new_raw_size)
    candidate[epilogue_offset : epilogue_offset + 5] = chain_after
    candidate.extend(payload)
    set_pe_checksum(candidate)
    result = bytes(candidate)

    result_hash = sha256(result)
    if result_hash != EXPECTED_PATCHED_HORIZONTAL_SHA256:
        raise RuntimeError(f"horizontal patched hash changed: {result_hash}")

    patch_definition: dict[str, object] = {
        "id": PATCH_ID,
        "name": PATCH_NAME,
        "sites": [
            {
                "name": "extend .mlbd virtual size through construction-icon helper",
                "offset": virtual_size_offset,
                "before_hex": struct.pack("<I", expected_virtual_size).hex().upper(),
                "after_hex": struct.pack("<I", new_virtual_size).hex().upper(),
            },
            {
                "name": "extend .mlbd raw size through construction-icon helper",
                "offset": raw_size_offset,
                "before_hex": struct.pack("<I", EXPECTED_SECTION_RAW_SIZE).hex().upper(),
                "after_hex": struct.pack("<I", new_raw_size).hex().upper(),
            },
            {
                "name": "chain auxiliary alignment into construction-icon alignment",
                "offset": epilogue_offset,
                "before_hex": AUX_HELPER_EPILOGUE_BEFORE.hex().upper(),
                "after_hex": chain_after.hex().upper(),
            },
        ],
        "append": {
            "relative_path": f"static/{PAYLOAD_NAME}",
            "base_size": len(source),
            "target_size": len(result),
            "payload_size": len(payload),
            "payload_sha256": sha256(payload),
        },
    }
    metadata: dict[str, object] = {
        "source_kind": "horizontal",
        "input": {"size": len(source), "sha256": source_hash},
        "output": {"size": len(result), "sha256": result_hash},
        "helper": {
            "file_offset": code_file_offset,
            "virtual_address": f"0x{code_va:X}",
            "size": len(injected),
            "label_width_widget_offset": f"0x{LABEL_WIDTH_WIDGET_OFFSET:X}",
            "construction_icon_widget_offset": f"0x{CONSTRUCTION_ICON_WIDGET_OFFSET:X}",
            "active_vertical_sentinel": [30.0, 92.0],
            "horizontal_formula": {"x": "30 + rendered name-plate width", "y": 189.0},
        },
        "patch_definition": patch_definition,
    }
    return result, payload, metadata


def build(
    horizontal_source_path: Path,
    xinput_recipe_path: Path,
    horizontal_output_path: Path,
    xinput_output_path: Path,
    payload_output_path: Path,
    manifest_output_path: Path,
    material_root: Path | None,
) -> dict[str, object]:
    horizontal_source = horizontal_source_path.read_bytes()
    if sha256(horizontal_source) != EXPECTED_HORIZONTAL_SHA256:
        raise RuntimeError("horizontal source hash gate failed")

    horizontal, horizontal_payload, horizontal_metadata = apply_hotfix(horizontal_source)
    xinput = materialize_patched_xinput(horizontal, xinput_recipe_path)
    xinput_metadata = {
        "source_kind": "xinput",
        "input": horizontal_metadata["input"],
        "output": {"size": len(xinput), "sha256": sha256(xinput)},
        "helper": horizontal_metadata["helper"],
        "patch_definition": horizontal_metadata["patch_definition"],
        "controller_tail_patch_id": "013",
    }

    horizontal_output_path.parent.mkdir(parents=True, exist_ok=True)
    xinput_output_path.parent.mkdir(parents=True, exist_ok=True)
    payload_output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_output_path.parent.mkdir(parents=True, exist_ok=True)
    horizontal_output_path.write_bytes(horizontal)
    xinput_output_path.write_bytes(xinput)
    payload_output_path.write_bytes(horizontal_payload)
    manifest: dict[str, object] = {
        "schema": "nobu16.castle-facility-construction-icon-horizontal.v1",
        "issue": 72,
        "normal": horizontal_metadata,
        "xinput": xinput_metadata,
        "shared_payload": {
            "path": str(payload_output_path),
            "size": len(horizontal_payload),
            "sha256": sha256(horizontal_payload),
        },
        "resource_archives_changed": False,
        "runtime_restart_required": True,
    }
    if material_root is not None:
        normal_recipe_path = xinput_recipe_path.with_name("static-recipe.horizontal.json")
        reproduced_horizontal = apply_static_recipe(normal_recipe_path, material_root)
        reproduced_xinput = apply_static_recipe(xinput_recipe_path, material_root)
        if reproduced_horizontal != horizontal:
            raise RuntimeError("normal horizontal recipe reproduction differs from candidate")
        if reproduced_xinput != xinput:
            raise RuntimeError("XInput horizontal recipe reproduction differs from candidate")
        manifest["recipe_reproduction"] = {
            "material_root": str(material_root),
            "normal_exact": True,
            "xinput_exact": True,
        }
    manifest_output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizontal-source", required=True, type=Path)
    parser.add_argument("--xinput-recipe", required=True, type=Path)
    parser.add_argument("--horizontal-output", required=True, type=Path)
    parser.add_argument("--xinput-output", required=True, type=Path)
    parser.add_argument("--payload-output", required=True, type=Path)
    parser.add_argument("--manifest-output", required=True, type=Path)
    parser.add_argument("--material-root", type=Path)
    args = parser.parse_args()
    manifest = build(
        args.horizontal_source,
        args.xinput_recipe,
        args.horizontal_output,
        args.xinput_output,
        args.payload_output,
        args.manifest_output,
        args.material_root,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
