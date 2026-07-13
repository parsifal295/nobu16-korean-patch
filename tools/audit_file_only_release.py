#!/usr/bin/env python3
"""Fail closed when a NOBU16 Korean-patch release is not file-only.

This is deliberately stricter than a general malware scanner.  A publishable
bundle may contain transparent offline scripts, compact recipes/deltas, hashes,
and license text.  It may not contain PE code, complete game resources, or any
of the Windows APIs commonly used to alter another process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path


REQUIRED_MANIFEST = {
    "architecture": "file-only-offline",
    "process_memory_access": False,
    "executable_modified": False,
    "registry_modified": False,
    "launches_game": False,
    "resident_component": False,
    "commercial_full_files_included": False,
    "requires_process_running": False,
    "runtime_validation": "passed",
    "install_restore_tested": True,
    "release_eligible": True,
    "target_files": ["MSG_PK/SC/msgui.bin", "RES_SC/res_lang.bin"],
    "payload_format": "recipes-and-deltas-only",
}

FORBIDDEN_PATTERNS = {
    "process-memory write": rb"\bWriteProcessMemory\b",
    "native process-memory write": rb"\bNtWriteVirtualMemory\b",
    "process-memory read": rb"\bReadProcessMemory\b",
    "remote process open": rb"\bOpenProcess\b",
    "remote allocation": rb"\bVirtualAllocEx\b",
    "remote protection change": rb"\bVirtualProtectEx\b",
    "remote thread": rb"\bCreateRemoteThread(?:Ex)?\b",
    "native remote thread": rb"\bNtCreateThreadEx\b",
    "APC injection": rb"\bQueueUserAPC\b",
    "thread-context injection": rb"\bSetThreadContext\b",
    "debugger attachment": rb"\bDebugActiveProcess\b",
    "Windows hook": rb"\bSetWindowsHookEx[AW]?\b",
    "process launcher": rb"\bStart-Process\b|\bSystem\.Diagnostics\.Process\s*\]\s*::\s*Start\b",
    "shell execution": rb"\bShellExecute(?:Ex)?[AW]?\b",
    "game executable reference": rb"\bNOBU16(?:PK(?:_EN)?|_Launcher)?\.exe\b",
    "registry command write": rb"\breg(?:\.exe)?\s+(?:add|delete|import|restore|load|unload|copy)\b",
    "PowerShell registry write": rb"\b(?:New|Set|Remove)-ItemProperty\b",
    "Python registry write": rb"\bwinreg\s*\.\s*(?:SetValue|SetValueEx|CreateKey|CreateKeyEx|DeleteValue|DeleteKey|DeleteKeyEx)\b",
    "native registry write": rb"\bReg(?:SetValue|CreateKey|DeleteValue|DeleteKey)[A-Za-z0-9_]*\b",
    "DLL injection wording": rb"\b(?:dll[ _-]?inject(?:ion|or)?|inject[ _-]?dll)\b",
    "runtime patcher wording": rb"\bRuntimePatcher\b",
    "retired runtime module": rb"\bnobu16_ko_runtime_patch\b",
}

FORBIDDEN_BASENAMES = {
    "res_lang.bin",
    "msgui.bin",
    "nobu16pk.exe",
    "nobu16pk_en.exe",
    "nobu16_launcher.exe",
}

# Known complete local resources.  Hash checks catch renamed copies too.
FORBIDDEN_SHA256 = {
    "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99": "stock SC res_lang.bin",
    "A286388AC4A8F6E03E3BD5AC5B91069E858805EBBE81F670991B162A813B0B2F": "stock TC res_lang.bin",
    "7FB2E6E7ABE2ADC7C359170ECB92952054C2F7F412933B8F1B339B6ADE661B7E": "complete SC candidate res_lang.bin",
    "5228871705DBF0CDB61B95A704E74B51B8B2CE59539CBA78CF94ACB096B199AF": "complete TC candidate res_lang.bin",
    "C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82": "stock SC msgui.bin",
    "45DD6DA6EA2BF924350E67FD3B5922410C6798477CA10F795327E1AD4239E3AA": "complete Korean SC msgui.bin",
    "BAA1A88F2C83E3EDA06AB2D02A28C3C96D2BA7090E3CE7E643D96B077A0B1739": "game executable",
}

TEXT_SUFFIXES = {
    ".bat", ".cmd", ".json", ".md", ".ps1", ".py", ".sh", ".txt", ".yaml", ".yml"
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def fail(issues: list[dict[str, str]], path: Path, rule: str, detail: str) -> None:
    issues.append({"path": path.as_posix(), "rule": rule, "detail": detail})


def audit(root: Path) -> dict[str, object]:
    issues: list[dict[str, str]] = []
    files: list[dict[str, object]] = []
    manifest_path = root / "release_manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # fail closed, including a missing manifest
        manifest = None
        fail(issues, manifest_path, "manifest", f"cannot read valid UTF-8 JSON: {exc}")

    if isinstance(manifest, dict):
        missing = object()
        for key, expected in REQUIRED_MANIFEST.items():
            actual = manifest.get(key, missing)
            if actual != expected:
                rendered_actual = "<missing>" if actual is missing else repr(actual)
                fail(
                    issues,
                    manifest_path,
                    "manifest contract",
                    f"{key} must be {expected!r}, got {rendered_actual}",
                )

    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail(issues, path, "symlink", "release entries must be ordinary files/directories")
            continue
        if not path.is_file():
            continue

        relative = path.relative_to(root)
        size = path.stat().st_size
        digest = sha256(path)
        files.append({"path": relative.as_posix(), "size": size, "sha256": digest})

        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_BASENAMES:
            fail(issues, relative, "complete resource name", path.name)
        if path.suffix.lower() in {".exe", ".dll", ".sys", ".com"}:
            fail(issues, relative, "native executable payload", path.suffix.lower())
        forbidden_hash = FORBIDDEN_SHA256.get(digest)
        if forbidden_hash:
            fail(issues, relative, "complete resource hash", forbidden_hash)

        # Complete game resources are large.  The current main-menu recipe and
        # deltas are tiny, so this cap also catches renamed full-file payloads.
        if size > 8 * 1024 * 1024:
            fail(issues, relative, "oversized payload", f"{size} bytes exceeds 8 MiB")

        with path.open("rb") as stream:
            prefix = stream.read(2)
        if prefix == b"MZ":
            fail(issues, relative, "PE signature", "MZ executable content is forbidden")

        if path.suffix.lower() in TEXT_SUFFIXES or size <= 2 * 1024 * 1024:
            data = path.read_bytes()
            for label, pattern in FORBIDDEN_PATTERNS.items():
                if re.search(pattern, data, re.IGNORECASE):
                    fail(issues, relative, "forbidden runtime capability", label)

    return {
        "schema": 1,
        "root": str(root.resolve()),
        "status": "PASS" if not issues else "FAIL",
        "policy": REQUIRED_MANIFEST,
        "file_count": len(files),
        "files": files,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    root = args.release_dir.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    report = audit(root)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8", newline="\n")
    sys.stdout.write(encoded)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
