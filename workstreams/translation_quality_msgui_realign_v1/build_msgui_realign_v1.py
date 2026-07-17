#!/usr/bin/env python3
"""Freeze/build all reviewed Korean corrections for the live PC ``msgui``.

This builder is for two kinds of defects discovered in the full audit:
unfinished Japanese UI text and Korean sentences placed at the wrong message
coordinate.  Every replacement is checked against the matching pristine PC
Japanese coordinate and PC-derived format profile.  Switch Korean text is not
an input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_ORIGINAL = DEFAULT_STEAM_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals" / "MSG_PK" / "JP" / "msgui.bin"
RESOURCE = "MSG_PK/JP/msgui.bin"
PRIVATE = REPO / "tmp" / "translation_quality_audit_v1"
SMALL_UI_RESIDUALS = REPO / "tmp" / "translation_quality_pc_small_ui_residuals_v1" / "private_candidates.v1.jsonl"
PROPOSAL_PATHS = (
    # The original ``msgui_ko.jsonl`` is retained as audit evidence.  This
    # full PC-only rebase has the identical 70-coordinate set and replaces
    # only ID 191, so never load both paths in the same builder invocation.
    PRIVATE / "proposals" / "msgui_ko_pc_only_rebase.v1.jsonl",
    PRIVATE / "semantic" / "msgui_realign_3625_3670.v1.jsonl",
    PRIVATE / "semantic" / "msgui_findings.v1.jsonl",
    PRIVATE / "semantic" / "msgui_short_label_addendum.v1.jsonl",
    PRIVATE / "semantic" / "msgui_game_clear_coordinate_drift_addendum.v1.jsonl",
    PRIVATE / "semantic" / "msgui_pc_only_quality_addendum.v1.jsonl",
    SMALL_UI_RESIDUALS,
)
PUBLIC_OVERLAY = WORKSTREAM / "public" / "msgui_realign.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
DEFAULT_OUTPUT = REPO / "tmp" / "translation_quality_msgui_realign_v1" / "candidate"

OVERLAY_SCHEMA = "nobu16.kr.msgui-realign-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.msgui-realign-validation.v1"
MANIFEST_SCHEMA = "nobu16.kr.msgui-realign-build-manifest.v1"
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
MALFORMED_RUNTIME_RE = re.compile(r"\[\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


class MsguiRealignError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pretty_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def require_private(path: Path) -> Path:
    value = path.resolve()
    root = (REPO / "tmp").resolve()
    if value == root or root not in value.parents:
        raise MsguiRealignError(f"candidate output must remain below {root}")
    return value


def common_data(path: Path) -> tuple[bytes, bytes, MessageTable]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise MsguiRealignError(f"unchanged rebuild differs: {path}")
    return packed, raw, table


def profile(text: str) -> dict[str, Any]:
    esc_ranges = {index for match in ESC_RE.finditer(text) for index in range(match.start(), match.end())}
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "escape": ESC_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "controls": [f"U+{ord(char):04X}" for index, char in enumerate(text) if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and index not in esc_ranges],
        "fullwidth_percent_count": text.count("％"),
        "marker_334d_count": text.count("㌍"),
        "box_drawing": [char for char in text if 0x2500 <= ord(char) <= 0x257F],
    }


def baseline(packed: bytes, raw: bytes, table: MessageTable) -> dict[str, Any]:
    return {"packed_size": len(packed), "packed_sha256": sha256_bytes(packed), "raw_size": len(raw), "raw_sha256": sha256_bytes(raw), "string_count": table.string_count}


def replacement_value(row: Mapping[str, Any], label: str) -> str:
    # Semantic-review rows retain the live Korean in ``ko`` and put the
    # replacement in ``proposed_ko``.  Ordinary UI residual rows put their
    # replacement directly in ``ko``.  Do not confuse the useful before/after
    # pair with a conflicting proposal.
    value = row.get("proposed_ko") if "proposed_ko" in row else row.get("ko")
    if not isinstance(value, str) or not value:
        raise MsguiRealignError(f"proposal has no Korean replacement: {label}")
    return value


def optional_hash(row: Mapping[str, Any], keys: Iterable[str], expected: str, label: str) -> None:
    values = [row[key] for key in keys if key in row]
    if not values:
        return
    if not all(isinstance(value, str) and HEX64_RE.fullmatch(value.upper()) and value.upper() == expected for value in values):
        raise MsguiRealignError(f"proposal hash differs: {label}")


def read_proposals() -> dict[int, tuple[str, Mapping[str, Any], str]]:
    merged: dict[int, tuple[str, Mapping[str, Any], str]] = {}
    for path in PROPOSAL_PATHS:
        if not path.is_file():
            raise MsguiRealignError(f"reviewed proposal is absent: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MsguiRealignError(f"invalid JSONL: {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise MsguiRealignError(f"proposal is not an object: {path}:{line_number}")
            declared_resource = row.get("resource")
            if declared_resource is not None and declared_resource != "msgui":
                raise MsguiRealignError(f"proposal resource differs: {path}:{line_number}")
            entry_id = row.get("id")
            if isinstance(entry_id, bool) or not isinstance(entry_id, int) or entry_id < 0:
                raise MsguiRealignError(f"invalid id: {path}:{line_number}")
            label = f"{path}:{line_number}"
            value = replacement_value(row, label)
            prior = merged.setdefault(entry_id, (value, row, label))
            if prior[0] != value:
                raise MsguiRealignError(f"conflicting Korean proposal at msgui:{entry_id}")
    if not merged:
        raise MsguiRealignError("no msgui corrections loaded")
    return dict(sorted(merged.items()))


def source_metadata(original_path: Path, packed: bytes, raw: bytes, table: MessageTable) -> dict[str, Any]:
    return {"path_class": "local_PC_pristine", "packed_size": len(packed), "packed_sha256": sha256_bytes(packed), "raw_size": len(raw), "raw_sha256": sha256_bytes(raw), "string_count": table.string_count}


def assert_source_free(blob: bytes, label: str) -> None:
    text = blob.decode("utf-8")
    if KANA_OR_HAN_RE.search(text):
        raise MsguiRealignError(f"{label} unexpectedly contains Japanese/CJK source text")


def freeze(steam_root: Path, original_path: Path) -> dict[str, Any]:
    live_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    if not live_path.is_file() or not original_path.is_file():
        raise MsguiRealignError("live msgui or pristine original is absent")
    live_packed, live_raw, live = common_data(live_path)
    original_packed, original_raw, original = common_data(original_path)
    if live.string_count != original.string_count:
        raise MsguiRealignError("live/pristine msgui string count differs")
    proposals = read_proposals()
    entries: list[dict[str, Any]] = []
    for entry_id, (ko, proposal, label) in proposals.items():
        if entry_id >= live.string_count:
            raise MsguiRealignError(f"proposal is outside msgui: {entry_id}")
        current = live.texts[entry_id]
        pristine = original.texts[entry_id]
        if "proposed_ko" in proposal:
            if "ko" in proposal:
                private_current = proposal.get("ko")
                if not isinstance(private_current, str) or private_current != current:
                    raise MsguiRealignError(f"private semantic current differs: {label}")
            elif not any(key in proposal for key in ("source_current_utf16le_sha256", "source_current_hash", "current_hash", "current_ko_utf16le_sha256")):
                raise MsguiRealignError(f"private semantic proposal lacks a current-text gate: {label}")
        optional_hash(proposal, ("source_current_utf16le_sha256", "source_current_hash", "current_hash", "current_ko_utf16le_sha256"), text_hash(current), label)
        optional_hash(proposal, ("proposed_ko_utf16le_sha256", "proposed_text_utf16le_sha256"), text_hash(ko), label)
        optional_hash(proposal, ("pristine_jp_utf16le_sha256", "pristine_jp_hash", "source_text_hash"), text_hash(pristine), label)
        if "\0" in ko or "\ufffd" in ko or KANA_OR_HAN_RE.search(ko) or MALFORMED_RUNTIME_RE.search(ko):
            raise MsguiRealignError(f"unsafe Korean replacement at msgui:{entry_id}")
        if ko.count("?") >= 3 and not HANGUL_RE.search(ko):
            raise MsguiRealignError(f"suspicious question-mark-only replacement at msgui:{entry_id}")
        pristine_profile = profile(pristine)
        if pristine_profile != profile(ko):
            raise MsguiRealignError(f"replacement format differs from pristine PC JP at msgui:{entry_id}")
        entries.append({
            "id": entry_id,
            "source_current_utf16le_sha256": text_hash(current),
            "pristine_jp_utf16le_sha256": text_hash(pristine),
            "ko": ko,
            "ko_utf16le_sha256": text_hash(ko),
            "pristine_format_profile_sha256": canonical_hash(pristine_profile),
        })
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgui_realign.v1",
        "resource": RESOURCE,
        "scope": "reviewed PC msgui residual and coordinate-realignment fixes; Switch Korean excluded",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False},
        "live_baseline": baseline(live_packed, live_raw, live),
        "pristine_pc_jp": source_metadata(original_path, original_packed, original_raw, original),
        "entry_count": len(entries),
        "entries": entries,
    }
    blob = pretty_json(overlay)
    assert_source_free(blob, "overlay")
    atomic_write(PUBLIC_OVERLAY, blob)
    validation = validate_overlay(steam_root, original_path, overlay)
    validation_blob = pretty_json(validation)
    assert_source_free(validation_blob, "validation")
    atomic_write(VALIDATION, validation_blob)
    return {"entry_count": len(entries), "overlay_sha256": sha256_bytes(blob), "validation_sha256": sha256_bytes(validation_blob), "steam_installation_written": False}


def read_overlay() -> dict[str, Any]:
    try:
        value = json.loads(PUBLIC_OVERLAY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsguiRealignError("public overlay is invalid") from exc
    if not isinstance(value, dict):
        raise MsguiRealignError("public overlay root is invalid")
    return value


def validate_overlay(steam_root: Path, original_path: Path, overlay: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = overlay if overlay is not None else read_overlay()
    required = {"schema", "overlay_id", "resource", "scope", "distribution_policy", "live_baseline", "pristine_pc_jp", "entry_count", "entries"}
    policy = {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "switch_korean_translation_used": False}
    if set(value) != required or value["schema"] != OVERLAY_SCHEMA or value["overlay_id"] != "msgui_realign.v1" or value["resource"] != RESOURCE or value["distribution_policy"] != policy:
        raise MsguiRealignError("public overlay header differs")
    live_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    live_packed, live_raw, live = common_data(live_path)
    original_packed, original_raw, original = common_data(original_path)
    if value["live_baseline"] != baseline(live_packed, live_raw, live) or value["pristine_pc_jp"] != source_metadata(original_path, original_packed, original_raw, original):
        raise MsguiRealignError("live/pristine baseline differs")
    entries = value["entries"]
    if not isinstance(entries, list) or value["entry_count"] != len(entries) or not entries:
        raise MsguiRealignError("entry count differs")
    previous = -1
    effective = 0
    for entry in entries:
        fields = {"id", "source_current_utf16le_sha256", "pristine_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "pristine_format_profile_sha256"}
        if not isinstance(entry, dict) or set(entry) != fields:
            raise MsguiRealignError("entry schema differs")
        entry_id = entry["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or not (previous < entry_id < live.string_count):
            raise MsguiRealignError("entry ids are invalid or unsorted")
        previous = entry_id
        ko = entry["ko"]
        if not isinstance(ko, str) or any(not isinstance(entry[key], str) or not HEX64_RE.fullmatch(entry[key]) for key in fields - {"id", "ko"}):
            raise MsguiRealignError(f"entry value type is invalid: {entry_id}")
        current = live.texts[entry_id]
        pristine = original.texts[entry_id]
        if text_hash(current) != entry["source_current_utf16le_sha256"] or text_hash(pristine) != entry["pristine_jp_utf16le_sha256"] or text_hash(ko) != entry["ko_utf16le_sha256"] or canonical_hash(profile(pristine)) != entry["pristine_format_profile_sha256"]:
            raise MsguiRealignError(f"entry hash/profile differs: {entry_id}")
        if profile(pristine) != profile(ko) or KANA_OR_HAN_RE.search(ko) or MALFORMED_RUNTIME_RE.search(ko):
            raise MsguiRealignError(f"entry Korean/format safety differs: {entry_id}")
        if ko.count("?") >= 3 and not HANGUL_RE.search(ko):
            raise MsguiRealignError(f"entry has a suspicious question-mark-only replacement: {entry_id}")
        effective += current != ko
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "resource": RESOURCE,
        "entry_count": len(entries),
        "effective_change_count": effective,
        "checks": {"live_baseline": "OK", "pristine_pc_jp_baseline": "OK", "per_entry_current_and_pristine_hashes": "OK", "pristine_format_profiles": "OK", "parser_roundtrip": "pending_build", "steam_installation_written": False},
    }


def build(steam_root: Path, original_path: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private(output_root)
    overlay = read_overlay()
    validation = validate_overlay(steam_root, original_path, overlay)
    live_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    packed, raw, table = common_data(live_path)
    texts = list(table.texts)
    replacements = {entry["id"]: entry["ko"] for entry in overlay["entries"]}
    for entry_id, ko in replacements.items():
        texts[entry_id] = ko
    candidate_raw_a = rebuild_message_table(table, texts)
    candidate_raw_b = rebuild_message_table(table, texts)
    if candidate_raw_a != candidate_raw_b:
        raise MsguiRealignError("raw candidate is not deterministic")
    candidate_a = recompress_wrapper(candidate_raw_a, packed)
    candidate_b = recompress_wrapper(candidate_raw_a, packed)
    if candidate_a != candidate_b:
        raise MsguiRealignError("packed candidate is not deterministic")
    _header, checked_raw = decompress_wrapper(candidate_a)
    checked = parse_message_table(checked_raw)
    if checked_raw != candidate_raw_a or checked.texts != tuple(texts) or rebuild_message_table(checked, checked.texts) != checked_raw:
        raise MsguiRealignError("candidate parser roundtrip differs")
    for entry_id, before in enumerate(table.texts):
        if checked.texts[entry_id] != replacements.get(entry_id, before):
            raise MsguiRealignError(f"candidate value differs: {entry_id}")
    target = (output_root / Path(RESOURCE)).resolve()
    if output_root not in target.parents:
        raise MsguiRealignError("candidate path escapes private output")
    atomic_write(target, candidate_a)
    if live_path.read_bytes() != packed or target.read_bytes() != candidate_a:
        raise MsguiRealignError("unexpected Steam/candidate mutation")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "switch_korean_translation_used": False,
        "resource": RESOURCE,
        "entry_count": validation["entry_count"],
        "effective_change_count": validation["effective_change_count"],
        "target": {"packed_size": len(candidate_a), "packed_sha256": sha256_bytes(candidate_a), "raw_size": len(candidate_raw_a), "raw_sha256": sha256_bytes(candidate_raw_a), "string_count": checked.string_count},
        "output_policy": {"private_root": "tmp", "steam_installation_written": False, "release_asset_written": False, "github_written": False},
        "checks": {"source_hash_gates": "OK", "pristine_format_profiles": "OK", "deterministic_rebuild": "OK", "parser_roundtrip": "OK", "nonselected_texts": "OK"},
    }
    blob = pretty_json(manifest)
    assert_source_free(blob, "manifest")
    atomic_write(output_root / "build_manifest.v1.json", blob)
    return {"entry_count": validation["entry_count"], "candidate_path": str(target), "steam_installation_written": False}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    freeze_parser.add_argument("--original", type=Path, default=DEFAULT_ORIGINAL)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--original", type=Path, default=DEFAULT_ORIGINAL)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        result = freeze(args.steam_root, args.original) if args.command == "freeze" else build(args.steam_root, args.original, args.output_root)
    except (MsguiRealignError, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
