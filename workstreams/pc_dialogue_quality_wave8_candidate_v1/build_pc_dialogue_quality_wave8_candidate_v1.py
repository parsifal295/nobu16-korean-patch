#!/usr/bin/env python3
"""Build the conservative PC-only Wave 8 dialogue candidate without writing Steam.

Wave 8 consumes the already reviewed PC-only quality-triage catalogues.  It
repairs thirty logical character-dialogue candidates (48 ``msggame`` records:
Base 18 / PK 30) and five PK Okehazama event entries.  The builder is pinned
to the installed Wave 7 profile, preserves every non-``0143`` opaque byte and
every manual line break, and validates the event entries against the existing
PK 3-line / 912px layout methodology.  It deliberately has no write-to-Steam
operation; scene QA remains required before any release decision.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
WAVE7_SCRIPT = (
    REPO
    / "workstreams"
    / "pc_dialogue_goodwill_runtime_wave7_v1"
    / "build_pc_dialogue_goodwill_runtime_wave7_v1.py"
)
TRIAGE_DIR = REPO / "workstreams" / "pc_dialogue_quality_triage_v1"
TRIAGE_MSGGAME = TRIAGE_DIR / "pc_dialogue_quality_triage_candidates.v1.json"
TRIAGE_EVENT = TRIAGE_DIR / "pk_msgev_okehazama_4494_4510_priority.v1.json"
AUDIT_PATH = WORKSTREAM / "audit_pc_dialogue_quality_wave8.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave8-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave8-audit.v1"
TRANSACTION_ID = "pc-dialogue-quality-wave8-candidate-v1"
EVENT_RESOURCE = "MSG_PK/JP/msgev.bin"
MSGGAME_RESOURCES = ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin")
CHANGED_PATHS = (*MSGGAME_RESOURCES, EVENT_RESOURCE)
EXPECTED_LOGICAL_DIALOGUE_CANDIDATES = tuple(f"C{index:02d}" for index in range(1, 31))
EXPECTED_EVENT_IDS = (4495, 4502, 4506, 4508, 4509)
EXPECTED_MSGGAME_RECORD_COUNTS = {"MSG/JP/msggame.bin": 18, "MSG_PK/JP/msggame.bin": 30}
EXPECTED_EVENT_STRING_COUNT = 17_916
MAX_EVENT_LINES = 3
MAX_EVENT_LINE_PX = 912
TRIAGE_MSGGAME_SHA256 = "FC79A141D2B0D69978F74D217B2A4606D3BAA146F83A5D3D4D06FFA7DB91FD0E"
TRIAGE_EVENT_SHA256 = "D9BA5F076037B583774973349C1A7439A7BB985076299DD6D324C4FDE6DE6CC9"
PRISTINE_EVENT_PATH = (
    DEFAULT_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
PRISTINE_EVENT_SHA256 = "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84"


class Wave8Error(ValueError):
    """The fixed PC-only source or preservation contract changed."""


def load_wave7() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_wave7_for_wave8", WAVE7_SCRIPT)
    if spec is None or spec.loader is None:
        raise Wave8Error(f"cannot load Wave 7 builder: {WAVE7_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE7 = load_wave7()
WAVE6 = WAVE7.WAVE6
WAVE5 = WAVE6.WAVE5
WAVE4 = WAVE6.WAVE4
PROFILE_PATHS = tuple(WAVE7.PROFILE_PATHS)
INPUT_SHA256 = dict(WAVE7.TARGET_SHA256)

TARGET_SHA256 = {
    **INPUT_SHA256,
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG_PK/JP/msggame.bin": "454A18B0F0ED5E39A3AC823AD0A30086C25226BF6E48D4580962DFEE84E24A32",
    "MSG_PK/JP/msgev.bin": "1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave8Error(f"{label} escapes allowed root: {resolved_path}") from exc
    return resolved_path


def require_tmp_path(path: Path, label: str) -> Path:
    return require_under(REPO / "tmp" / WORKSTREAM.name, path, label)


def profile_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = require_under(root, root / relative, f"profile resource {relative}")
        if not path.is_file():
            raise Wave8Error(f"profile resource is absent: {relative}")
        hashes[relative] = sha256_path(path)
    return hashes


def assert_profile(root: Path, expected: dict[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual != expected:
        mismatches = {
            path: {"actual": actual.get(path), "expected": expected.get(path)}
            for path in PROFILE_PATHS
            if actual.get(path) != expected.get(path)
        }
        raise Wave8Error(f"{label} profile differs: {json.dumps(mismatches, sort_keys=True)}")


def parse_coordinate(value: object) -> tuple[int, int]:
    if not isinstance(value, str):
        raise Wave8Error(f"invalid coordinate: {value!r}")
    try:
        block, record = value.split(":", 1)
        return int(block), int(record)
    except ValueError as exc:
        raise Wave8Error(f"invalid coordinate: {value!r}") from exc


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def literal_tuple(record: Any) -> tuple[str, ...]:
    return tuple(item.text for item in WAVE4.parse_record_literals(record))


def literal_layout(literals: tuple[str, ...], advance: Any) -> dict[str, object]:
    merged = "".join(literals)
    widths = [sum(advance(character) for character in line) for line in merged.split("\n")]
    return {"line_count": len(widths), "widths_px": widths}


def output_literal_slots(text: str, current_literals: tuple[str, ...]) -> tuple[str, ...]:
    """Split only the literal container, never the rendered Korean text.

    The JP-only ``0143`` commands split the current static message into several
    literal slots.  Removing them must not remove a slot or change its opaque
    neighbours.  This deterministic proportional split keeps all slots nonempty
    while concatenating exactly to the reviewed Korean sentence.
    """
    if not text or not current_literals or any(not item for item in current_literals):
        raise Wave8Error("static record has an empty literal slot")
    count = len(current_literals)
    if len(text) < count:
        raise Wave8Error("reviewed Korean text is too short for its pinned literal topology")
    weights = [len(item) for item in current_literals]
    total = sum(weights)
    cuts: list[int] = []
    previous = 0
    cumulative = 0
    for index, weight in enumerate(weights[:-1], start=1):
        cumulative += weight
        nominal = round(len(text) * cumulative / total)
        minimum = previous + 1
        maximum = len(text) - (count - index)
        cut = max(minimum, min(maximum, nominal))
        # Use a nearby whitespace boundary when it is available, but keep the
        # exact full text and a nonempty remainder contract.
        nearby = [
            point
            for point in range(max(minimum, cut - 5), min(maximum, cut + 5) + 1)
            if text[point - 1].isspace() or text[point].isspace()
        ]
        if nearby:
            cut = min(nearby, key=lambda point: (abs(point - nominal), point))
        cuts.append(cut)
        previous = cut
    parts: list[str] = []
    start = 0
    for cut in (*cuts, len(text)):
        parts.append(text[start:cut])
        start = cut
    result = tuple(parts)
    if len(result) != count or any(not item for item in result) or "".join(result) != text:
        raise Wave8Error("literal topology split differs")
    return result


def triage_documents() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if sha256_path(TRIAGE_MSGGAME) != TRIAGE_MSGGAME_SHA256:
        raise Wave8Error("PC-only msggame triage artifact hash differs")
    if sha256_path(TRIAGE_EVENT) != TRIAGE_EVENT_SHA256:
        raise Wave8Error("PC-only Okehazama triage artifact hash differs")
    message_rows = json.loads(TRIAGE_MSGGAME.read_text(encoding="utf-8"))
    event_document = json.loads(TRIAGE_EVENT.read_text(encoding="utf-8"))
    if not isinstance(message_rows, list) or len(message_rows) != len(EXPECTED_LOGICAL_DIALOGUE_CANDIDATES):
        raise Wave8Error("msgame triage row count differs")
    if tuple(row.get("id") for row in message_rows) != EXPECTED_LOGICAL_DIALOGUE_CANDIDATES:
        raise Wave8Error("msggame triage candidate order differs")
    policy = event_document.get("source_policy") if isinstance(event_document, dict) else None
    if not isinstance(policy, dict) or policy.get("switch_korean_translation_used") is not False:
        raise Wave8Error("event triage source policy is not PC-only")
    event_rows = event_document.get("candidates") if isinstance(event_document, dict) else None
    if not isinstance(event_rows, list) or tuple(row.get("id") for row in event_rows) != EXPECTED_EVENT_IDS:
        raise Wave8Error("Okehazama triage candidate order differs")
    for row in message_rows:
        scope = row.get("scope")
        if scope != "PC character dialogue / static 0143 cleanup":
            raise Wave8Error(f"unexpected dialogue triage scope: {scope!r}")
        targets = row.get("targets")
        if not isinstance(targets, dict) or "pk" not in targets:
            raise Wave8Error(f"triage targets are absent for {row.get('id')}")
        contract = row.get("safe_apply_contract")
        if not isinstance(contract, dict) or contract.get("runtime_tokens_present") is not False:
            raise Wave8Error(f"triage runtime contract differs for {row.get('id')}")
    return message_rows, event_rows


def record_removals(target: dict[str, Any]) -> tuple[Any, ...]:
    raw = target.get("current_0143_commands")
    if not isinstance(raw, list) or not raw:
        raise Wave8Error("static triage removal list is absent")
    removals: list[Any] = []
    seen: set[int] = set()
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("offset"), int) or not isinstance(item.get("hex"), str):
            raise Wave8Error("static triage removal contract is malformed")
        offset = item["offset"]
        if offset in seen:
            raise Wave8Error("static triage removal offset is duplicated")
        seen.add(offset)
        removals.append(WAVE4.remove_command(offset, item["hex"]))
    return tuple(removals)


def resource_for_target(name: str) -> str:
    if name == "base":
        return "MSG/JP/msggame.bin"
    if name == "pk":
        return "MSG_PK/JP/msggame.bin"
    raise Wave8Error(f"unexpected triage target family: {name!r}")


def verify_pc_japanese_source(resource: str, coordinate: tuple[int, int], expected_text: str) -> Any:
    source_path, source_hash = WAVE4.WAVE3.PRISTINE_SOURCES[resource]
    if sha256_path(source_path) != source_hash:
        raise Wave8Error(f"pristine PC Japanese resource hash differs: {resource}")
    record = WAVE4.records_by_coordinate(source_path.read_bytes()).get(coordinate)
    if record is None:
        raise Wave8Error(f"pristine PC Japanese record is absent: {resource} {coordinate_text(coordinate)}")
    if "".join(literal_tuple(record)) != expected_text:
        raise Wave8Error(f"pristine PC Japanese text differs: {resource} {coordinate_text(coordinate)}")
    return record


def validate_static_record_from_triage(
    steam_root: Path,
    candidate: dict[str, Any],
    family: str,
    target: dict[str, Any],
    advance: Any,
) -> dict[str, Any]:
    resource = resource_for_target(family)
    coordinate = parse_coordinate(target.get("coordinate"))
    current = WAVE4.records_by_coordinate((steam_root / resource).read_bytes()).get(coordinate)
    if current is None:
        raise Wave8Error(f"current record is absent: {resource} {coordinate_text(coordinate)}")
    current_literals = literal_tuple(current)
    if sha256_bytes(current.data) != target.get("current_record_sha256"):
        raise Wave8Error(f"current record hash differs: {resource} {coordinate_text(coordinate)}")
    if current_literals != tuple(target.get("current_literals", ())):
        raise Wave8Error(f"current literal tuple differs: {resource} {coordinate_text(coordinate)}")
    if "".join(current_literals) != candidate.get("current_korean"):
        raise Wave8Error(f"current Korean text differs: {resource} {coordinate_text(coordinate)}")
    current_opaque = WAVE4.opaque_bytes(current)
    if current_opaque.hex().upper() != target.get("static_opaque_bytes"):
        raise Wave8Error(f"static opaque bytes differ: {resource} {coordinate_text(coordinate)}")
    removals = record_removals(target)
    expected_commands = tuple((item.offset, item.value) for item in removals)
    if WAVE4.opaque_commands(current) != expected_commands:
        raise Wave8Error(f"JP-only 0143 commands differ: {resource} {coordinate_text(coordinate)}")
    WAVE7.verify_non_japanese_structure(steam_root, resource, coordinate)
    source = verify_pc_japanese_source(resource, coordinate, target.get("pristine_pc_japanese"))
    recommended = candidate.get("recommended_korean")
    if not isinstance(recommended, str) or not recommended:
        raise Wave8Error(f"recommended Korean is absent: {candidate.get('id')}")
    output_literals = output_literal_slots(recommended, current_literals)
    if sum(item.count("\n") for item in current_literals) != sum(item.count("\n") for item in output_literals):
        raise Wave8Error(f"manual line breaks differ: {resource} {coordinate_text(coordinate)}")
    changes = tuple(
        WAVE4.change(index, before, after)
        for index, (before, after) in enumerate(zip(current_literals, output_literals))
        if before != after
    )
    if not changes:
        raise Wave8Error(f"static repair is a no-op: {resource} {coordinate_text(coordinate)}")
    plan = WAVE4.plan(coordinate[0], coordinate[1], sha256_bytes(current.data), changes, remove_commands=removals)
    replacement_map = {index: text for index, text in enumerate(output_literals)}
    output_data = WAVE4.rebuild_quality_record(current, plan, replacement_map)
    output = type(current)(current.block_id, current.record_id, current.relative_offset, output_data)
    expected_opaque = WAVE4.expected_opaque_after_removals(current, plan)
    if WAVE4.opaque_bytes(output) != expected_opaque or expected_opaque != b"\x05\x05\x05":
        raise Wave8Error(f"output opaque bytes differ: {resource} {coordinate_text(coordinate)}")
    if WAVE4.opaque_commands(output):
        raise Wave8Error(f"output retains a JP-only 0143 command: {resource} {coordinate_text(coordinate)}")
    if literal_tuple(output) != output_literals:
        raise Wave8Error(f"output literal tuple differs: {resource} {coordinate_text(coordinate)}")
    before_layout = literal_layout(current_literals, advance)
    after_layout = literal_layout(output_literals, advance)
    if before_layout["line_count"] != after_layout["line_count"]:
        raise Wave8Error(f"output line count differs: {resource} {coordinate_text(coordinate)}")
    if after_layout["line_count"] > MAX_EVENT_LINES:
        raise Wave8Error(f"dialogue exceeds three manual lines: {resource} {coordinate_text(coordinate)}")
    return {
        "candidate_id": candidate["id"],
        "kind": "msggame_static_0143_cleanup",
        "resource": resource,
        "coordinate": coordinate_text(coordinate),
        "current_record_sha256": sha256_bytes(current.data),
        "output_record_sha256": sha256_bytes(output.data),
        "current_literals": list(current_literals),
        "output_literals": list(output_literals),
        "current_opaque_hex": current_opaque.hex().upper(),
        "output_opaque_hex": expected_opaque.hex().upper(),
        "remove_0143_commands": [[item.offset, item.expected_hex] for item in removals],
        "manual_line_count": before_layout["line_count"],
        "literal_layout": {"before": before_layout, "after": after_layout},
        "pristine_pc_jp_record_sha256": sha256_bytes(source.data),
        "pristine_pc_jp_literals": list(literal_tuple(source)),
        "pristine_pc_jp_opaque_hex": WAVE4.opaque_bytes(source).hex().upper(),
        "pc_reference_languages_checked": ["EN", "SC", "TC"] if family == "pk" else ["SC", "TC"],
        "real_game_qa_required_before_release": True,
    }


def event_format_contract(value: str) -> dict[str, Any]:
    return {
        "protected": WAVE5.event_protected_contract(value),
        "linebreak_vector": WAVE5.EVENT_LINEBREAK_RE.findall(value),
        "manual_line_count": WAVE5.event_line_count(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
    }


def event_reservations(table: Any, text: str, advance: Any) -> dict[str, int]:
    reservations: dict[str, int] = {}
    for token in WAVE5.EVENT_RUNTIME_BRACKET_RE.findall(text):
        if token in reservations:
            continue
        match = WAVE5.EVENT_RUNTIME_TOKEN_RE.fullmatch(token)
        if match is None:
            raise Wave8Error(f"event runtime token is malformed: {token}")
        source_id = int(match.group(2))
        if source_id >= table.string_count:
            raise Wave8Error(f"event runtime token is out of range: {token}")
        reservations[token] = WAVE5.event_visible_line_width(table.texts[source_id], advance)
        if reservations[token] <= 0:
            raise Wave8Error(f"event runtime reservation is empty: {token}")
    return reservations


def event_layout(table: Any, text: str, advance: Any) -> dict[str, Any]:
    reservations = event_reservations(table, text, advance)
    actual, reserved = WAVE5.event_measure_text_widths(text, advance, reservations)
    if len(actual) > MAX_EVENT_LINES or max(reserved, default=0) > MAX_EVENT_LINE_PX:
        raise Wave8Error(
            f"event static layout exceeds {MAX_EVENT_LINES} lines/{MAX_EVENT_LINE_PX}px: "
            f"lines={len(actual)} reserved={reserved}"
        )
    return {
        "actual_line_width_px": actual,
        "reserved_line_width_px": reserved,
        "line_count": len(actual),
        "runtime_reservations_px": reservations,
        "limit": {"max_lines": MAX_EVENT_LINES, "max_reserved_width_px": MAX_EVENT_LINE_PX},
    }


def event_candidate_output(table: Any, event_rows: list[dict[str, Any]], advance: Any) -> tuple[bytes, dict[str, Any]]:
    texts = list(table.texts)
    audit_rows: list[dict[str, Any]] = []
    for candidate in event_rows:
        entry_id = candidate["id"]
        current = candidate.get("current_korean")
        output = candidate.get("recommended_korean")
        source = candidate.get("pc_japanese")
        if not isinstance(current, str) or not isinstance(output, str) or not isinstance(source, str):
            raise Wave8Error(f"event candidate text is malformed: {entry_id}")
        if table.texts[entry_id] != current:
            raise Wave8Error(f"current PC event text differs: {entry_id}")
        if event_format_contract(current) != event_format_contract(output):
            raise Wave8Error(f"event format/token contract differs: {entry_id}")
        before_layout = event_layout(table, current, advance)
        after_layout = event_layout(table, output, advance)
        texts[entry_id] = output
        audit_rows.append(
            {
                "candidate_id": entry_id,
                "kind": "pk_msgev_okehazama_static_repair",
                "resource": EVENT_RESOURCE,
                "coordinate": entry_id,
                "current_utf16le_sha256": WAVE5.event_text_sha256(current),
                "output_utf16le_sha256": WAVE5.event_text_sha256(output),
                "current_literal": current,
                "output_literal": output,
                "pc_japanese_literal": source,
                "format_contract": event_format_contract(current),
                "layout": {"before": before_layout, "after": after_layout},
                "real_game_qa_required_before_release": True,
            }
        )
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, table._wave8_header)  # type: ignore[attr-defined]
    return candidate, {"rows": audit_rows, "raw": candidate_raw, "texts": texts}


def pristine_event_table() -> Any:
    if sha256_path(PRISTINE_EVENT_PATH) != PRISTINE_EVENT_SHA256:
        raise Wave8Error("pristine PC Japanese Okehazama source hash differs")
    _header, raw = decompress_wrapper(PRISTINE_EVENT_PATH.read_bytes())
    table = parse_message_table(raw)
    if table.string_count != EXPECTED_EVENT_STRING_COUNT:
        raise Wave8Error("pristine PC Japanese event table count differs")
    return table


def make_audit(steam_root: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    assert_profile(steam_root, INPUT_SHA256, "Wave 8 Steam input")
    message_candidates, event_candidates = triage_documents()
    advance = WAVE5.validate_event_pk_font_support(steam_root)
    message_rows: list[dict[str, Any]] = []
    for candidate in message_candidates:
        targets = candidate["targets"]
        for family in ("base", "pk"):
            target = targets.get(family)
            if target is None:
                continue
            if not isinstance(target, dict):
                raise Wave8Error(f"malformed triage target: {candidate['id']} {family}")
            message_rows.append(validate_static_record_from_triage(steam_root, candidate, family, target, advance))
    message_rows.sort(key=lambda row: (row["resource"], parse_coordinate(row["coordinate"])))
    grouped = Counter(row["resource"] for row in message_rows)
    if dict(grouped) != EXPECTED_MSGGAME_RECORD_COUNTS:
        raise Wave8Error(f"Wave 8 msggame record counts differ: {dict(grouped)}")
    if len({(row["resource"], row["coordinate"]) for row in message_rows}) != len(message_rows):
        raise Wave8Error("Wave 8 msggame coordinate is duplicated")

    event_path = steam_root / EVENT_RESOURCE
    packed = event_path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if table.string_count != EXPECTED_EVENT_STRING_COUNT or rebuild_message_table(table, table.texts) != raw:
        raise Wave8Error("current PC event table cannot be rebuilt byte-exactly")
    # Keep the wrapper header out of the published audit object but pass it to
    # the event builder without a mutable global.
    object.__setattr__(table, "_wave8_header", header)
    pristine = pristine_event_table()
    for candidate in event_candidates:
        if pristine.texts[candidate["id"]] != candidate["pc_japanese"]:
            raise Wave8Error(f"pristine PC Japanese event text differs: {candidate['id']}")
    event_packed, event_result = event_candidate_output(table, event_candidates, advance)
    event_header, event_raw = decompress_wrapper(event_packed)
    event_table = parse_message_table(event_raw)
    if event_header.prefix != header.prefix or rebuild_message_table(event_table, event_table.texts) != event_raw:
        raise Wave8Error("candidate PC event wrapper/table round trip differs")
    changed_ids = {
        index for index, (before, after) in enumerate(zip(table.texts, event_table.texts)) if before != after
    }
    if tuple(sorted(changed_ids)) != EXPECTED_EVENT_IDS:
        raise Wave8Error(f"Wave 8 event coordinate set differs: {sorted(changed_ids)}")
    for row in event_result["rows"]:
        entry_id = row["coordinate"]
        if event_table.texts[entry_id] != row["output_literal"]:
            raise Wave8Error(f"candidate PC event literal differs: {entry_id}")

    return {
        "schema": AUDIT_SCHEMA,
        "scope": {
            "platform": "Steam PC",
            "allowed_sources": ["PC Japanese", "PC English", "PC Simplified Chinese", "PC Traditional Chinese", "current PC Korean"],
            "excluded_sources": ["Switch Korean"],
            "steam_game_resource_written": False,
        },
        "input_profile_sha256": INPUT_SHA256,
        "triage_inputs": {
            "msggame_path": str(TRIAGE_MSGGAME.relative_to(REPO)).replace("\\", "/"),
            "msggame_sha256": TRIAGE_MSGGAME_SHA256,
            "msgev_path": str(TRIAGE_EVENT.relative_to(REPO)).replace("\\", "/"),
            "msgev_sha256": TRIAGE_EVENT_SHA256,
        },
        "summary": {
            "logical_msggame_candidates": len(message_candidates),
            "msggame_record_count": len(message_rows),
            "msggame_record_counts": dict(sorted(grouped.items())),
            "pk_msgev_entry_count": len(event_result["rows"]),
            "total_changed_records_or_entries": len(message_rows) + len(event_result["rows"]),
            "real_game_qa_required_before_release": True,
        },
        "msggame_records": message_rows,
        "pk_msgev": {
            "resource": EVENT_RESOURCE,
            "input_packed_sha256": sha256_bytes(packed),
            "input_raw_sha256": sha256_bytes(raw),
            "output_packed_sha256": sha256_bytes(event_packed),
            "output_raw_sha256": sha256_bytes(event_result["raw"]),
            "string_count": table.string_count,
            "records": event_result["rows"],
        },
    }


def read_audit(steam_root: Path) -> dict[str, Any]:
    if not AUDIT_PATH.is_file():
        raise Wave8Error(f"Wave 8 audit is absent: {AUDIT_PATH}")
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    regenerated = make_audit(steam_root)
    if canonical_json(audit) != canonical_json(regenerated):
        raise Wave8Error("Wave 8 audit differs from the fixed PC-only source regeneration")
    return audit


def audit_rows_by_resource(audit: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    records = audit.get("msggame_records")
    if not isinstance(records, list):
        raise Wave8Error("Wave 8 msggame audit records are absent")
    grouped: dict[str, list[dict[str, Any]]] = {resource: [] for resource in MSGGAME_RESOURCES}
    for row in records:
        if not isinstance(row, dict) or row.get("resource") not in grouped:
            raise Wave8Error("Wave 8 msggame audit resource differs")
        grouped[row["resource"]].append(row)
    return grouped


def row_removals(row: dict[str, Any]) -> tuple[Any, ...]:
    raw = row.get("remove_0143_commands")
    if not isinstance(raw, list):
        raise Wave8Error(f"audit removal list absent: {row.get('coordinate')}")
    return tuple(WAVE4.remove_command(offset, value) for offset, value in raw)


def rebuild_msggame_resource(source: bytes, resource: str, rows: list[dict[str, Any]]) -> bytes:
    before = WAVE4.records_by_coordinate(source)
    replacements: dict[tuple[int, int], bytes] = {}
    for row in rows:
        coordinate = parse_coordinate(row["coordinate"])
        current = before.get(coordinate)
        if current is None:
            raise Wave8Error(f"current resource record absent: {resource} {coordinate_text(coordinate)}")
        current_literals = literal_tuple(current)
        output_literals = tuple(row.get("output_literals", ()))
        if sha256_bytes(current.data) != row.get("current_record_sha256"):
            raise Wave8Error(f"current resource record hash differs: {resource} {coordinate_text(coordinate)}")
        if current_literals != tuple(row.get("current_literals", ())):
            raise Wave8Error(f"current resource literals differ: {resource} {coordinate_text(coordinate)}")
        if len(current_literals) != len(output_literals) or any(not item for item in output_literals):
            raise Wave8Error(f"output literal topology differs: {resource} {coordinate_text(coordinate)}")
        removals = row_removals(row)
        if WAVE4.opaque_bytes(current).hex().upper() != row.get("current_opaque_hex"):
            raise Wave8Error(f"current opaque bytes differ: {resource} {coordinate_text(coordinate)}")
        changes = tuple(
            WAVE4.change(index, before_text, after_text)
            for index, (before_text, after_text) in enumerate(zip(current_literals, output_literals))
            if before_text != after_text
        )
        plan = WAVE4.plan(coordinate[0], coordinate[1], row["current_record_sha256"], changes, remove_commands=removals)
        replacements[coordinate] = WAVE4.rebuild_quality_record(
            current, plan, {index: text for index, text in enumerate(output_literals)}
        )
    rebuilt = WAVE4.rebuild_packed_msggame(source, replacements)
    after = WAVE4.records_by_coordinate(rebuilt)
    if set(before) != set(after):
        raise Wave8Error(f"record topology changed: {resource}")
    changed = {coordinate for coordinate, item in before.items() if item.data != after[coordinate].data}
    expected = {parse_coordinate(row["coordinate"]) for row in rows}
    if changed != expected:
        raise Wave8Error(f"changed record set differs: {resource} {sorted(changed)}")
    for row in rows:
        coordinate = parse_coordinate(row["coordinate"])
        output = after[coordinate]
        if sha256_bytes(output.data) != row.get("output_record_sha256"):
            raise Wave8Error(f"output record hash differs: {resource} {coordinate_text(coordinate)}")
        if literal_tuple(output) != tuple(row["output_literals"]):
            raise Wave8Error(f"output literals differ: {resource} {coordinate_text(coordinate)}")
        if WAVE4.opaque_bytes(output).hex().upper() != row.get("output_opaque_hex"):
            raise Wave8Error(f"output opaque bytes differ: {resource} {coordinate_text(coordinate)}")
        if WAVE4.opaque_commands(output):
            raise Wave8Error(f"output retains an 0143 command: {resource} {coordinate_text(coordinate)}")
    return rebuilt


def rebuild_event_resource(source: bytes, audit: dict[str, Any], steam_root: Path) -> bytes:
    event = audit.get("pk_msgev")
    if not isinstance(event, dict):
        raise Wave8Error("Wave 8 event audit is absent")
    if sha256_bytes(source) != event.get("input_packed_sha256"):
        raise Wave8Error("current event packed hash differs")
    header, raw = decompress_wrapper(source)
    table = parse_message_table(raw)
    if sha256_bytes(raw) != event.get("input_raw_sha256") or rebuild_message_table(table, table.texts) != raw:
        raise Wave8Error("current event raw table differs")
    rows = event.get("records")
    if not isinstance(rows, list) or tuple(row.get("coordinate") for row in rows) != EXPECTED_EVENT_IDS:
        raise Wave8Error("event audit coordinates differ")
    advance = WAVE5.validate_event_pk_font_support(steam_root)
    texts = list(table.texts)
    for row in rows:
        entry_id = row["coordinate"]
        if table.texts[entry_id] != row.get("current_literal"):
            raise Wave8Error(f"event current literal differs: {entry_id}")
        if WAVE5.event_text_sha256(table.texts[entry_id]) != row.get("current_utf16le_sha256"):
            raise Wave8Error(f"event current literal hash differs: {entry_id}")
        if event_format_contract(table.texts[entry_id]) != row.get("format_contract"):
            raise Wave8Error(f"event protected contract differs: {entry_id}")
        before_layout = event_layout(table, table.texts[entry_id], advance)
        if before_layout != row.get("layout", {}).get("before"):
            raise Wave8Error(f"event current layout differs: {entry_id}")
        output = row.get("output_literal")
        if not isinstance(output, str) or event_format_contract(output) != row.get("format_contract"):
            raise Wave8Error(f"event output protected contract differs: {entry_id}")
        after_layout = event_layout(table, output, advance)
        if after_layout != row.get("layout", {}).get("after"):
            raise Wave8Error(f"event output layout differs: {entry_id}")
        texts[entry_id] = output
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, header)
    result_header, result_raw = decompress_wrapper(candidate)
    result_table = parse_message_table(result_raw)
    if result_header.prefix != header.prefix or result_raw != candidate_raw or rebuild_message_table(result_table, result_table.texts) != candidate_raw:
        raise Wave8Error("candidate event wrapper/table differs")
    changed = {index for index, (before, after) in enumerate(zip(table.texts, result_table.texts)) if before != after}
    if tuple(sorted(changed)) != EXPECTED_EVENT_IDS:
        raise Wave8Error(f"candidate event changed set differs: {sorted(changed)}")
    if sha256_bytes(candidate_raw) != event.get("output_raw_sha256") or sha256_bytes(candidate) != event.get("output_packed_sha256"):
        raise Wave8Error("candidate event hash differs")
    return candidate


def construct_resources(steam_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    audit = read_audit(steam_root)
    by_resource = audit_rows_by_resource(audit)
    resources = {
        resource: rebuild_msggame_resource((steam_root / resource).read_bytes(), resource, by_resource[resource])
        for resource in MSGGAME_RESOURCES
    }
    resources[EVENT_RESOURCE] = rebuild_event_resource((steam_root / EVENT_RESOURCE).read_bytes(), audit, steam_root)
    return resources, audit


def target_is_pinned() -> bool:
    return all(isinstance(TARGET_SHA256.get(path), str) and TARGET_SHA256[path] for path in PROFILE_PATHS)


def build_candidate(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    output_root = require_tmp_path(output_root, "candidate output")
    manifest_path = require_tmp_path(manifest_path, "manifest output")
    if output_root.exists():
        raise Wave8Error(f"candidate output already exists: {output_root}")
    if not target_is_pinned():
        raise Wave8Error("Wave 8 target profile is not pinned")
    assert_profile(steam_root, INPUT_SHA256, "Wave 8 Steam input")
    resources, audit = construct_resources(steam_root)
    for resource, value in resources.items():
        if sha256_bytes(value) != TARGET_SHA256[resource]:
            raise Wave8Error(f"target resource SHA-256 differs: {resource}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require_under(steam_root, steam_root / relative, relative), target)
        for relative, value in resources.items():
            (stage / relative).write_bytes(value)
        output_hashes = profile_hashes(stage)
        if output_hashes != TARGET_SHA256:
            raise Wave8Error("candidate output full profile differs")
        manifest = {
            "schema": SCHEMA,
            "transaction_id": TRANSACTION_ID,
            "changed_paths": list(CHANGED_PATHS),
            "input_sha256": INPUT_SHA256,
            "output_sha256": output_hashes,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_path": str(AUDIT_PATH.relative_to(REPO)).replace("\\", "/"),
            "audit_sha256": sha256_path(AUDIT_PATH),
            "summary": audit["summary"],
            "real_game_qa_required_before_release": True,
            "steam_write_capability": "absent; this workstream builds candidates only",
        }
        os.replace(stage, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(manifest))
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def write_audit(steam_root: Path) -> dict[str, Any]:
    steam_root = steam_root.resolve(strict=True)
    audit = make_audit(steam_root)
    AUDIT_PATH.write_bytes(canonical_json(audit))
    return {
        "status": "PASS",
        "audit_path": str(AUDIT_PATH.relative_to(REPO)).replace("\\", "/"),
        "summary": audit["summary"],
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="generate the workstream-only exact preimage audit")
    audit.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    audit.add_argument("--write", action="store_true", help="write only this workstream's audit artifact")
    build = sub.add_parser("build", help="build a fully pinned candidate without writing Steam")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            if not args.write:
                raise Wave8Error("audit generation requires --write and writes only the Wave 8 audit artifact")
            result = write_audit(args.steam_root)
        else:
            result = build_candidate(args.steam_root, args.output_root, args.manifest)
            result = {"status": "PASS", **result}
    except (OSError, ValueError, Wave8Error, WAVE4.QualityError, WAVE5.Wave5Error) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
