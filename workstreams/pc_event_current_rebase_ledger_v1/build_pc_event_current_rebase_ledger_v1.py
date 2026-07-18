#!/usr/bin/env python3
"""Verify the current Steam-PC event-layout state without changing any file.

This ledger deliberately does *not* consume the stale v2 target overlay.  The
current PK event table already contains its accepted layout state, so the only
valid build result is an in-memory no-op proof.  It reads the current Base/PK
event tables and event font, pins their hashes, validates the current hard-LF
domain and runtime-name reservations, and emits a source-free JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, parse_link  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
import build_common_message_overlay as common  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-current-rebase-ledger.v1"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
V2_AUDIT_PATH = REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "public" / "msgev_full_layout_audit.v2.json"

BASE_RESOURCE = "MSG/JP/ev_strdata.bin"
PK_RESOURCE = "MSG_PK/JP/msgev.bin"
FONT_RESOURCE = "RES_JP/res_lang.bin"
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
MAX_LINES = 3
MAX_LINE_PX = 912
UNBOUNDED_PRINTF_ID = 16402

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
WIDE_SCRIPT_RE = re.compile(
    r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3\u3040-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9f\u3400-\u9fff\uf900-\ufaff]"
)
REVIEW_CLASSES = frozenset(
    {
        "already_fit_after_review",
        "protected_runtime_width_unknown_preserved",
        "reviewed_boundary_reflow",
        "reviewed_semantic_compaction",
    }
)


class LedgerError(ValueError):
    """Raised when the current installation no longer matches this no-op ledger."""


@dataclass(frozen=True)
class MessageResource:
    relative: str
    path: Path
    packed: bytes
    raw: bytes
    table: MessageTable


@dataclass(frozen=True)
class FontMetrics:
    packed: bytes
    raw: bytes
    table_offset: int

    def advance(self, character: str) -> int:
        codepoint = ord(character)
        if codepoint >= g1n.MAP_ENTRIES:
            raise LedgerError(f"event-font codepoint is outside table 0: U+{codepoint:04X}")
        ordinal = struct.unpack_from("<H", self.raw, self.table_offset + codepoint * 2)[0]
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character) is not None:
                return 48
            raise LedgerError(f"event-font glyph is absent: U+{codepoint:04X}")
        record_offset = self.table_offset + g1n.MAP_SIZE + ordinal * g1n.RECORD_SIZE
        if record_offset + g1n.RECORD_SIZE > len(self.raw):
            raise LedgerError(f"event-font record exceeds table: U+{codepoint:04X}")
        width = self.raw[record_offset]
        advance = self.raw[record_offset + 4]
        if width != advance or advance not in (24, 48):
            raise LedgerError(f"unexpected event-font metric: U+{codepoint:04X}")
        return advance


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise LedgerError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def coordinate_hash(ids: Iterable[int]) -> str:
    return sha256_bytes(canonical_json_bytes([{"id": item} for item in sorted(ids)]))


def file_spec(value: bytes) -> dict[str, Any]:
    return {"size": len(value), "sha256": sha256_bytes(value)}


def resource_path(steam_root: Path, relative: str) -> Path:
    root = steam_root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise LedgerError(f"resource escapes Steam root: {relative}") from exc
    return path


def read_contract() -> dict[str, Any]:
    try:
        contract = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"cannot read validation contract: {VALIDATION_PATH}") from exc
    if not isinstance(contract, dict):
        raise LedgerError("validation contract root is not an object")
    require(contract.get("schema"), SCHEMA, "validation schema")
    return contract


def read_message_resource(steam_root: Path, relative: str, expected: Mapping[str, Any]) -> MessageResource:
    path = resource_path(steam_root, relative)
    packed = path.read_bytes()
    require(file_spec(packed), expected.get("packed"), f"{relative} packed profile")
    _header, raw = decompress_wrapper(packed)
    require(file_spec(raw), expected.get("raw"), f"{relative} raw profile")
    table = parse_message_table(raw)
    require(table.string_count, expected.get("string_count"), f"{relative} string count")
    require(rebuild_message_table(table, table.texts), raw, f"{relative} raw parse/rebuild identity")
    return MessageResource(relative=relative, path=path, packed=packed, raw=raw, table=table)


def read_font(steam_root: Path, expected: Mapping[str, Any]) -> FontMetrics:
    path = resource_path(steam_root, FONT_RESOURCE)
    packed = path.read_bytes()
    require(file_spec(packed), expected.get("packed"), "event font packed profile")
    archive = parse_link(packed)
    if FONT_OUTER_ENTRY >= len(archive.entries):
        raise LedgerError("event font outer entry is absent")
    _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    require(file_spec(raw), expected.get("event_g1n_raw"), "event font G1N profile")
    if raw[:8] != g1n.MAGIC:
        raise LedgerError("event font G1N signature differs")
    table_count = struct.unpack_from("<I", raw, 0x1C)[0]
    if FONT_TABLE >= table_count:
        raise LedgerError("event font table 0 is absent")
    table_offset = struct.unpack_from("<I", raw, g1n.FIXED_HEADER_SIZE + FONT_TABLE * 4)[0]
    record_start = table_offset + g1n.MAP_SIZE
    if not (g1n.FIXED_HEADER_SIZE <= table_offset < record_start <= len(raw)):
        raise LedgerError("event font table 0 bounds differ")
    metrics = FontMetrics(packed=packed, raw=raw, table_offset=table_offset)
    samples = expected.get("sample_advances_px")
    require(
        {
            "ascii_space": metrics.advance(" "),
            "ellipsis": metrics.advance(chr(0x2026)),
            "hangul": metrics.advance(chr(0xAC00)),
        },
        samples,
        "event font sample advances",
    )
    return metrics


def visible_line_width(value: str, advance: Callable[[str], int]) -> int:
    width = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise LedgerError("malformed ESC-C token in event text")
            cursor += 3
            continue
        character = value[cursor]
        if unicodedata.category(character) == "Cc":
            raise LedgerError(f"unexpected control in visible text: U+{ord(character):04X}")
        width += advance(character)
        cursor += 1
    return width


def line_width_pairs(
    value: str,
    advance: Callable[[str], int],
    reservations: Mapping[str, int],
) -> tuple[list[int], list[int]]:
    actual: list[int] = []
    reserved: list[int] = []
    for line in common.LINE_BREAK_RE.sub("\n", value).split("\n"):
        visible = visible_line_width(line, advance)
        projected = visible
        for token in RUNTIME_RE.findall(line):
            if token not in reservations:
                raise LedgerError(f"runtime reservation is absent: {token}")
            projected += max(0, reservations[token] - visible_line_width(token, advance))
        actual.append(visible)
        reserved.append(projected)
    return actual, reserved


def current_hardbreak_ids(table: MessageTable) -> list[int]:
    return [
        identifier
        for identifier, value in enumerate(table.texts)
        if HANGUL_RE.search(value) is not None and common.LINE_BREAK_RE.search(value) is not None
    ]


def token_identifier(token: str) -> int:
    digits = "".join(character for character in token if "0" <= character <= "9")
    if not digits:
        raise LedgerError(f"runtime token has no numeric identifier: {token}")
    return int(digits)


def runtime_reservations(
    table: MessageTable,
    hardbreak_ids: Sequence[int],
    advance: Callable[[str], int],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    tokens = sorted({token for identifier in hardbreak_ids for token in RUNTIME_RE.findall(table.texts[identifier])})
    rows: list[dict[str, Any]] = []
    for token in tokens:
        name_id = token_identifier(token)
        if not 0 <= name_id < table.string_count:
            raise LedgerError(f"runtime token target is outside PK message table: {token}")
        name = table.texts[name_id]
        if common.LINE_BREAK_RE.search(name) is not None:
            raise LedgerError(f"runtime name unexpectedly has a hard line break: {token}")
        rows.append(
            {
                "token": token,
                "name_id": name_id,
                "name_utf16le_sha256": text_hash(name),
                "width_px": visible_line_width(name, advance),
            }
        )
    return {row["token"]: row["width_px"] for row in rows}, rows


def load_historic_audit(contract: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expected = contract.get("historic_v2_audit")
    if not isinstance(expected, Mapping):
        raise LedgerError("historic audit contract is absent")
    blob = V2_AUDIT_PATH.read_bytes()
    require(sha256_bytes(blob), expected.get("sha256"), "historic v2 audit hash")
    try:
        document = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError("historic v2 audit is unreadable") from exc
    require(document.get("resource"), PK_RESOURCE, "historic v2 audit resource")
    rows = document.get("rows")
    if not isinstance(rows, list):
        raise LedgerError("historic v2 audit rows are absent")
    ids: list[int] = []
    for row in rows:
        if not isinstance(row, dict) or type(row.get("id")) is not int:
            raise LedgerError("historic v2 audit row shape differs")
        ids.append(row["id"])
    require(len(rows), expected.get("hardbreak_rows"), "historic hardbreak row count")
    require(len(ids), len(set(ids)), "historic hardbreak IDs are unique")
    require(coordinate_hash(ids), expected.get("hardbreak_coordinate_sha256"), "historic hardbreak coordinate domain")
    review_rows = [row for row in rows if row.get("classification") in REVIEW_CLASSES]
    review_ids = [int(row["id"]) for row in review_rows]
    require(len(review_rows), expected.get("review_rows"), "historic review row count")
    require(len(review_ids), len(set(review_ids)), "historic review IDs are unique")
    require(coordinate_hash(review_ids), expected.get("review_coordinate_sha256"), "historic review coordinate domain")
    protected = [row for row in review_rows if row["id"] == UNBOUNDED_PRINTF_ID]
    require(len(protected), 1, "unbounded printf row presence")
    require(
        protected[0].get("classification"),
        "protected_runtime_width_unknown_preserved",
        "unbounded printf historic class",
    )
    return rows, review_rows


def reconciliation_ids(contract: Mapping[str, Any]) -> set[int]:
    reconciliation = contract.get("stale_v2_reconciliation")
    if not isinstance(reconciliation, Mapping):
        raise LedgerError("stale v2 reconciliation contract is absent")
    groups = reconciliation.get("groups")
    if not isinstance(groups, Mapping):
        raise LedgerError("stale v2 reconciliation groups are absent")
    collected: list[int] = []
    for label, values in groups.items():
        if not isinstance(label, str) or not isinstance(values, list) or not all(type(value) is int for value in values):
            raise LedgerError("stale v2 reconciliation group shape differs")
        collected.extend(values)
    if len(collected) != len(set(collected)):
        raise LedgerError("stale v2 reconciliation IDs are duplicated")
    require(len(collected), reconciliation.get("nonexact_target_count"), "stale v2 nonexact target count")
    require(
        int(reconciliation.get("exact_current_target_noop_count", -1)) + len(collected),
        reconciliation.get("prior_overlay_entry_count"),
        "stale v2 overlay reconciliation total",
    )
    return set(collected)


def verify(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    """Build a report entirely in memory; no Steam or candidate path is written."""

    contract = read_contract()
    profiles = contract.get("profiles")
    if not isinstance(profiles, Mapping):
        raise LedgerError("profile contract is absent")
    base = read_message_resource(steam_root, BASE_RESOURCE, profiles.get("base", {}))
    pk = read_message_resource(steam_root, PK_RESOURCE, profiles.get("pk", {}))
    font = read_font(steam_root, profiles.get("font", {}))

    base_anchor_contract = contract.get("base_event_anchors")
    if not isinstance(base_anchor_contract, Mapping):
        raise LedgerError("Base event anchor contract is absent")
    base_anchors: list[dict[str, Any]] = []
    for identifier_text, expected_hash in sorted(base_anchor_contract.items(), key=lambda item: int(item[0])):
        identifier = int(identifier_text)
        if not 0 <= identifier < base.table.string_count:
            raise LedgerError(f"Base event anchor is outside table: {identifier}")
        value = base.table.texts[identifier]
        require(text_hash(value), expected_hash, f"Base event anchor {identifier}")
        base_anchors.append(
            {
                "id": identifier,
                "utf16le_sha256": text_hash(value),
                "line_break_count": len(common.message_invariants(value)["line_breaks"]),
            }
        )

    historic_rows, review_rows = load_historic_audit(contract)
    historic_ids = {int(row["id"]) for row in historic_rows}
    review_ids = {int(row["id"]) for row in review_rows}
    current_ids = current_hardbreak_ids(pk.table)
    selection = contract.get("current_pk_selection")
    if not isinstance(selection, Mapping):
        raise LedgerError("current PK selection contract is absent")
    require(len(current_ids), selection.get("hardbreak_rows"), "current PK hardbreak row count")
    require(coordinate_hash(current_ids), selection.get("coordinate_sha256"), "current PK hardbreak coordinate domain")
    missing_historic = sorted(historic_ids - set(current_ids))
    new_ids = sorted(set(current_ids) - historic_ids)
    require(missing_historic, [], "historic hardbreak IDs missing from current PK")
    require(new_ids, selection.get("new_runtime_ids"), "new current hardbreak IDs")

    reservations, reservation_rows = runtime_reservations(pk.table, current_ids, font.advance)
    runtime = contract.get("runtime_reservations")
    if not isinstance(runtime, Mapping):
        raise LedgerError("runtime reservation contract is absent")
    require(len(reservation_rows), runtime.get("token_spelling_count"), "runtime token spelling count")
    require(len({row["name_id"] for row in reservation_rows}), runtime.get("name_id_count"), "runtime name ID count")
    require(
        sha256_bytes(canonical_json_bytes(reservation_rows)),
        runtime.get("rows_sha256"),
        "runtime reservation profile",
    )

    bounded_rows = 0
    maximum_actual = 0
    maximum_reserved = 0
    maximum_lines = 0
    for identifier in sorted(review_ids):
        value = pk.table.texts[identifier]
        actual, reserved = line_width_pairs(value, font.advance, reservations)
        invariants = common.message_invariants(value)
        if identifier == UNBOUNDED_PRINTF_ID:
            if not invariants["printf"]:
                raise LedgerError("unbounded printf row no longer contains a printf token")
            continue
        bounded_rows += 1
        if len(actual) > MAX_LINES or max(reserved, default=0) > MAX_LINE_PX:
            raise LedgerError(f"current bounded review row exceeds layout: {identifier}")
        maximum_actual = max(maximum_actual, max(actual, default=0))
        maximum_reserved = max(maximum_reserved, max(reserved, default=0))
        maximum_lines = max(maximum_lines, len(actual))

    layout_contract = contract.get("layout")
    if not isinstance(layout_contract, Mapping):
        raise LedgerError("layout contract is absent")
    require(bounded_rows, layout_contract.get("bounded_review_rows"), "bounded review count")
    require(maximum_lines, layout_contract.get("max_lines"), "bounded maximum line count")
    require(maximum_actual, layout_contract.get("max_actual_width_px"), "bounded maximum actual width")
    require(maximum_reserved, layout_contract.get("max_reserved_width_px"), "bounded maximum reserved width")

    new_metrics: list[dict[str, Any]] = []
    expected_new_widths = selection.get("new_runtime_reserved_widths_px")
    if not isinstance(expected_new_widths, Mapping):
        raise LedgerError("new runtime width contract is absent")
    for identifier in new_ids:
        value = pk.table.texts[identifier]
        tokens = RUNTIME_RE.findall(value)
        if not tokens:
            raise LedgerError(f"new hardbreak row has no runtime token: {identifier}")
        actual, reserved = line_width_pairs(value, font.advance, reservations)
        if len(actual) > MAX_LINES or max(reserved, default=0) > MAX_LINE_PX:
            raise LedgerError(f"new hardbreak row exceeds layout: {identifier}")
        require(reserved, expected_new_widths.get(str(identifier)), f"new hardbreak reservation widths {identifier}")
        new_metrics.append({"id": identifier, "actual_widths_px": actual, "reserved_widths_px": reserved, "tokens": tokens})

    reconciled = reconciliation_ids(contract)
    require(reconciled <= historic_ids, True, "reconciliation IDs remain within historic hardbreak domain")
    nonreview_reconciled = reconciled - review_ids
    reconciliation = contract["stale_v2_reconciliation"]
    require(
        len(nonreview_reconciled),
        reconciliation.get("historic_v1_reused_nonreview_count"),
        "historic v1-reused reconciliation count",
    )
    historic_class_by_id = {int(row["id"]): row.get("classification") for row in historic_rows}
    require(
        {historic_class_by_id[identifier] for identifier in nonreview_reconciled},
        {"v1_reused"},
        "historic nonreview reconciliation classifications",
    )
    nonexact_maximum_actual = 0
    nonexact_maximum_reserved = 0
    nonexact_maximum_lines = 0
    for identifier in sorted(reconciled):
        actual, reserved = line_width_pairs(pk.table.texts[identifier], font.advance, reservations)
        if len(actual) > MAX_LINES or max(reserved, default=0) > MAX_LINE_PX:
            raise LedgerError(f"current nonexact reconciliation row exceeds layout: {identifier}")
        nonexact_maximum_actual = max(nonexact_maximum_actual, max(actual, default=0))
        nonexact_maximum_reserved = max(nonexact_maximum_reserved, max(reserved, default=0))
        nonexact_maximum_lines = max(nonexact_maximum_lines, len(actual))
    require(
        nonexact_maximum_lines,
        reconciliation.get("current_bounded_max_lines"),
        "current nonexact reconciliation maximum line count",
    )
    require(
        nonexact_maximum_actual,
        reconciliation.get("current_bounded_max_actual_width_px"),
        "current nonexact reconciliation maximum actual width",
    )
    require(
        nonexact_maximum_reserved,
        reconciliation.get("current_bounded_max_reserved_width_px"),
        "current nonexact reconciliation maximum reserved width",
    )

    # A no-op candidate is the exact current PK input.  No message table is
    # rebuilt or recompressed, so there is no route to overwrite current text.
    no_op_candidate = {
        "resource": PK_RESOURCE,
        "mode": "current_resource_retained",
        "effective_change_count": 0,
        "packed": file_spec(pk.packed),
        "raw": file_spec(pk.raw),
    }

    # Detect an external mutation that happened after the source was parsed.
    require(sha256_path(base.path), sha256_bytes(base.packed), "Base Steam source changed during verification")
    require(sha256_path(pk.path), sha256_bytes(pk.packed), "PK Steam source changed during verification")
    require(
        sha256_path(resource_path(steam_root, FONT_RESOURCE)),
        sha256_bytes(font.packed),
        "event font changed during verification",
    )

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "profiles": {
            "base": {"resource": BASE_RESOURCE, "packed": file_spec(base.packed), "raw": file_spec(base.raw), "string_count": base.table.string_count},
            "pk": {"resource": PK_RESOURCE, "packed": file_spec(pk.packed), "raw": file_spec(pk.raw), "string_count": pk.table.string_count},
            "font": {
                "resource": FONT_RESOURCE,
                "packed": file_spec(font.packed),
                "event_g1n_raw": file_spec(font.raw),
                "outer_entry": FONT_OUTER_ENTRY,
                "table": FONT_TABLE,
            },
        },
        "base_event_anchors": base_anchors,
        "selection": {
            "historic_hardbreak_rows": len(historic_rows),
            "current_hardbreak_rows": len(current_ids),
            "current_coordinate_sha256": coordinate_hash(current_ids),
            "new_runtime_rows": new_metrics,
            "historic_review_rows": len(review_rows),
            "bounded_review_rows": bounded_rows,
            "unbounded_printf_preserved_id": UNBOUNDED_PRINTF_ID,
        },
        "runtime_reservations": {
            "token_spelling_count": len(reservation_rows),
            "name_id_count": len({row["name_id"] for row in reservation_rows}),
            "rows_sha256": sha256_bytes(canonical_json_bytes(reservation_rows)),
        },
        "layout": {
            "max_lines": maximum_lines,
            "max_actual_width_px": maximum_actual,
            "max_reserved_width_px": maximum_reserved,
            "limit": {"max_lines": MAX_LINES, "max_reserved_width_px": MAX_LINE_PX},
        },
        "stale_v2_reconciliation": {
            "target_overlay_read": False,
            "target_overlay_reinjected": False,
            "nonexact_target_ids": sorted(reconciled),
            "nonexact_target_count": len(reconciled),
            "historic_v1_reused_nonreview_count": len(nonreview_reconciled),
            "current_bounded_max_lines": nonexact_maximum_lines,
            "current_bounded_max_actual_width_px": nonexact_maximum_actual,
            "current_bounded_max_reserved_width_px": nonexact_maximum_reserved,
            "exact_current_target_noop_count": contract["stale_v2_reconciliation"]["exact_current_target_noop_count"],
        },
        "candidate": no_op_candidate,
        "safety": {
            "steam_files_written": False,
            "candidate_files_written": False,
            "font_resources_touched": False,
            "old_v2_target_overlay_reinjected": False,
            "git_written": False,
            "release_written": False,
        },
    }


def build_noop(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    """Alias for the no-op build proof; it intentionally has no output path."""

    report = verify(steam_root)
    require(report["candidate"]["effective_change_count"], 0, "no-op candidate change count")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "build"), help="both commands are read-only and emit JSON to stdout")
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args(argv)
    try:
        report = verify(args.steam_root) if args.command == "verify" else build_noop(args.steam_root)
    except (LedgerError, OSError, ValueError, struct.error) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    report["command"] = args.command
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
