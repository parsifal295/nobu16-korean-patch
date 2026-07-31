#!/usr/bin/env python3
"""Inspect or temporarily align active castle-facility construction icons.

This is a narrow real-game QA probe for the v0.90 horizontal map-label fix.
It scans only live label-pool category 1 and only child field 0x268.  Writes
are additionally gated on the exact native vertical sentinel (30.0, 92.0).
Restarting the game discards all probe writes.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import struct
from ctypes import wintypes

import build_castle_facility_construction_icon_hotfix_v090 as hotfix


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PAGE_EXECUTE_READWRITE = 0x40

PREFERRED_IMAGE_BASE = 0x140000000
LABEL_POOL_VA = 0x1422626CC
LABEL_OBJECT_SIZE = 0x2D0
LABEL_WIDTH_CHILD_OFFSET = 0x140
CONSTRUCTION_CHILD_OFFSET = 0x268
ACTIVE_VERTICAL = (30.0, 92.0)
HORIZONTAL_Y = 189.0

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.WriteProcessMemory.restype = wintypes.BOOL
kernel32.VirtualProtectEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_size_t,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.VirtualProtectEx.restype = wintypes.BOOL
kernel32.FlushInstructionCache.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
kernel32.FlushInstructionCache.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def read_exact(handle: int, address: int, size: int) -> bytes | None:
    buffer = ctypes.create_string_buffer(size)
    read = ctypes.c_size_t()
    if not kernel32.ReadProcessMemory(
        handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(read)
    ):
        return None
    return buffer.raw if read.value == size else None


def write_exact(handle: int, address: int, data: bytes) -> None:
    buffer = ctypes.create_string_buffer(data)
    written = ctypes.c_size_t()
    if not kernel32.WriteProcessMemory(
        handle,
        ctypes.c_void_p(address),
        buffer,
        len(data),
        ctypes.byref(written),
    ) or written.value != len(data):
        raise ctypes.WinError(ctypes.get_last_error())


def write_executable(handle: int, address: int, data: bytes) -> None:
    old_protect = wintypes.DWORD()
    if not kernel32.VirtualProtectEx(
        handle,
        ctypes.c_void_p(address),
        len(data),
        PAGE_EXECUTE_READWRITE,
        ctypes.byref(old_protect),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        write_exact(handle, address, data)
        if not kernel32.FlushInstructionCache(
            handle, ctypes.c_void_p(address), len(data)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        ignored = wintypes.DWORD()
        if not kernel32.VirtualProtectEx(
            handle,
            ctypes.c_void_p(address),
            len(data),
            old_protect.value,
            ctypes.byref(ignored),
        ):
            raise ctypes.WinError(ctypes.get_last_error())


def apply_or_restore_code(handle: int, image_base: int, restore: bool) -> dict[str, object]:
    helper_va = 0x1447BF600
    helper = hotfix.build_injected_code(helper_va)
    chain = b"\xE9" + hotfix.rel32(hotfix.AUX_HELPER_EPILOGUE_VA + 5, helper_va)
    epilogue_address = image_base + (
        hotfix.AUX_HELPER_EPILOGUE_VA - PREFERRED_IMAGE_BASE
    )
    helper_address = image_base + (helper_va - PREFERRED_IMAGE_BASE)
    current_epilogue = read_exact(handle, epilogue_address, len(chain))
    current_helper = read_exact(handle, helper_address, len(helper))
    if current_epilogue is None or current_helper is None:
        raise RuntimeError("runtime code sites are unreadable")

    if restore:
        if current_epilogue != chain or current_helper != helper:
            raise RuntimeError("runtime hotfix is not present exactly; refusing restore")
        write_executable(handle, epilogue_address, hotfix.AUX_HELPER_EPILOGUE_BEFORE)
        write_executable(handle, helper_address, b"\0" * len(helper))
        expected_epilogue = hotfix.AUX_HELPER_EPILOGUE_BEFORE
        expected_helper = b"\0" * len(helper)
        action = "restored"
    else:
        if current_epilogue not in (hotfix.AUX_HELPER_EPILOGUE_BEFORE, chain):
            raise RuntimeError("runtime patch-008 epilogue preimage mismatch")
        if current_helper not in (b"\0" * len(helper), helper):
            raise RuntimeError("runtime helper area is not empty")
        write_executable(handle, helper_address, helper)
        write_executable(handle, epilogue_address, chain)
        expected_epilogue = chain
        expected_helper = helper
        action = "applied"

    if read_exact(handle, epilogue_address, len(expected_epilogue)) != expected_epilogue:
        raise RuntimeError("runtime epilogue verification failed")
    if read_exact(handle, helper_address, len(expected_helper)) != expected_helper:
        raise RuntimeError("runtime helper verification failed")
    return {
        "action": action,
        "epilogue_address": f"0x{epilogue_address:X}",
        "epilogue_bytes": expected_epilogue.hex(" ").upper(),
        "helper_address": f"0x{helper_address:X}",
        "helper_size": len(helper),
        "helper_sha256": hotfix.sha256(helper),
        "restart_restores_runtime_code": True,
    }


def inspect_or_apply(handle: int, image_base: int, apply: bool) -> dict[str, object]:
    pool = image_base + (LABEL_POOL_VA - PREFERRED_IMAGE_BASE)
    header = read_exact(handle, pool, 12)
    if header is None:
        raise RuntimeError(f"label pool is unreadable at 0x{pool:X}")
    count = struct.unpack_from("<I", header, 0)[0]
    records = struct.unpack_from("<Q", header, 4)[0]
    matches: list[dict[str, object]] = []

    for index in range(count):
        record = read_exact(handle, records + index * 0x30, 0x30)
        if record is None:
            continue
        label = struct.unpack_from("<Q", record, 0)[0]
        if not label:
            continue
        fields = read_exact(handle, label, LABEL_OBJECT_SIZE)
        if fields is None:
            continue
        plate = struct.unpack_from("<Q", fields, LABEL_WIDTH_CHILD_OFFSET)[0]
        icon = struct.unpack_from("<Q", fields, CONSTRUCTION_CHILD_OFFSET)[0]
        if not plate or not icon:
            continue
        plate_data = read_exact(handle, plate, 0x18)
        icon_data = read_exact(handle, icon, 0x18)
        if plate_data is None or icon_data is None:
            continue
        width = struct.unpack_from("<f", plate_data, 0x10)[0]
        x, y = struct.unpack_from("<2f", icon_data, 0x08)
        if (x, y) != ACTIVE_VERTICAL:
            continue
        target_x = ACTIVE_VERTICAL[0] + width
        if apply:
            write_exact(handle, icon + 0x08, struct.pack("<2f", target_x, HORIZONTAL_Y))
            verified = read_exact(handle, icon + 0x08, 8)
            if verified != struct.pack("<2f", target_x, HORIZONTAL_Y):
                raise RuntimeError(f"write verification failed for label index {index}")
        matches.append(
            {
                "index": index,
                "label": f"0x{label:X}",
                "plate": f"0x{plate:X}",
                "icon": f"0x{icon:X}",
                "before": [x, y],
                "rendered_width": width,
                "after": [target_x, HORIZONTAL_Y] if apply else None,
            }
        )

    return {
        "pid": None,
        "image_base": f"0x{image_base:X}",
        "label_count": count,
        "apply": apply,
        "matched_active_vertical_icons": len(matches),
        "matches": matches,
        "restart_restores_probe_writes": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--base", required=True, type=lambda value: int(value, 0))
    parser.add_argument("--apply", action="store_true")
    code_mode = parser.add_mutually_exclusive_group()
    code_mode.add_argument("--apply-code", action="store_true")
    code_mode.add_argument("--restore-code", action="store_true")
    args = parser.parse_args()
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
    if args.apply or args.apply_code or args.restore_code:
        access |= PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    handle = kernel32.OpenProcess(access, False, args.pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if args.apply_code or args.restore_code:
            result = apply_or_restore_code(handle, args.base, args.restore_code)
            result["pid"] = args.pid
            result["image_base"] = f"0x{args.base:X}"
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        result = inspect_or_apply(handle, args.base, args.apply)
        result["pid"] = args.pid
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        kernel32.CloseHandle(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
