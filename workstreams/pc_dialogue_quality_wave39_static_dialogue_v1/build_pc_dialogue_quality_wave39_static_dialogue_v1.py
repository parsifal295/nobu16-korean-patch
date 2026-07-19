#!/usr/bin/env python3
"""Build a private PC-only static-dialogue correction candidate for Wave 39.

Forty-one high-confidence static Base/PK dialogue records are rebuilt without
moving markers, opaque spans, or manual linebreaks.  The builder cannot write
Steam resources, operate Git, contact a network, or publish a release.
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
W37_HELPER = REPO / "workstreams" / "pc_dialogue_quality_wave37_runtime_slots_v1" / "build_pc_dialogue_quality_wave37_runtime_slots_v1.py"
W37_HELPER_SHA256 = "A389058A996A3D2F6BC3E0C6222849D86617F71FD12EB6C2D77077A0A89870CE"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave39-static-dialogue.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave39-static-dialogue-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave39-static-dialogue-manifest.v1"


class Wave39Error(RuntimeError):
    """Raised when a static source, structure, or private output differs."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave39Error(label)


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


def load_w37() -> Any:
    require(W37_HELPER.is_file(), "Wave 37 helper is absent")
    require(sha256_path(W37_HELPER) == W37_HELPER_SHA256, "pinned Wave 37 helper differs")
    spec = importlib.util.spec_from_file_location("wave39_imported_wave37", W37_HELPER)
    if spec is None or spec.loader is None:
        raise Wave39Error("cannot load Wave 37 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W37 = load_w37()
W27 = W37.W27
BASE_RESOURCE = W37.BASE_RESOURCE
PK_RESOURCE = W37.PK_RESOURCE
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
    PK_RESOURCE: STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
}
INPUT_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_422, "sha256": "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"},
    PK_RESOURCE: {"size": 1_806_542, "sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"},
}
TARGET_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_414, "sha256": "E3BDC4EE13EEA030904842A42F9426FDCBCD05D59B50FABF0C77DE4E9784C81B", "raw_size": 1_498_512, "raw_sha256": "E039C0DC658355F16A86D3CAE69B97DB0BD7D080D5112773341D654E6D1BE39D"},
    PK_RESOURCE: {"size": 1_806_566, "sha256": "CC81E750BE0BC4226BC251D2C84E09F09FF3E9CF257D9366E41D63DF368D5E69", "raw_size": 1_799_484, "raw_sha256": "9BC271F317D5FC3847E1FC123786670DC5F3B716A60BFABB2698C1A875954248"},
}


@dataclass(frozen=True)
class Change:
    name: str
    resource: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    rationale: str
    base_display_qa_required: bool = False
    pk_display_qa_required: bool = False


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Project-authored Korean targets.  The source files themselves remain external.
CHANGES = (
    Change("base_ashikaga_only_1848", BASE_RESOURCE, (6, 1848), ("아시카가 가문만 실행할 수 있습니다",), "아시카가 가문 외에는 실행할 수 없다는 정적 UI 뜻을 자연스럽게 복원한다."),
    Change("base_koga_ashikaga_only_4039", BASE_RESOURCE, (6, 4039), ("고가 아시카가 가문이 아니면 취임할 수 없습니다",), "고가 아시카가 가문 전용 조건을 복원한다.", True),
    Change("base_koga_ashikaga_only_4045", BASE_RESOURCE, (6, 4045), ("고가 아시카가 가문이 아니면 취임할 수 없습니다",), "고가 아시카가 가문 전용 조건을 복원한다.", True),
    Change("base_tsunokuma_3772", BASE_RESOURCE, (9, 3772), ("이 우세한 상황에서 강화를 하라니…?\n", "쓰노쿠마", " 주군은 지나치게 소극적이오!"), "고유명과 주군 사이의 단어 경계를 복원한다."),
    Change("base_tanaka_saeki_3774", BASE_RESOURCE, (9, 3774), ("기타키타", "와 ", "사에키", "가 선수를 쳤다고…!?\n강화를 깨고 오토모를 칠 셈인가…!"), "두 인명, 조사, 원문의 전개를 복원한다."),
    Change("base_yoshihiro_3783", BASE_RESOURCE, (9, 3783), ("요시히로", "는 강가에 진을 치고\n복병을 들키지 않도록 하라"), "모음으로 끝나는 인명 뒤의 보조사를 바로잡는다."),
    Change("base_takajogawa_3793", BASE_RESOURCE, (9, 3793), ("돌격이다!\n저놈들을 ", "다카조강", "에 처넣어라!"), "목적어와 강조된 강 이름 사이의 공백을 복원한다."),
    Change("base_otomo_tsunokuma_3799", BASE_RESOURCE, (9, 3799), ("오토모", "의 군사님은 반드시 베어라\n", "쓰노쿠마", " 없는 ", "오토모", "는 두렵지 않다"), "쓰노쿠마 없는 오토모를 두려워할 필요 없다는 원문 뜻을 복원한다."),
    Change("base_demon_shimazu_3800", BASE_RESOURCE, (9, 3800), ("이것은 ", "귀신 시마즈", "의 부대인가…!\n", "오토모", "를 위해서라도 살아 돌아가야…"), "지시어·별칭·세력명 사이의 단어 경계와 목적격을 복원한다."),
    Change("base_tsunokuma_17_3", BASE_RESOURCE, (17, 3), ("이 우세한 상황에서 강화를 하라니…?\n", "쓰노쿠마", " 주군은 지나치게 소극적이오!"), "고유명과 주군 사이의 단어 경계를 복원한다."),
    Change("base_yoshihiro_17_14", BASE_RESOURCE, (17, 14), ("요시히로", "는 강가에 진을 치고\n복병을 들키지 않도록 하라"), "모음으로 끝나는 인명 뒤의 보조사를 바로잡는다."),
    Change("base_takajogawa_17_24", BASE_RESOURCE, (17, 24), ("돌격이다!\n저놈들을 ", "다카조강", "에 처넣어라!"), "목적어와 강조된 강 이름 사이의 공백을 복원한다."),
    Change("base_otomo_tsunokuma_17_30", BASE_RESOURCE, (17, 30), ("오토모", "의 군사님은 반드시 베어라\n", "쓰노쿠마", " 없는 ", "오토모", "는 두렵지 않다"), "쓰노쿠마 없는 오토모를 두려워할 필요 없다는 원문 뜻을 복원한다."),
    Change("base_demon_shimazu_17_31", BASE_RESOURCE, (17, 31), ("이것은 ", "귀신 시마즈", "의 부대인가…!\n", "오토모", "를 위해서라도 살아 돌아가야…"), "지시어·별칭·세력명 사이의 단어 경계와 목적격을 복원한다."),
    Change("pk_oni_mino_3880", PK_RESOURCE, (9, 3880), ("나를 얕봤군!\n이 ", "오니 미노", "에게 잔꾀는 통하지 않는다!"), "지시어와 별칭 사이의 단어 경계를 복원한다.", pk_display_qa_required=True),
    Change("pk_oni_mino_3881", PK_RESOURCE, (9, 3881), ("이 ", "오니 미노", "에게\n잔꾀는 통하지 않는다!"), "지시어와 별칭 사이의 단어 경계를 복원한다."),
    Change("pk_yasha_mino_3892", PK_RESOURCE, (9, 3892), ("안 통한다, 안 통해!\n잔꾀로는 ", "야샤미노", "를 쓰러뜨릴 수 없다!"), "조사와 별칭 사이의 단어 경계를 복원한다."),
    Change("pk_yasha_mino_3914", PK_RESOURCE, (9, 3914), ("이 ", "야샤미노", "는\n잔꾀로 쓰러뜨릴 수 없다!"), "지시어와 별칭 사이의 단어 경계를 복원한다."),
    Change("pk_sasano_saizo_3921", PK_RESOURCE, (9, 3921), ("이 ", "사사노 사이조", "의 창을\n네 몸으로 받아 보아라!"), "지시어와 별칭 사이의 단어 경계를 복원한다."),
    Change("pk_tsunokuma_4090", PK_RESOURCE, (9, 4090), ("이 우세한 상황에서 강화를 하라니…?\n", "쓰노쿠마", " 주군은 지나치게 소극적이오!"), "고유명과 주군 사이의 단어 경계를 복원한다."),
    Change("pk_tanaka_saeki_4092", PK_RESOURCE, (9, 4092), ("기타키타", "와 ", "사에키", "가 선수를 쳤다고…!?\n강화를 깨고 오토모를 칠 셈인가…!"), "두 인명, 조사, 원문의 전개를 복원한다."),
    Change("pk_yoshihiro_4101", PK_RESOURCE, (9, 4101), ("요시히로", "는 강가에 진을 치고\n복병을 들키지 않도록 하라"), "모음으로 끝나는 인명 뒤의 보조사를 바로잡는다."),
    Change("pk_takajogawa_4111", PK_RESOURCE, (9, 4111), ("돌격이다!\n저놈들을 ", "다카조강", "에 처넣어라!"), "목적어와 강조된 강 이름 사이의 공백을 복원한다."),
    Change("pk_otomo_tsunokuma_4117", PK_RESOURCE, (9, 4117), ("오토모", "의 군사님은 반드시 베어라\n", "쓰노쿠마", " 없는 ", "오토모", "는 두렵지 않다"), "쓰노쿠마 없는 오토모를 두려워할 필요 없다는 원문 뜻을 복원한다."),
    Change("pk_demon_shimazu_4118", PK_RESOURCE, (9, 4118), ("이것은 ", "귀신 시마즈", "의 부대인가…!\n", "오토모", "를 위해서라도 살아 돌아가야…"), "지시어·별칭·세력명 사이의 단어 경계와 목적격을 복원한다."),
    Change("pk_tsunokuma_17_3", PK_RESOURCE, (17, 3), ("이 우세한 상황에서 강화를 하라니…?\n", "쓰노쿠마", " 주군은 지나치게 소극적이오!"), "고유명과 주군 사이의 단어 경계를 복원한다."),
    Change("pk_yoshihiro_17_14", PK_RESOURCE, (17, 14), ("요시히로", "는 강가에 진을 치고\n복병을 들키지 않도록 하라"), "모음으로 끝나는 인명 뒤의 보조사를 바로잡는다."),
    Change("pk_takajogawa_17_25", PK_RESOURCE, (17, 25), ("돌격이다!\n저놈들을 ", "다카조강", "에 처넣어라!"), "목적어와 강조된 강 이름 사이의 공백을 복원한다."),
    Change("pk_otomo_tsunokuma_17_31", PK_RESOURCE, (17, 31), ("오토모", "의 군사님은 반드시 베어라\n", "쓰노쿠마", " 없는 ", "오토모", "는 두렵지 않다"), "쓰노쿠마 없는 오토모를 두려워할 필요 없다는 원문 뜻을 복원한다."),
    Change("pk_demon_shimazu_17_32", PK_RESOURCE, (17, 32), ("이것은 ", "귀신 시마즈", "의 부대인가…!\n", "오토모", "를 위해서라도 살아 돌아가야…"), "지시어·별칭·세력명 사이의 단어 경계와 목적격을 복원한다."),
    Change("pk_vanguard_17_36", PK_RESOURCE, (17, 36), ("선봉 부대", "를 ", "요충지", "까지 유인하라!"), "선봉 부대의 목적격과 요충지 앞 공백을 복원한다."),
    Change("pk_vanguard_17_37", PK_RESOURCE, (17, 37), ("선봉 부대", "를 ", "요충지", "까지 유인하라!", " 성공"), "선봉 부대의 목적격과 요충지 앞 공백을 복원한다."),
    Change("pk_vanguard_17_38", PK_RESOURCE, (17, 38), ("선봉 부대", "를 ", "요충지", "까지 유인하라!", " 실패"), "선봉 부대의 목적격과 요충지 앞 공백을 복원한다."),
    Change("pk_takeda_oda_17_80", PK_RESOURCE, (17, 80), ("다케다", " 기마대… 무시무시한 기세로군!\n우리 ", "오다 가문", "이 맞설 방법이 있는가…?"), "기마대·가문 앞 공백과 모음 뒤 주격 조사를 복원한다."),
    Change("pk_forest_objective_17_186", PK_RESOURCE, (17, 186), ("숲가의 요충지", "를 차지하라"), "요충지 뒤의 목적격을 복원한다."),
    Change("pk_forest_objective_17_187", PK_RESOURCE, (17, 187), ("숲가의 요충지", "를 차지하라", " 성공"), "요충지 뒤의 목적격을 복원한다."),
    Change("pk_forest_objective_17_188", PK_RESOURCE, (17, 188), ("숲가의 요충지", "를 차지하라", " 실패"), "요충지 뒤의 목적격을 복원한다."),
    Change("pk_mori_17_401", PK_RESOURCE, (17, 401), ("우리는 식사 중이라고 전해라!\n…이번 싸움에서, ", "모리 가문", "은 관망한다!"), "쉼표 뒤 공백과 가문 뒤의 주제 조사를 복원한다."),
    Change("pk_retreat_17_956", PK_RESOURCE, (17, 956), ("적의 ", "퇴각 지점", "을 파괴하라"), "수식어·목적어 사이 공백과 목적격을 복원한다."),
    Change("pk_retreat_17_957", PK_RESOURCE, (17, 957), ("적의 ", "퇴각 지점", "을 파괴하라", " 성공"), "수식어·목적어 사이 공백과 목적격을 복원한다."),
    Change("pk_retreat_17_958", PK_RESOURCE, (17, 958), ("적의 ", "퇴각 지점", "을 파괴하라", " 실패"), "수식어·목적어 사이 공백과 목적격을 복원한다."),
)

if len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 39 must contain unique resource coordinates")


def source_languages(resource: str) -> tuple[str, ...]:
    return ("BASE_JP", "BASE_SC", "BASE_TC") if resource == BASE_RESOURCE else ("PK_JP", "PK_EN", "PK_SC", "PK_TC")


def validate_change(change: Change, before: Any, sources: Mapping[str, Mapping[tuple[int, int], Any]], advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"{change.name} literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} terminator differs")
    before_opaque = W27.opaque_spans(before)
    require(not W27.complete_0143_commands(before_opaque), f"{change.name} contains an unreviewed 0143 command")
    require(not any(span.startswith(b"\x02") for span in before_opaque), f"{change.name} contains a runtime opcode")
    before_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(before_text.count("\n") == target_text.count("\n"), f"{change.name} manual line count differs")
    layout = W27.line_layout(change.target_literals, advance)
    require(not layout["wide_fallback_codepoints"], f"{change.name} uses a fallback glyph")
    anchor = {}
    for language in source_languages(change.resource):
        record = sources[language].get(change.coordinate)
        require(record is not None, f"{change.name} {language} source record is absent")
        anchor[language] = W27.sha256_bytes(record.data)
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"{change.name} target literals differ")
    require(W27.opaque_spans(after) == before_opaque, f"{change.name} opaque spans differ")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.name} marker topology differs")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} target terminator differs")
    return rebuilt, {
        "name": change.name,
        "resource": change.resource,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "current_record_sha256": W27.sha256_bytes(before.data),
        "target_record_sha256": W27.sha256_bytes(after.data),
        "target_record_size": len(after.data),
        "target_line_widths_px": list(layout["line_widths_px"]),
        "base_display_qa_required": change.base_display_qa_required,
        "pk_display_qa_required": change.pk_display_qa_required,
        "pc_source_record_sha256": anchor,
        "rationale": change.rationale,
    }


def prepare_candidate() -> CandidateBundle:
    current_packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = W37.reject_switch(path, f"current Steam {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"current Steam profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"current Steam {resource}")
        current_packed[resource] = packed
        current_records[resource] = W27.records_by_coordinate(packed)
    sources, source_hashes = W37.load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_records[change.resource].get(change.coordinate)
        require(before is not None and change.coordinate not in replacements[change.resource], f"current coordinate differs: {change.name}")
        replacement, row = validate_change(change, before, sources, advance)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)
    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in current_packed.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 39 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after = W27.records_by_coordinate(candidate)
        changed = {coordinate for coordinate in current_records[resource] if current_records[resource][coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected and set(current_records[resource]) == set(after), f"changed record scope differs: {resource}")
        packed_output[resource] = candidate
        raw_output[resource] = raw
    for resource, profile in TARGET_PROFILES.items():
        require(len(packed_output[resource]) == profile["size"] and sha256_bytes(packed_output[resource]) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw_output[resource]) == profile["raw_size"] and sha256_bytes(raw_output[resource]) == profile["raw_sha256"], f"target raw profile differs: {resource}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {"platform": "Steam PC", "pc_jp_en_sc_tc_only": True, "switch_korean_read": False, "steam_game_resource_written": False, "steam_apply_or_transaction_capability": "absent", "git_operation_capability": "absent", "network_capability": "absent", "release_capability": "absent"},
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "input": INPUT_PROFILES,
        "target": TARGET_PROFILES,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "base_display_qa_required_coordinates": [row["coordinate"] for row in rows if row["base_display_qa_required"]],
        "pk_display_qa_required_coordinates": [row["coordinate"] for row in rows if row["pk_display_qa_required"]],
        "layout_policy": "Manual linebreak count is preserved for every static record. Base renderer scale is not statically proven, so explicitly marked long Base UI rows require display QA before application. A PK row at the 912 px static threshold is also explicitly held for display QA.",
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {resource: {"input": INPUT_PROFILES[resource], "output": TARGET_PROFILES[resource], "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource]} for resource in RESOURCE_PATHS},
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


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave39Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            path = stage / resource
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed)
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
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "base_display_qa_required_coordinates": ["6:4039", "6:4045"], "pk_display_qa_required_coordinates": ["9:3880"], "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "base_display_qa_required_coordinates": ["6:4039", "6:4045"], "pk_display_qa_required_coordinates": ["9:3880"], "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
