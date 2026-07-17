#!/usr/bin/env python3
"""Revalidate the current Steam PC event-layout review set without writing Steam.

The frozen v2 candidate is intentionally hash-gated to its older source.  This
read-only verifier instead measures the *currently installed* post-quality
``msgev.bin`` against the same 4,003 reviewed coordinates and current font.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
V2_SCRIPT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "build_steam_jp_msgev_full_layout_v2.py"
AUDIT_PATH = REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "public" / "msgev_full_layout_audit.v2.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_REPORT = REPO / "tmp" / WORKSTREAM.name / "revalidation.v1.json"

EXPECTED_MSGEV_SHA256 = "9572873D2BBFF3C62581F09BE2CD54225CCDD2C400D3ACC895675E2C0A2780DD"
EXPECTED_FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
EXPECTED_COORDINATE_SHA256 = "5907103ACB45E4822966559817B39EE77BC00E4C9DDBEEA89A409AD9A1EA5A8B"
REVIEW_CLASSES = {
    "already_fit_after_review",
    "protected_runtime_width_unknown_preserved",
    "reviewed_boundary_reflow",
    "reviewed_semantic_compaction",
}
PROTECTED_ID = 16402
TOKEN_RE = re.compile(r"\[([a-z]+)(\d+)\]")
SCHEMA = "nobu16.kr.pc-msgev-current-layout-revalidation.v1"


class RevalidationError(ValueError):
    """Raised when the installed resource or audit contract differs."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_hash(ids: list[int]) -> str:
    value = [{"id": entry_id} for entry_id in sorted(ids)]
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode("ascii")).hexdigest().upper()


def load_v2():
    spec = importlib.util.spec_from_file_location("msgev_layout_v2_current_revalidation", V2_SCRIPT)
    if spec is None or spec.loader is None:
        raise RevalidationError(f"cannot load v2 layout builder: {V2_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def reviewed_ids() -> list[int]:
    document = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if document.get("resource") != "MSG_PK/JP/msgev.bin":
        raise RevalidationError("v2 audit resource differs")
    rows = document.get("rows")
    if not isinstance(rows, list):
        raise RevalidationError("v2 audit rows are absent")
    ids: list[int] = []
    classes: dict[str, int] = {kind: 0 for kind in REVIEW_CLASSES}
    for row in rows:
        if not isinstance(row, dict):
            raise RevalidationError("v2 audit row is not an object")
        classification = row.get("classification")
        entry_id = row.get("id")
        if classification in REVIEW_CLASSES:
            if type(entry_id) is not int or entry_id < 0:
                raise RevalidationError("v2 audit reviewed row ID differs")
            ids.append(entry_id)
            classes[classification] += 1
    if len(ids) != 4003 or len(set(ids)) != 4003:
        raise RevalidationError(f"v2 reviewed coordinate count differs: {len(ids)}")
    expected = {
        "already_fit_after_review": 1157,
        "protected_runtime_width_unknown_preserved": 1,
        "reviewed_boundary_reflow": 1293,
        "reviewed_semantic_compaction": 1552,
    }
    if classes != expected or ids.count(PROTECTED_ID) != 1:
        raise RevalidationError(f"v2 review classification contract differs: {classes}")
    coordinate_sha256 = canonical_hash(ids)
    if coordinate_sha256 != EXPECTED_COORDINATE_SHA256:
        raise RevalidationError(f"v2 review coordinate contract differs: {coordinate_sha256}")
    return sorted(ids)


def live_reservations(module, table, advance, ids: list[int]) -> tuple[dict[str, int], dict[str, object]]:
    tokens: list[str] = []
    for entry_id in ids:
        for token in module.RUNTIME_RE.findall(table.texts[entry_id]):
            tokens.append(token)
    reservations: dict[str, int] = {}
    name_ids: set[int] = set()
    for token in sorted(set(tokens)):
        match = TOKEN_RE.fullmatch(token)
        if match is None:
            raise RevalidationError(f"unparseable runtime token: {token}")
        name_id = int(match.group(2))
        if name_id >= table.string_count:
            raise RevalidationError(f"runtime name ID is outside msgsev table: {token}")
        name_ids.add(name_id)
        reservations[token] = module.base.visual_line_width(table.texts[name_id], advance)
        if reservations[token] <= 0:
            raise RevalidationError(f"runtime name width is not positive: {token}")
    return reservations, {
        "token_spelling_count": len(reservations),
        "token_occurrence_count": len(tokens),
        "referenced_name_count": len(name_ids),
    }


def verify(steam_root: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    msg_path = steam_root / "MSG_PK" / "JP" / "msgev.bin"
    font_path = steam_root / "RES_JP" / "res_lang.bin"
    msg_hash = sha256_path(msg_path)
    font_hash = sha256_path(font_path)
    if msg_hash != EXPECTED_MSGEV_SHA256 or font_hash != EXPECTED_FONT_SHA256:
        raise RevalidationError(f"current Steam baseline differs: msgsev={msg_hash}, font={font_hash}")
    module = load_v2()
    _path, _packed, _raw, table = module.source_table(steam_root)
    advance, _font = module.current_font(steam_root)
    ids = reviewed_ids()
    reservations, reservation_summary = live_reservations(module, table, advance, ids)
    failures: list[dict[str, object]] = []
    max_lines = 0
    max_actual = 0
    max_reserved = 0
    protected_actual: list[int] | None = None
    protected_reserved: list[int] | None = None
    for entry_id in ids:
        actual, reserved = module.target_width_pairs(table.texts[entry_id], advance, reservations)
        max_lines = max(max_lines, len(actual))
        max_actual = max(max_actual, max(actual, default=0))
        max_reserved = max(max_reserved, max(reserved, default=0))
        if entry_id == PROTECTED_ID:
            protected_actual, protected_reserved = actual, reserved
            continue
        if len(actual) > module.MAX_LINES or max(reserved, default=0) > module.MAX_LINE_PX:
            failures.append({"id": entry_id, "actual_widths": actual, "reserved_widths": reserved})
    if protected_actual is None or protected_reserved is None:
        raise RevalidationError("protected printf row was not measured")
    return {
        "schema": SCHEMA,
        "status": "PASS" if not failures else "FAIL",
        "resource": "MSG_PK/JP/msgev.bin",
        "steam": {"msgev_sha256": msg_hash, "font_sha256": font_hash},
        "reviewed_row_count": len(ids),
        "coordinate_sha256": canonical_hash(ids),
        "bounded_row_count": len(ids) - 1,
        "bounded_failures": failures,
        "max_static_line_count_all_rows": max_lines,
        "max_actual_width_px_all_rows": max_actual,
        "max_reserved_width_px_all_rows": max_reserved,
        "limit": {"max_lines": module.MAX_LINES, "max_reserved_width_px": module.MAX_LINE_PX},
        "protected_printf_row": {"id": PROTECTED_ID, "static_line_count": len(protected_actual), "static_actual_widths_px": protected_actual, "static_reserved_widths_px": protected_reserved},
        "runtime_reservations": reservation_summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true", help="write the source-free report under tmp")
    args = parser.parse_args(argv)
    try:
        report = verify(args.steam_root)
    except (OSError, ValueError, RevalidationError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    if args.write:
        report_path = args.report.resolve()
        allowed = (REPO / "tmp" / WORKSTREAM.name).resolve()
        try:
            report_path.relative_to(allowed)
        except ValueError:
            print(json.dumps({"status": "FAIL", "error": f"report path escapes {allowed}"}, ensure_ascii=False, sort_keys=True))
            return 2
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
