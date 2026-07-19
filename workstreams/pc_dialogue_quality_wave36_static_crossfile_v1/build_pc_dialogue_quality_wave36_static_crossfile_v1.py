#!/usr/bin/env python3
"""Build a private PC-only static dialogue correction candidate for Wave 36.

This candidate contains three independently anchored static records: one Base
spacing repair and two byte-identical PK dialogue records.  It is private-only
and cannot write Steam resources, operate Git, contact a network, or release.
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
BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / BASE_RESOURCE,
    PK_RESOURCE: STEAM_ROOT / PK_RESOURCE,
}
W32_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave32_static_remainder_v1"
    / "build_pc_dialogue_quality_wave32_static_remainder_v1.py"
)
W32_HELPER_SHA256 = "442ECDF8ABB5998B020AC2BA55420E9397FACF31D942A33D8285165685F9C92F"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave36-static-crossfile.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave36-static-crossfile-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave36-static-crossfile-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_422, "sha256": "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"},
    PK_RESOURCE: {"size": 1_806_542, "sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"},
}
TARGET_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_422, "sha256": "D7741CBA053FCBA5D4D11D4923839FE6B863E7C4632C394F2E7E0BA979EE5668", "raw_size": 1_498_520, "raw_sha256": "35FF63B300508A57E62381A2A0990B44CA5F7B5F2588EB55490FC694D95FC846"},
    PK_RESOURCE: {"size": 1_806_522, "sha256": "51BFCC53298725543DA71E1CE777F8231FAADDF8D0526A11B109AF68040DB609", "raw_size": 1_799_440, "raw_sha256": "A8D72118A7A0F970FE935AF283660BA830CE6431B54B98A7D7C3C6DAF016EB37"},
}

# Only PC resources are admissible.  Base EN is not shipped in this installation;
# the exact Base SC/TC records are present but empty and are checked as such.
PC_SOURCES = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "BASE_SC": (
        STEAM_ROOT / "MSG" / "SC" / "msggame.bin",
        "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    ),
    "BASE_TC": (
        STEAM_ROOT / "MSG" / "TC" / "msggame.bin",
        "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    ),
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
    "PK_EN": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "PK_SC": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "PK_TC": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave36Error(RuntimeError):
    """Raised when a pinned input, source anchor, or candidate contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    resource: str
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
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Korean targets are project-authored.  Source text is checked by record hash
# only; no Switch Korean text or Switch-derived translation is read or emitted.
CHANGES = (
    Change(
        name="base_ambush_missing_space",
        resource=BASE_RESOURCE,
        coordinate=(9, 3795),
        target_literals=("복병이 있었다! 혼란한 틈에 쳐부수자!",),
        current_record_sha256="36853392B2DFB50EE5E2FF21183090583361FA2835511057F92947E7974C37EC",
        target_record_sha256="A1C33D6CFD7C3CEE040C02C9A7B507922DD53A5DFB41BD9BB629E93087223871",
        target_record_size=51,
        target_line_widths_px=(864,),
        source_record_sha256={
            "BASE_JP": "C0BC47D7D7B66CFE42B932A8622766D3ED75EAAB555BD48BB646B67902DDA360",
            "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850",
            "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850",
        },
        rationale="문장 사이 공백 하나만 복원한다. 동일 PC 일본어 원문의 다른 현재 한국어 레코드와도 일치한다.",
    ),
    Change(
        name="pk_found_out_714",
        resource=PK_RESOURCE,
        coordinate=(17, 714),
        target_literals=("들킨 건가…!\n하지만 여기까지 왔으니 물러설 수 없다!",),
        current_record_sha256="CD1B3CEBAC34F828E8B06151F2FD05616E31DEC0CCCA4EF37F694C82DCD95E8F",
        target_record_sha256="2EAA8FB4B77BF0EA78DDDBC800983930CD47B7847A328628DC92BE46CE71AA4E",
        target_record_size=69,
        target_line_widths_px=(288, 912),
        source_record_sha256={
            "PK_JP": "ADD7047114A526428F8980580F9CD4F61E253CE1DB0031D57A9D72142C93FFD5",
            "PK_EN": "5675E5B2E33ECEA5EB135957F7CC6ABE9DA2B2424F57696E81ACACED99B421F3",
            "PK_SC": "609E9FEA0815BC511814B70284037B03B91E7B6A0A9D72980562AAB255581C71",
            "PK_TC": "69D41695352005B1CEFCA7BE0B796F8BE82F44864A1B4481BE91688B30FCF7F8",
        },
        rationale="발각된 주체를 '눈치챘는가'로 뒤집은 오류를 바로잡고, 퇴각 불가 의미를 유지한다.",
    ),
    Change(
        name="pk_found_out_821",
        resource=PK_RESOURCE,
        coordinate=(17, 821),
        target_literals=("들킨 건가…!\n하지만 여기까지 왔으니 물러설 수 없다!",),
        current_record_sha256="CD1B3CEBAC34F828E8B06151F2FD05616E31DEC0CCCA4EF37F694C82DCD95E8F",
        target_record_sha256="2EAA8FB4B77BF0EA78DDDBC800983930CD47B7847A328628DC92BE46CE71AA4E",
        target_record_size=69,
        target_line_widths_px=(288, 912),
        source_record_sha256={
            "PK_JP": "ADD7047114A526428F8980580F9CD4F61E253CE1DB0031D57A9D72142C93FFD5",
            "PK_EN": "5675E5B2E33ECEA5EB135957F7CC6ABE9DA2B2424F57696E81ACACED99B421F3",
            "PK_SC": "609E9FEA0815BC511814B70284037B03B91E7B6A0A9D72980562AAB255581C71",
            "PK_TC": "69D41695352005B1CEFCA7BE0B796F8BE82F44864A1B4481BE91688B30FCF7F8",
        },
        rationale="714와 완전히 같은 원문·현문인 중복 레코드다. 같은 의미 오류를 함께 보정한다.",
    ),
)

if len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 36 must contain unique resource coordinates")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave36Error(label)


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
        raise Wave36Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave36Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w32() -> Any:
    require(W32_HELPER.is_file(), "Wave 32 helper is absent")
    require(sha256_path(W32_HELPER) == W32_HELPER_SHA256, "pinned Wave 32 helper differs")
    spec = importlib.util.spec_from_file_location("wave36_imported_wave32", W32_HELPER)
    if spec is None or spec.loader is None:
        raise Wave36Error("cannot load pinned Wave 32 helper")
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


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    for language, expected_record_hash in change.source_record_sha256.items():
        record = sources[language].get(change.coordinate)
        require(record is not None, f"{change.name} {language} source record is absent")
        actual_record_hash = W27.sha256_bytes(record.data)
        require(actual_record_hash == expected_record_hash, f"{change.name} {language} source record differs")
        literals = W27.literal_texts(record)
        contexts[language] = {
            "record_sha256": actual_record_hash,
            "first_literal_utf16le_sha256": sha256_bytes(literals[0].encode("utf-16le")) if literals and literals[0] else None,
            "literal_count": len(literals),
        }
    return {"coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}", "pc_contexts": contexts}


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"{change.name} current record differs")
    require(W27.literal_texts(before) != change.target_literals, f"{change.name} is already applied")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"{change.name} literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} record terminator differs")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), f"{change.name} manual line count differs")
    layout = W27.line_layout(change.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"{change.name} line widths differ")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, f"{change.name} exceeds dialogue layout")
    require(not layout["wide_fallback_codepoints"], f"{change.name} uses a fallback glyph")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"{change.name} target record differs")
    require(len(after.data) == change.target_record_size, f"{change.name} target record size differs")
    require(W27.literal_texts(after) == change.target_literals, f"{change.name} target literals differ")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"{change.name} opaque bytecode differs")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"{change.name} static inflection command remains")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.name} literal markers differ")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} target terminator differs")
    return rebuilt, {
        "name": change.name,
        "resource": change.resource,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "target_record_size": change.target_record_size,
        "target_line_widths_px": list(change.target_line_widths_px),
        "rationale": change.rationale,
        "removed_static_0143_command_count": len(W27.complete_0143_commands(W27.opaque_spans(before))),
    }


def prepare_candidate() -> CandidateBundle:
    current_packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = reject_switch(path, f"current Steam {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"current Steam profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"current Steam {resource}")
        current_packed[resource] = packed
        current_records[resource] = W27.records_by_coordinate(packed)
    sources, source_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_records[change.resource].get(change.coordinate)
        require(before is not None and change.coordinate not in replacements[change.resource], f"current coordinate differs: {change.name}")
        source_anchor = validate_source_anchor(change, sources)
        replacement, row = validate_change(change, before, advance)
        replacements[change.resource][change.coordinate] = replacement
        row["pc_source_anchor"] = source_anchor
        rows.append(row)
    # The Base target is an existing current Korean rendering of the same JP text.
    precedent = current_records[BASE_RESOURCE].get((17, 26))
    require(precedent is not None and W27.literal_texts(precedent) == CHANGES[0].target_literals, "Base Korean precedent differs")
    require(W27.sha256_bytes(precedent.data) == CHANGES[0].target_record_sha256, "Base Korean precedent record differs")
    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in current_packed.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"] and sha256_bytes(candidate) == profile["sha256"], f"target packed profile differs: {resource}")
        W27.validate_raw_roundtrip(candidate, f"Wave 36 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
        after = W27.records_by_coordinate(candidate)
        changed = {coordinate for coordinate in current_records[resource] if current_records[resource][coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(set(current_records[resource]) == set(after) and changed == expected, f"changed record scope differs: {resource}")
        for change in (entry for entry in CHANGES if entry.resource == resource):
            require(W27.sha256_bytes(after[change.coordinate].data) == change.target_record_sha256, f"output record differs: {change.name}")
            require(W27.literal_texts(after[change.coordinate]) == change.target_literals, f"output literals differ: {change.name}")
        packed_output[resource] = candidate
        raw_output[resource] = raw
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "pc_only_sources": True,
            "switch_korean_read": False,
            "base_en_source": "not_shipped",
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "input": {resource: {"size": INPUT_PROFILES[resource]["size"], "sha256": INPUT_PROFILES[resource]["sha256"]} for resource in RESOURCE_PATHS},
        "target": TARGET_PROFILES,
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "base_korean_precedent": {"resource": BASE_RESOURCE, "coordinate": "17:26", "record_sha256": CHANGES[0].target_record_sha256},
        "changed_record_count": len(CHANGES),
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "output": {"size": TARGET_PROFILES[resource]["size"], "sha256": TARGET_PROFILES[resource]["sha256"]},
                "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource],
            }
            for resource in RESOURCE_PATHS
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
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    require_private(TMP_ROOT, "tmp root")
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            destination = stage / resource
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(packed)
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
    for resource, packed in bundle.packed.items():
        candidate_resource = output / resource
        require(candidate_resource.is_file() and candidate_resource.read_bytes() == packed, f"private candidate differs: {resource}")
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
