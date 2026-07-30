#!/usr/bin/env python3
"""Build a private PC-only clarity-improvement candidate for one PK dialogue.

The candidate makes one current Steam dialogue command more explicit while
preserving its source meaning.  It is deliberately private-only: it writes a reproducible candidate
under ``tmp/`` and has no Steam, Git, network, or release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATH = STEAM_ROOT / RESOURCE
W32_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave32_static_remainder_v1"
    / "build_pc_dialogue_quality_wave32_static_remainder_v1.py"
)
W32_HELPER_SHA256 = "442ECDF8ABB5998B020AC2BA55420E9397FACF31D942A33D8285165685F9C92F"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave35-static-command.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave35-static-command-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave35-static-command-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_SIZE = 1_806_542
INPUT_SHA256 = "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"
TARGET_SIZE = 1_806_550
TARGET_SHA256 = "F6F75C68A8E80E752351D4C943F9DB5E3A88C4208C90EC0074178BFC1094EB72"
TARGET_RAW_SIZE = 1_799_468
TARGET_RAW_SHA256 = "1B87C9D063265CF856EA86053AE950140F03C0142F35E7462B4E93B3E6D10DE5"

PC_SOURCES = {
    "PK_JP": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave35Error(RuntimeError):
    """Raised when a pinned input, source anchor, or candidate contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    target_record_sha256: str
    target_record_size: int
    target_line_widths_px: tuple[int, ...]
    source_record_sha256: Mapping[str, str]
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Korean target text is authored in this project.  PC JP/EN/SC/TC source text
# is checked by hash but never embedded or emitted here.
CHANGE = Change(
    name="third_wave_command_and_resolution",
    coordinate=(17, 938),
    target_literals=("제3진, 전진하라!\n이제 곧 결판이 나겠군.",),
    current_record_sha256="D525C71770F01BFFBA95A4AE6D45513A44EE4A16DC37E0D05D9D22E5E400E114",
    target_record_sha256="8A66F0FBE7465632D9D1E28B5EB1D1A662E7D8AC029D28CD3EB46A42CADB3BA9",
    target_record_size=57,
    target_line_widths_px=(384, 528),
    source_record_sha256={
        "PK_JP": "D229B7DE6AFEE8AE13D6EE888747E58B9FBC55BD2C08408C1AA9DFAA43207B12",
        "EN": "06C5E6313F287CA65F8D438549AF35014F5BD374CC71304591CA1D396988BE1D",
        "SC": "7993F4123C6E92565E60C7D57EBDDD9F9F71128B1F58A5A95D8F3ECD8CBB0F65",
        "TC": "04125630B21932C3633757FDD6345A83810A8611CB064849DB013C697008F41C",
    },
    rationale="원문의 전진 명령을 완전한 명령문으로 복원하고, 임박한 결판의 의미를 유지한다.",
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave35Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any(part.casefold() == "switch" or "switch" in part.casefold() for part in resolved.parts):
        raise Wave35Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave35Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w32() -> Any:
    require(W32_HELPER.is_file(), "Wave 32 helper is absent")
    require(sha256_path(W32_HELPER) == W32_HELPER_SHA256, "pinned Wave 32 helper differs")
    spec = importlib.util.spec_from_file_location("wave35_imported_wave32", W32_HELPER)
    if spec is None or spec.loader is None:
        raise Wave35Error("cannot load pinned Wave 32 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W32 = load_w32()
W27 = W32.W27


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def validate_source_anchor(sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    for language, expected_record_hash in CHANGE.source_record_sha256.items():
        record = sources[language].get(CHANGE.coordinate)
        require(record is not None and W27.literal_texts(record), f"{language} source record is absent")
        actual_record_hash = W27.sha256_bytes(record.data)
        require(actual_record_hash == expected_record_hash, f"{language} source record differs")
        contexts[language] = {
            "record_sha256": actual_record_hash,
            "first_literal_utf16le_sha256": sha256_bytes(W27.literal_texts(record)[0].encode("utf-16le")),
        }
    return {
        "coordinate": f"{CHANGE.coordinate[0]}:{CHANGE.coordinate[1]}",
        "pc_contexts": contexts,
    }


def validate_change(before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == CHANGE.current_record_sha256, "current record differs")
    require(W27.literal_texts(before) != CHANGE.target_literals, "change is already applied")
    require(len(W27.literal_texts(before)) == len(CHANGE.target_literals), "literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), "record terminator differs")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(CHANGE.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), "manual line count differs")
    layout = W27.line_layout(CHANGE.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == CHANGE.target_line_widths_px, "line widths differ")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, "target exceeds dialogue layout")
    require(not layout["wide_fallback_codepoints"], "target uses a fallback glyph")
    rebuilt = W27.rebuild_static_record(before, CHANGE.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == CHANGE.target_record_sha256, "target record differs")
    require(len(after.data) == CHANGE.target_record_size, "target record size differs")
    require(W27.literal_texts(after) == CHANGE.target_literals, "target literals differ")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), "opaque bytecode differs")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), "static inflection command remains")
    require(W27.marker_topology(after) == W27.marker_topology(before), "literal markers differ")
    require(after.data.endswith(W27.RECORD_TERMINATOR), "target terminator differs")
    return rebuilt, {
        "name": CHANGE.name,
        "coordinate": f"{CHANGE.coordinate[0]}:{CHANGE.coordinate[1]}",
        "current_record_sha256": CHANGE.current_record_sha256,
        "target_record_sha256": CHANGE.target_record_sha256,
        "target_record_size": CHANGE.target_record_size,
        "target_line_widths_px": list(CHANGE.target_line_widths_px),
        "rationale": CHANGE.rationale,
        "removed_static_0143_command_count": len(W27.complete_0143_commands(W27.opaque_spans(before))),
    }


def prepare_candidate() -> CandidateBundle:
    input_path = reject_switch(RESOURCE_PATH, "current Steam PK dialogue")
    packed = input_path.read_bytes()
    require(len(packed) == INPUT_SIZE and sha256_bytes(packed) == INPUT_SHA256, "current Steam PK dialogue profile differs")
    W27.validate_raw_roundtrip(packed, "current Steam PK dialogue")
    current = W27.records_by_coordinate(packed)
    before = current.get(CHANGE.coordinate)
    require(before is not None, "current PK coordinate is absent")
    sources, source_hashes = load_source_records()
    source_anchor = validate_source_anchor(sources)
    advance, font = W27.load_font_advance()
    replacement, row = validate_change(before, advance)
    candidate = W27.rebuild_packed_msggame(packed, {CHANGE.coordinate: replacement})
    require(len(candidate) == TARGET_SIZE and sha256_bytes(candidate) == TARGET_SHA256, "target PK dialogue profile differs")
    W27.validate_raw_roundtrip(candidate, "Wave 35 private PK dialogue candidate")
    _header, raw = W27.decompress_wrapper(candidate)
    require(len(raw) == TARGET_RAW_SIZE and sha256_bytes(raw) == TARGET_RAW_SHA256, "target PK dialogue raw profile differs")
    after = W27.records_by_coordinate(candidate)
    changed = {coordinate for coordinate in current if current[coordinate].data != after[coordinate].data}
    require(set(current) == set(after) and changed == {CHANGE.coordinate}, "changed PK record scope differs")
    require(W27.sha256_bytes(after[CHANGE.coordinate].data) == CHANGE.target_record_sha256, "output record differs")
    require(W27.literal_texts(after[CHANGE.coordinate]) == CHANGE.target_literals, "output literals differ")
    row["pc_source_anchor"] = source_anchor
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "input": {"resource": RESOURCE, "size": INPUT_SIZE, "sha256": INPUT_SHA256},
        "target": {"resource": RESOURCE, "size": TARGET_SIZE, "sha256": TARGET_SHA256, "raw_size": TARGET_RAW_SIZE, "raw_sha256": TARGET_RAW_SHA256},
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "record": row,
        "changed_record_count": 1,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {RESOURCE: {"input": {"size": INPUT_SIZE, "sha256": INPUT_SHA256}, "output": {"size": TARGET_SIZE, "sha256": TARGET_SHA256}, "changed_coordinates": [f"{CHANGE.coordinate[0]}:{CHANGE.coordinate[1]}"]}},
        "changed_record_count": 1,
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    require_private(TMP_ROOT, "tmp root")
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource = stage / RESOURCE
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_bytes(bundle.packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    resource = output / RESOURCE
    require(resource.is_file() and resource.read_bytes() == bundle.packed, "private candidate PK dialogue differs")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": 1, "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        print(json.dumps({"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": 1, "steam_game_resource_written": False}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(verify_private(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
