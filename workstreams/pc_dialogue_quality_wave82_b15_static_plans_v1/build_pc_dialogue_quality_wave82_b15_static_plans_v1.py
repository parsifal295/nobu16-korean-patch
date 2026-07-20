#!/usr/bin/env python3
"""Build the private Wave 82 PK static B15-plan dialogue candidate.

Only two pinned static records are rebuilt.  The builder writes a candidate
below its own ``tmp`` directory and deliberately has no Steam-apply, Git,
network, or release operation.
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

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave82-b15-static-plans.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave82-b15-static-plans-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave82-b15-static-plans-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_SIZE = 1_806_590
INPUT_SHA256 = "A8983770FF9026F018042D94F44AF7D0E67B6A7E01F42891B74386B32078791D"
INPUT_RAW_SIZE = 1_799_508
INPUT_RAW_SHA256 = "A395885A2FC8CCDD1CF26F92D0B9F1C8B4D62EBE8ACE8D3B17B1DCE501C90CE8"
TARGET_SIZE = 1_806_570
TARGET_SHA256 = "3F6F85E503F0FF5FA4E3C53E2B51DE12622E2E9AAE74F0C18A18A4832848C2C7"
TARGET_RAW_SIZE = 1_799_488
TARGET_RAW_SHA256 = "23E709A424D654A43498D748B3CB7BB2E49439A72AEE5B8133423C56CB5732B5"

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
        STEAM_ROOT / "MSG_PK/EN/msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        STEAM_ROOT / "MSG_PK/SC/msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        STEAM_ROOT / "MSG_PK/TC/msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave82Error(RuntimeError):
    """A pinned input, source anchor, or structural invariant drifted."""


@dataclass(frozen=True)
class Change:
    name: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    current_record_size: int
    target_record_sha256: str
    target_record_size: int
    target_line_widths_px: tuple[int, ...]
    source_record_sha256: Mapping[str, str]
    input_opaque_spans_hex: tuple[str, ...]
    static_0143_commands: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Korean targets are authored here after same-coordinate PC JP/EN/SC/TC review.
# They retain all three literal slots and two manual LFs of each source record.
CHANGES = (
    Change(
        name="b15_arson_plan",
        coordinate=(15, 259),
        target_literals=(
            "방화 계책이라면 잠시 시간을 주십시오.",
            "\n성 병사를 회유해 요충지를 장악한다면",
            "\n이쪽이 더 승산이 있습니다.",
        ),
        current_record_sha256="83917A745013D5911E569006C353077D3EC8E4F78868C0F9B0375D32EF00B81E",
        current_record_size=135,
        target_record_sha256="9C1C41D844F56A22FE5B5B8E1B80B561FC93A4124779983D2728DAFED0B64FC6",
        target_record_size=137,
        target_line_widths_px=(888, 864, 624),
        source_record_sha256={
            "PK_JP": "AC9B87C5B4C15B96F910D56C27929EB50DA20148F0DA1FA01C4285A2398FAD14",
            "EN": "09109F93B20DCEE06458972D22FFDF1E765518C5025D2112458AE5B046F2665C",
            "SC": "6A7FD29117D384E5C6080776E944A9A8FB24F7EA9948E602ED2B4FC6F45239A0",
            "TC": "EA89CE7077F76F06448627B79AB30087B76E0B67C5DA2982DE8ACCC0D63F1007",
        },
        input_opaque_spans_hex=("", "01439C040000", "01432A040000", "01431E010000050505"),
        static_0143_commands=("01439C040000", "01432A040000", "01431E010000"),
        rationale="방화 계책의 대기·성 병사 회유·요충지 장악·더 높은 승산이라는 원문 의미를 모두 완결한다.",
    ),
    Change(
        name="b15_recruitment_plan",
        coordinate=(15, 261),
        target_literals=(
            "인재를 빼내는 방안은 다소 위험하지만",
            "\n연고자를 내세워 권유한다면",
            "\n잘되면 모두 함께 돌아설지도 모릅니다.",
        ),
        current_record_sha256="6B4E6992284963C293BA28E6092992530FE648A0B483AF78F2450FA7AF828BB1",
        current_record_size=157,
        target_record_sha256="4A08BB98395E05731D55893A70E5E0AD2C0E92EA513EBCFA395DC599501F71C2",
        target_record_size=135,
        target_line_widths_px=(864, 624, 888),
        source_record_sha256={
            "PK_JP": "ADDC8AC786A1818C335373D8F9AB8176934E4796987D41454CBF5762C2F897F4",
            "EN": "B52F6B810A4C034C1EFA972DF36AAF6BE4162C21D003257CE827E55AC8FAC56C",
            "SC": "2F825D8E850B1ED9DA0DDCDD18856A9F4D75EFF76C90172A997A890170A5A2F3",
            "TC": "8215E270FE944D8AAD4AFE5341C014D5A2FEB37B822E1FD26E5A66CD0C589FC8",
        },
        input_opaque_spans_hex=("", "014326020000", "0143BC020000014324010000", "01435A040000050505"),
        static_0143_commands=("014326020000", "0143BC020000", "014324010000", "01435A040000"),
        rationale="인재 포섭의 위험, 연고자를 통한 권유, 함께 돌아설 가능성의 조건 구조를 보존한다.",
    ),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave82Error(label)


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
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave82Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave82Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 helper differs")
    spec = importlib.util.spec_from_file_location("wave82_imported_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave82Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    for language, expected_record_hash in change.source_record_sha256.items():
        record = sources[language].get(change.coordinate)
        require(record is not None and W27.literal_texts(record), f"{language} source record is absent: {change.coordinate}")
        actual_record_hash = W27.sha256_bytes(record.data)
        require(actual_record_hash == expected_record_hash, f"{language} source record differs: {change.coordinate}")
        contexts[language] = {
            "record_sha256": actual_record_hash,
            "literal_count": len(W27.literal_texts(record)),
            "visible_text_utf16le_sha256": sha256_bytes("".join(W27.literal_texts(record)).encode("utf-16le")),
        }
    return {"coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}", "pc_contexts": contexts}


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"current record differs: {change.coordinate}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.coordinate}")
    require(W27.literal_texts(before) != change.target_literals, f"change is already applied: {change.coordinate}")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"literal boundary differs: {change.coordinate}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"record terminator differs: {change.coordinate}")
    before_spans = tuple(span.hex().upper() for span in W27.opaque_spans(before))
    require(before_spans == change.input_opaque_spans_hex, f"input opaque bytes differ: {change.coordinate}")
    commands = W27.complete_0143_commands(W27.opaque_spans(before))
    require(commands == change.static_0143_commands, f"0143 command set differs: {change.coordinate}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.coordinate}")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), f"manual line count differs: {change.coordinate}")
    layout = W27.line_layout(change.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"line widths differ: {change.coordinate}")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, f"target exceeds dialogue layout: {change.coordinate}")
    require(not layout["wide_fallback_codepoints"], f"target uses a fallback glyph: {change.coordinate}")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record differs: {change.coordinate}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.coordinate}")
    require(W27.literal_texts(after) == change.target_literals, f"target literals differ: {change.coordinate}")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"opaque bytecode differs: {change.coordinate}")
    require(tuple(span.hex().upper() for span in W27.opaque_spans(after)) == ("", "", "", "050505"), f"target opaque layout differs: {change.coordinate}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"static inflection command remains: {change.coordinate}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"literal markers differ: {change.coordinate}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.coordinate}")
    return rebuilt, {
        "name": change.name,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "target_line_widths_px": list(change.target_line_widths_px),
        "manual_line_count": target_text.count("\n"),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": ["", "", "", "050505"],
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "rationale": change.rationale,
    }


def prepare_candidate() -> CandidateBundle:
    input_path = reject_switch(RESOURCE_PATH, "current Steam PK dialogue")
    packed = input_path.read_bytes()
    require(len(packed) == INPUT_SIZE and sha256_bytes(packed) == INPUT_SHA256, "current Steam PK dialogue profile differs")
    W27.validate_raw_roundtrip(packed, "current Steam PK dialogue")
    _input_header, input_raw = W27.decompress_wrapper(packed)
    require(len(input_raw) == INPUT_RAW_SIZE and sha256_bytes(input_raw) == INPUT_RAW_SHA256, "current Steam PK dialogue raw profile differs")
    current = W27.records_by_coordinate(packed)
    sources, source_hashes = source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current.get(change.coordinate)
        require(before is not None, f"current PK coordinate is absent: {change.coordinate}")
        replacement, row = validate_change(change, before, advance)
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        replacements[change.coordinate] = replacement
        rows.append(row)
    candidate = W27.rebuild_packed_msggame(packed, replacements)
    require(len(candidate) == TARGET_SIZE and sha256_bytes(candidate) == TARGET_SHA256, "target PK dialogue profile differs")
    W27.validate_raw_roundtrip(candidate, "Wave 82 private PK dialogue candidate")
    _header, raw = W27.decompress_wrapper(candidate)
    require(len(raw) == TARGET_RAW_SIZE and sha256_bytes(raw) == TARGET_RAW_SHA256, "target PK dialogue raw profile differs")
    after = W27.records_by_coordinate(candidate)
    require(set(current) == set(after), "record coordinate set differs")
    changed = {coordinate for coordinate in current if current[coordinate].data != after[coordinate].data}
    target_coordinates = {change.coordinate for change in CHANGES}
    require(changed == target_coordinates, "changed PK record scope differs")
    unchanged_record_count = 0
    for coordinate, before in current.items():
        if coordinate in target_coordinates:
            continue
        require(before.data == after[coordinate].data, f"non-target record changed: {coordinate}")
        unchanged_record_count += 1
    for change in CHANGES:
        require(W27.sha256_bytes(after[change.coordinate].data) == change.target_record_sha256, f"output record differs: {change.coordinate}")
        require(W27.literal_texts(after[change.coordinate]) == change.target_literals, f"output literals differ: {change.coordinate}")
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
        "input": {"resource": RESOURCE, "size": INPUT_SIZE, "sha256": INPUT_SHA256, "raw_size": INPUT_RAW_SIZE, "raw_sha256": INPUT_RAW_SHA256},
        "target": {"resource": RESOURCE, "size": TARGET_SIZE, "sha256": TARGET_SHA256, "raw_size": TARGET_RAW_SIZE, "raw_sha256": TARGET_RAW_SHA256},
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "non_target_record_count": unchanged_record_count,
        "non_target_record_byte_identity": "PASS",
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            RESOURCE: {
                "input": {"size": INPUT_SIZE, "sha256": INPUT_SHA256},
                "output": {"size": TARGET_SIZE, "sha256": TARGET_SHA256},
                "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
            }
        },
        "changed_record_count": len(CHANGES),
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
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        print(json.dumps({"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(verify_private(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
