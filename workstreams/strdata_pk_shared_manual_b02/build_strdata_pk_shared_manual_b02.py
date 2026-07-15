#!/usr/bin/env python3
"""Build the next disjoint shared-runtime strdata manual batch B02."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
B01_ROOT = REPO_ROOT / "workstreams" / "strdata_pk_shared_manual_b01"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module(
    "nobu16_strdata_pk_shared_manual_b02_base",
    B01_ROOT / "build_strdata_pk_shared_manual_b01.py",
)
common = base.common
direct = base.direct
ManualBatchError = base.ManualBatchError
RESOURCE = base.RESOURCE
OVERLAY_SCHEMA = base.OVERLAY_SCHEMA
TARGET_CATALOG = base.TARGET_CATALOG
PROGRESS = base.PROGRESS
DEFAULT_SWITCH_ZIP = base.DEFAULT_SWITCH_ZIP
HAN_OR_KANA_RE = base.HAN_OR_KANA_RE

BATCH_ID = "strdata-pk-shared-manual-b02-final-27-v1"
OVERLAY_ID = BATCH_ID
OVERLAY_NAME = "strdata_ko_pk_shared_manual_b02_final_27.v1.json"
EVIDENCE_NAME = "strdata_pk_shared_manual_b02_evidence.v1.json"
REVIEW_NAME = "strdata_pk_shared_manual_b02_review.v1.json"
VALIDATION_NAME = "translation_validation.v1.json"
SELF_LOGICAL_PATH = f"workstreams/strdata_pk_shared_manual_b02/public/{OVERLAY_NAME}"

PREDECESSORS = base.PREDECESSORS + (
    {
        "path": "workstreams/strdata_pk_shared_manual_b01/public/strdata_ko_pk_shared_manual_b01_206.v1.json",
        "entry_count": 206,
        "size": 47_902,
        "sha256": "5455DEED73967A2F2435E968AAF1C9EE6B50B96B2B750B58E0070B3301D8949A",
    },
)
USER_RESERVED = {
    "path": "workstreams/strdata/public/strdata_ko_name_labels_b00s0000_0099.v0.1.json",
    "entry_count": 100,
    "size": 18_874,
    "sha256": "9B1C3F1B2C3C1BFC44974C6C2E1573DA6C48433B9E945EEF6EC5BE2C54B85F24",
    "coordinates_sha256": "19B2C39B5C70E2A8F372F344C7A71C024DB0A3F2FAF4FFF392BFC38170EDB49B",
}

SELECTED_COORDINATES = (
    (0, 2086), (0, 2089), (0, 17887), (0, 17908), (0, 17913),
    (0, 17914), (0, 17915), (0, 17916), (0, 17938), (0, 17939),
    (0, 17940), (0, 17965), (0, 17967), (0, 18012), (1, 39),
    (1, 461), (1, 462), (1, 464), (1, 466), (1, 468), (1, 967),
    (2, 805), (2, 944), (2, 1104), (2, 1238), (3, 60), (3, 92),
)
SELECTED_COORDINATES_SHA256 = "1FCA967B1E2AD6537A1FA54DE1E7DE8FB3AAC4381A202A7EDB29FA829D07C762"
OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "SC": "3C186886A4760532F68714FD860F6D7D4AC68A50F951DB5C1952B903EE7C5ADF",
    "JP": "CB2965B6BABD124F89B84033EF81EBE401A97F7D9A5460F8B752DAFECED4C3E0",
    "SW": "860315CEFB32313FE61C7A7CF8F9CB71A1C7588933F6BBD8B8EDBCB271DC1AD7",
}
STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy": {
        "count": 1739,
        "coordinates_sha256": "0C1CA4CB3FD746770742B1D6E4A82631E27703D77358E2B22FBFEC6A25591BF0",
    },
    "ascii_lookup_key": {
        "count": 133,
        "coordinates_sha256": "DA7C9D5ECDA0D8A1692E98212046FDFCA6FA87B5614FB914DF071D6D4702D180",
    },
    "format_symbol_or_nonsemantic": {
        "count": 60,
        "coordinates_sha256": "D4A7862C0EEE23AB876A617E8B894845E257320FD8C5EE7DA4B3D746E15E942D",
    },
}
STRUCTURAL_EXCLUSION_COUNT = 1932
STRUCTURAL_EXCLUSION_SHA256 = "60F5957227716C72AE235484427C870FC68354BF334EEDE3868DB137002943B3"

TRANSLATIONS: dict[tuple[int, int], str] = {
    (0, 2086): "차",
    (0, 2089): "네",
    (0, 17887): "그야말로 청천벽력이었다",
    (0, 17908): "……오와리 원정은 갑작스레 막을 내렸다",
    (0, 17913): "그 이름은————",
    (0, 17914): "오다, 노부나가",
    (0, 17915): "오다 노부나가는 천하포무의 실현을\n목표로 한 전국의 패자",
    (0, 17916): "그 행보에는 한 치의 빈틈도 없었다",
    (0, 17938): "인간 오십 년",
    (0, 17939): "하늘과 땅의 영원함에 비하면",
    (0, 17940): "덧없는 꿈과도 같으니",
    (0, 17965): "——일명 “노히메”라 불렸다.",
    (0, 17967): "다케다 가쓰요리의 대군이 미카와 나가시노성을 포위했다.",
    (0, 18012): "그 뒤로도 용과 호랑이의 싸움은 계속되었다……",
    (1, 39): "←백스페이스",
    (1, 461): "이",
    (1, 462): "삼",
    (1, 464): "오",
    (1, 466): "칠",
    (1, 468): "구",
    (1, 967): "%d×%d 픽셀",
    (2, 805): (
        "난부 가신. 노부자네의 장남. 구노헤성주. 우쿄라 칭했다. "
        "구노헤가는 난부가의 방계로, 난부가의 시조 미쓰유키의 여섯째 "
        "아들인 난부 유키쓰라를 시조로 한다고 한다. 하치노헤 노부나가의 "
        "딸을 아내로 맞았다."
    ),
    (2, 944): (
        "도쿠가와 가신. 도쿠가와 사천왕의 한 사람. ‘무’의 깃발을 내걸고 "
        "전장을 질주하며 각지에서 발군의 공을 세웠다. 만년에 ‘노신이 "
        "권세를 다투는 것은 망국의 조짐’이라며 로주 취임을 사퇴했다."
    ),
    (2, 1104): (
        "다테 가신. 데루무네와 마사무네 2대를 섬기며 각지의 합전에서 "
        "공을 세웠다. 스리아게하라 합전에서는 다테 시게자네와 함께 다테군의 "
        "주력을 이루었다. 투구에는 금색 ‘야’ 자의 큰 장식물을 달았다."
    ),
    (2, 1238): (
        "미마사카의 호족. 이치노세성주. 우키타 나오이에의 미마사카 침공군에 "
        "패해 그 신하가 되었다. 전장에서 맞붙어 싸우는 기술을 바탕으로 일본에서 "
        "가장 오래된 유술 유파인 다케우치류 유술을 창시했다."
    ),
    (3, 60): (
        "나오에 가네쓰구가 쓰던 투구. 앞장식의 ‘사랑 애’ 자는 우에스기 겐신이 "
        "부동명왕 앞장식 투구를 애용한 것을 본떠 애염명왕 또는 아타고 권현에서 "
        "따온 것이라 하나, 정확한 유래는 알 수 없다."
    ),
    (3, 92): (
        "고대 중국의 병법서. 무경칠서의 하나. 정치와 전술, 용병, 전략에 관한 "
        "선인의 지혜를 6권으로 정리한 것이다. ‘도’란 병법서를 넣는 가죽 주머니를 뜻한다."
    ),
}

EXPECTED = {
    "total_slots": 32_311,
    "target_count": 26_690,
    "registered_predecessor_coverage": 24_631,
    "user_reserved_count": 100,
    "remaining_after_reservation": 1_959,
    "selected_count": 27,
    "selected_per_block": {"0": 14, "1": 7, "2": 4, "3": 2, "4": 0},
    "coverage_after": 24_658,
    "catalog_remaining_after": 2_032,
    "semantic_remaining_after": 0,
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object)
    if not isinstance(value, dict):
        raise ManualBatchError(f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any, out_root: Path) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": path.relative_to(out_root).as_posix(), "size": len(blob), "sha256": sha256(blob)}


def load_registered_and_reserved(
    repo_root: Path, pc_sc: dict[tuple[int, int], str]
) -> tuple[dict[tuple[int, int], str], list[dict[str, Any]], dict[tuple[int, int], str]]:
    values: dict[tuple[int, int], str] = {}
    snapshots: list[dict[str, Any]] = []
    for descriptor in PREDECESSORS:
        path = repo_root / descriptor["path"]
        blob = path.read_bytes()
        if len(blob) != descriptor["size"] or sha256(blob) != descriptor["sha256"]:
            raise ManualBatchError(f"predecessor pin changed: {descriptor['path']}")
        current = base._validate_overlay_entries(read_json(path), pc_sc, descriptor["path"])
        if len(current) != descriptor["entry_count"] or set(current) & set(values):
            raise ManualBatchError(f"predecessor count or disjointness changed: {descriptor['path']}")
        values.update(current)
        snapshots.append(dict(descriptor))
    if len(values) != EXPECTED["registered_predecessor_coverage"]:
        raise ManualBatchError("registered predecessor coordinate union changed")
    reserved_path = repo_root / USER_RESERVED["path"]
    reserved_blob = reserved_path.read_bytes()
    if len(reserved_blob) != USER_RESERVED["size"] or sha256(reserved_blob) != USER_RESERVED["sha256"]:
        raise ManualBatchError("user-reserved overlay pin changed")
    reserved = base._validate_overlay_entries(read_json(reserved_path), pc_sc, USER_RESERVED["path"])
    if (
        len(reserved) != USER_RESERVED["entry_count"]
        or canonical_hash([list(value) for value in sorted(reserved)]) != USER_RESERVED["coordinates_sha256"]
        or set(reserved) & set(values)
    ):
        raise ManualBatchError("user-reserved coordinate scope changed or overlaps registered predecessors")
    return values, snapshots, reserved


def classify_structural(
    coordinates: set[tuple[int, int]], pc_sc: dict[tuple[int, int], str]
) -> dict[str, tuple[tuple[int, int], ...]]:
    groups: dict[str, list[tuple[int, int]]] = {key: [] for key in STRUCTURAL_EXCLUSION_PINS}
    for coordinate in sorted(coordinates):
        text = pc_sc[coordinate]
        if text.strip().lower() == "dummy":
            reason = "placeholder_dummy"
        elif re.fullmatch(r"[\x00-\x7F\s]+", text.strip()) and re.search(r"[A-Za-z]", text):
            reason = "ascii_lookup_key"
        else:
            reason = "format_symbol_or_nonsemantic"
        groups[reason].append(coordinate)
    frozen = {key: tuple(value) for key, value in groups.items()}
    for reason, pin in STRUCTURAL_EXCLUSION_PINS.items():
        values = frozen[reason]
        if len(values) != pin["count"] or canonical_hash([list(value) for value in values]) != pin["coordinates_sha256"]:
            raise ManualBatchError(f"structural exclusion group changed: {reason}")
    all_values = sorted(value for values in frozen.values() for value in values)
    if len(all_values) != STRUCTURAL_EXCLUSION_COUNT or canonical_hash([list(value) for value in all_values]) != STRUCTURAL_EXCLUSION_SHA256:
        raise ManualBatchError("combined structural exclusion scope changed")
    return frozen


def make_models(inputs: dict[str, Any], classified: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    pc_sc = classified["pc_sc"]
    targets, target_snapshot = base.load_target_catalog(repo_root / TARGET_CATALOG.relative_to(REPO_ROOT))
    predecessors, predecessor_snapshots, reserved = load_registered_and_reserved(repo_root, pc_sc)
    selected = set(SELECTED_COORDINATES)
    remaining = targets - set(predecessors) - set(reserved)
    if (
        len(remaining) != EXPECTED["remaining_after_reservation"]
        or len(selected) != EXPECTED["selected_count"]
        or canonical_hash([list(value) for value in SELECTED_COORDINATES]) != SELECTED_COORDINATES_SHA256
        or selected - remaining
        or set(TRANSLATIONS) != selected
    ):
        raise ManualBatchError("selected or remaining coordinate scope changed")
    structural = classify_structural(remaining - selected, pc_sc)
    if selected | {value for values in structural.values() for value in values} != remaining:
        raise ManualBatchError("selection and structural exclusions do not exhaust remaining coordinates")
    per_block = Counter(str(block_id) for block_id, _slot_id in selected)
    actual_per_block = {str(block_id): per_block[str(block_id)] for block_id in range(5)}
    if actual_per_block != EXPECTED["selected_per_block"]:
        raise ManualBatchError("selected per-block scope changed")
    rowsets = {
        language: canonical_hash([
            {"block_id": block_id, "slot_id": slot_id, "utf16le_sha256": text_hash(classified[key][(block_id, slot_id)])}
            for block_id, slot_id in SELECTED_COORDINATES
        ])
        for language, key in (("SC", "pc_sc"), ("JP", "pc_jp"), ("SW", "switch"))
    }
    if rowsets != OFFICIAL_SELECTED_ROWSET_SHA256:
        raise ManualBatchError("selected official rowset changed")
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    by_source: dict[str, set[str]] = defaultdict(set)
    for coordinate in SELECTED_COORDINATES:
        source = pc_sc[coordinate]
        replacement = TRANSLATIONS[coordinate]
        if common.invariant_mismatches(source, replacement):
            raise ManualBatchError(f"format invariant mismatch: {coordinate}")
        if HAN_OR_KANA_RE.search(replacement) or not any(0xAC00 <= ord(character) <= 0xD7A3 for character in replacement):
            raise ManualBatchError(f"replacement is not source-free Hangul text: {coordinate}")
        by_source[source].add(replacement)
        row = {
            "block_id": coordinate[0],
            "slot_id": coordinate[1],
            "source_sc_utf16le_sha256": text_hash(source),
            "ko": replacement,
        }
        entries.append(row)
        evidence_entries.append({
            "block_id": coordinate[0], "slot_id": coordinate[1],
            "pc_sc_utf16le_sha256": text_hash(source),
            "pc_jp_utf16le_sha256": text_hash(classified["pc_jp"][coordinate]),
            "switch_v13_utf16le_sha256": text_hash(classified["switch"][coordinate]),
            "ko_utf16le_sha256": text_hash(replacement),
            "format_invariants_equal": True, "registered_predecessor_disjoint": True,
            "user_reserved_disjoint": True, "runtime_reviewed": False,
        })
        review_entries.append({
            "block_id": coordinate[0], "slot_id": coordinate[1],
            "status": "translated", "human_review_required": True,
            "runtime_reviewed": False, "format_invariants_equal": True,
        })
    if any(len(values) != 1 for values in by_source.values()):
        raise ManualBatchError("repeated SC source groups are translation-inconsistent")
    selection = {
        "registered_predecessor_coverage": len(predecessors),
        "user_reserved_coordinate_count": len(reserved),
        "remaining_after_user_reservation": len(remaining),
        "selected_count": len(selected),
        "selected_coordinates_sha256": SELECTED_COORDINATES_SHA256,
        "selected_per_block": actual_per_block,
        "structural_exclusion_count": STRUCTURAL_EXCLUSION_COUNT,
        "semantic_remaining_after": 0,
    }
    overlay = {
        "schema": OVERLAY_SCHEMA, "overlay_id": OVERLAY_ID, "resource": RESOURCE,
        "base_language": "SC", "entry_count": len(entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "defaults": {"status": "translated"}, "entries": entries,
    }
    evidence = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-evidence.v1", "batch_id": BATCH_ID,
        "resource": RESOURCE, "entry_count": len(entries), "contains_commercial_source_text": False,
        "contains_complete_game_resource": False, "target_catalog": target_snapshot,
        "predecessors": predecessor_snapshots,
        "user_reserved": {**USER_RESERVED, "read_only": True, "disjoint": True},
        "selection": selection, "official_selected_rowset_sha256": rowsets,
        "structural_exclusions": {
            reason: {"count": len(values), "coordinates_sha256": STRUCTURAL_EXCLUSION_PINS[reason]["coordinates_sha256"]}
            for reason, values in structural.items()
        },
        "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-review.v1", "batch_id": BATCH_ID,
        "resource": RESOURCE, "entry_count": len(entries),
        "review_policy": {"pc_sc_jp_switch_context_checked": True, "user_reserved_read_only": True,
                          "block_slot_exact": True, "source_free_public_artifacts": True},
        "entries": review_entries,
    }
    return {
        "overlay": overlay, "evidence": evidence, "review": review,
        "values": dict(TRANSLATIONS), "predecessor_values": predecessors,
        "reserved_values": reserved, "selection": selection, "target_snapshot": target_snapshot,
    }


def audit_progress_registration(
    progress_path: Path, repo_root: Path, pc_sc: dict[tuple[int, int], str],
    target_coordinates: set[tuple[int, int]], predecessor_coordinates: set[tuple[int, int]],
    reserved_coordinates: set[tuple[int, int]], self_overlay: dict[str, Any],
) -> dict[str, Any]:
    progress = read_json(progress_path)
    resources = [row for row in progress.get("shared_strings", []) if row.get("path") == RESOURCE]
    if len(resources) != 1:
        raise ManualBatchError("progress shared strdata resource is not unique")
    patterns = resources[0].get("overlay_globs")
    expected = [row["path"] for row in PREDECESSORS]
    if not isinstance(patterns, list) or patterns[: len(expected)] != expected:
        raise ManualBatchError("registered predecessor boundary changed")
    self_blob = encode_json(self_overlay)
    self_coordinates = {(entry["block_id"], entry["slot_id"]) for entry in self_overlay["entries"]}
    self_count = 0
    successor_coordinates: set[tuple[int, int]] = set()
    successor_paths: list[str] = []
    for pattern in patterns[len(expected):]:
        if not isinstance(pattern, str) or ".." in Path(pattern).parts:
            raise ManualBatchError("unsafe progress overlay path")
        matches = sorted(repo_root.glob(pattern))
        if len(matches) != 1:
            raise ManualBatchError(f"progress path must resolve exactly once: {pattern}")
        current = base._validate_overlay_entries(read_json(matches[0]), pc_sc, pattern)
        if pattern == SELF_LOGICAL_PATH:
            if matches[0].read_bytes() != self_blob:
                raise ManualBatchError("self registration is not deterministic")
            self_count += 1
            continue
        coordinates = set(current)
        if coordinates - target_coordinates or coordinates & (predecessor_coordinates | reserved_coordinates | self_coordinates | successor_coordinates):
            raise ManualBatchError(f"successor target or overlap contract failed: {pattern}")
        successor_coordinates.update(coordinates)
        successor_paths.append(pattern)
    if self_count > 1:
        raise ManualBatchError("self overlay is registered more than once")
    return {
        "predecessor_registration_count": len(PREDECESSORS), "self_registration_count": self_count,
        "self_registration_states_supported": [0, 1], "successor_overlay_count": len(successor_paths),
        "successor_coordinate_count": len(successor_coordinates), "successor_paths": successor_paths,
        "user_reserved_excluded_from_all_registration_roles": True,
    }


def build(
    game_root: Path, switch_zip: Path, repo_root: Path, out_root: Path,
    candidate_out: Path, progress_path: Path,
) -> dict[str, Any]:
    inputs = direct.load_inputs(game_root, switch_zip)
    classified = direct.classify_direct(inputs)
    models = make_models(inputs, classified, repo_root)
    targets, _ = base.load_target_catalog(repo_root / TARGET_CATALOG.relative_to(REPO_ROOT))
    progress_audit = audit_progress_registration(
        progress_path, repo_root, classified["pc_sc"], targets,
        set(models["predecessor_values"]), set(models["reserved_values"]), models["overlay"],
    )
    integrated = {**models["predecessor_values"], **models["values"]}
    first, first_stats = base.build_candidate(inputs, integrated)
    second, second_stats = base.build_candidate(inputs, integrated)
    if first != second or first_stats != second_stats:
        raise ManualBatchError("candidate A/B builds differ")
    artifacts = {
        "overlay": write_json(out_root / "public" / OVERLAY_NAME, models["overlay"], out_root),
        "evidence": write_json(out_root / "evidence" / EVIDENCE_NAME, models["evidence"], out_root),
        "review": write_json(out_root / "review" / REVIEW_NAME, models["review"], out_root),
    }
    for artifact in artifacts.values():
        text = (out_root / artifact["path"]).read_text(encoding="utf-8")
        if "\x00" in text or HAN_OR_KANA_RE.search(text):
            raise ManualBatchError("public artifact contains NUL, Han, or Kana")
    candidate_out.parent.mkdir(parents=True, exist_ok=True)
    candidate_out.write_bytes(first)
    validation = {
        "schema": "nobu16.kr.strdata-pk-shared-manual-validation.v1", "batch_id": BATCH_ID,
        "resource": RESOURCE, "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "input_pins": {"pc_sc": direct.PC_SC_PIN, "pc_jp": direct.PC_JP_PIN,
                       "switch_v13": direct.SWITCH_PIN, "switch_zip": direct.ZIP_PIN,
                       "target_catalog": models["target_snapshot"]},
        "predecessors": {"entry_count": len(models["predecessor_values"]), "overlays": list(PREDECESSORS), "disjoint": True},
        "user_reserved": {**USER_RESERVED, "read_only": True, "disjoint": True},
        "selection": models["selection"],
        "coverage": {"target_count": EXPECTED["target_count"], "before": EXPECTED["registered_predecessor_coverage"],
                     "added": EXPECTED["selected_count"], "after": EXPECTED["coverage_after"],
                     "remaining": EXPECTED["catalog_remaining_after"], "semantic_remaining_excluding_reserved": 0},
        "format_contract": {"all_selected_invariants_equal": True, "han_or_kana_in_public_artifacts": 0,
                            "block_slot_counts_preserved": True, "all_nonselected_coordinates_preserved": True,
                            "repeated_source_groups_consistent": True},
        "progress_registration_audit": progress_audit, "candidate": first_stats,
        "reproducibility": {"in_memory_candidate_a_b_equal": True, "artifact_json_canonical": True},
        "artifacts": artifacts,
        "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False,
                   "user_untracked_strdata_workstream_read": True, "user_untracked_strdata_workstream_modified": False,
                   "progress_modified": False, "root_readme_modified": False, "font_modified": False,
                   "installed_game_files_modified": False, "deployment_performed": False, "commit_or_push_performed": False},
    }
    write_json(out_root / VALIDATION_NAME, validation, out_root)
    return validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    parser.add_argument("--progress", type=Path, default=PROGRESS)
    parser.add_argument("--candidate-out", type=Path, default=REPO_ROOT / "tmp/strdata_pk_shared_manual_b02/candidate" / RESOURCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = build(
        args.game_root.resolve(), args.switch_zip.resolve(), args.repo_root.resolve(),
        args.out_root.resolve(), args.candidate_out.resolve(), args.progress.resolve(),
    )
    print(f"entries={validation['selection']['selected_count']}")
    print(f"semantic_remaining={validation['selection']['semantic_remaining_after']}")
    for name, artifact in validation["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
