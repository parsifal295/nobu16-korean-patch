#!/usr/bin/env python3
"""Build the final 278 native PK msgdata semantic translations after batch 05."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
BATCH05_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch05"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module(
    "nobu16_msgdata_pk_native_batch06_base",
    BATCH05_ROOT / "build_msgdata_pk_native_batch05.py",
)
engine = base.base
common = base.common
BatchError = base.BatchError
sha256 = base.sha256
encode_json = base.encode_json
hash_json = base.hash_json

BATCH_ID = "pk_msgdata_native_batch06_final_278.v1"
RESOURCE = base.RESOURCE
STRING_COUNT = base.STRING_COUNT
OVERLAY_NAME = "msgdata_ko_pk_native_batch06_final_278.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch06_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch06_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch06/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = base.PROGRESS_RELATIVE
TARGET_CATALOG_RELATIVE = base.TARGET_CATALOG_RELATIVE
STOCK_SC_RELATIVE = base.STOCK_SC_RELATIVE
OFFICIAL_PINS = base.OFFICIAL_PINS
TARGET_RESOURCE_ROW_SHA256 = base.TARGET_RESOURCE_ROW_SHA256
TARGET_IDS_SHA256 = base.TARGET_IDS_SHA256
TARGET_COUNT = base.TARGET_COUNT

SELECTED_IDS = (
    2086, 2089, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327,
    3328, 3329, 11310, 11311, 14764, 14765, 14766, 15753, 15754, 15755,
    15758, 15759, 15760, 15761, 15762, 16403, 17432, 28760, 28761, 28762,
    28763, 28764, 28765, 28766, 28767, 28768, 28789, 28790, 28791, 28792,
    28793, 28844, 28845, 28846, 28847, 28848, 28849, 28850, 28851, 28852,
    28853, 28854, 28855, 28856, 28857, 28858, 28859, 28860, 28861, 28862,
    28863, 28864, 28929, 28930, 28931, 28932, 28933, 28934, 28935, 28936,
    28937, 28938, 28939, 28940, 28941, 28942, 28943, 28944, 28945, 28946,
    28947, 28948, 28949, 28950, 28951, 28952, 28953, 28954, 28955, 28956,
    28957, 28958, 28959, 28960, 28961, 28962, 28963, 28964, 28965, 28966,
    28967, 28968, 28969, 28970, 28971, 28972, 28973, 28974, 28975, 28976,
    28977, 28978, 28979, 28980, 28981, 28982, 28983, 28984, 28985, 28986,
    28987, 28988, 28989, 28990, 28991, 28992, 28993, 28994, 28995, 28996,
    28997, 28998, 28999, 29000, 29001, 29002, 29003, 29004, 29005, 29006,
    29007, 29008, 29009, 29010, 29011, 29012, 29013, 29014, 29015, 29016,
    29017, 29018, 29019, 29020, 29021, 29022, 29023, 29024, 29025, 29026,
    29027, 29028, 29029, 29030, 29031, 29032, 29033, 29034, 29035, 29036,
    29037, 29038, 29039, 29040, 29041, 29042, 29043, 29044, 29045, 29046,
    29047, 29048, 29049, 29050, 29051, 29052, 29053, 29054, 29055, 29056,
    29057, 29058, 29059, 29060, 29061, 29062, 29063, 29064, 29065, 29066,
    29067, 29068, 29069, 29070, 29071, 29072, 29073, 29074, 29075, 29076,
    29077, 29078, 29079, 29080, 29081, 29082, 29083, 29084, 29085, 29086,
    29087, 29088, 29089, 29090, 29091, 29092, 29093, 29094, 29095, 29096,
    29097, 29098, 29099, 29100, 29101, 29102, 29103, 29104, 29105, 29106,
    29107, 29108, 29109, 29110, 29111, 29112, 29113, 29114, 29179, 29180,
    29181, 29182, 29183, 29184, 29185, 29186, 29187, 29188, 29189, 29190,
    29191, 29192, 29193, 29194, 29195, 29196, 29197, 29198, 29199, 29200,
    29201, 29203, 29204, 29205, 29206, 29207, 29208,
)
SELECTED_IDS_SHA256 = "E77B4D4DBE83E6FA99E7418678C2BA36E8324F54471F07E5DD6CB8362E27724A"

STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 1759,
        "ids_sha256": "9001E169209B7120F0E2F73C3C67B0E980FC5EA59B2E3E5FDFFE6E9D1C3EE719",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 2331,
        "ids_sha256": "569C06CC38E4C11EA37008FE73362F5F0AC89B606E3BBDF0D422BDE7FB994385",
    },
    "format_or_control_only_token": {
        "count": 20,
        "ids_sha256": "544E7FF4E94C1F3B5BCED19E6C5C1730BCB4CD9D232F6E637384021DED3E6639",
    },
}
EXCLUDED_COUNT = 4110
EXCLUDED_IDS_SHA256 = "83756A7BE8E0E324EF0FC4B0513E7410CF27A3156C0F0084F8E7A2F93A7DE6EA"

TRANSLATIONS: dict[int, str] = {
    2086: "차", 2089: "네", 3319: "나쓰메", 3320: "히로쓰구", 3321: "마사쓰구",
    3322: "유키마사", 3323: "쓰카하라", 3324: "보쿠덴", 3325: "쓰보네",
    3326: "아사히", 3327: "아차", 3328: "가메주", 3329: "진자에몬",
    11310: "스이타", 11311: "에비에", 14764: "오다 히데오 가문",
    14765: "도미타 가문", 14766: "가타기리 가문", 15753: "지휘", 15754: "계산",
    15755: "불굴", 15758: "무쌍", 15759: "용사", 15760: "결사", 15761: "수변",
    15762: "천시", 16403: "다자이노곤노소치", 17432: "기쓰레가와슈",
    28856: "도호쿠 통일", 28857: "간토 통일", 28858: "호쿠리쿠 통일",
    28859: "고신 통일", 28860: "도카이 통일", 28861: "긴키 통일",
    28862: "주고쿠 통일", 28863: "시코쿠 통일", 28864: "규슈 통일",
    29106: "도호쿠 지방의 모든 성 제압", 29107: "간토 지방의 모든 성 제압",
    29108: "호쿠리쿠 지방의 모든 성 제압", 29109: "고신 지방의 모든 성 제압",
    29110: "도카이 지방의 모든 성 제압", 29111: "긴키 지방의 모든 성 제압",
    29112: "주고쿠 지방의 모든 성 제압", 29113: "시코쿠 지방의 모든 성 제압",
    29114: "규슈 지방의 모든 성 제압", 29179: "금전 +%d", 29180: "정책 비용 -%d％",
    29181: "감장 +%d", 29182: "%s 등급까지의 가보 구매 가능",
    29183: "대농촌의 석고 +%d", 29184: "대시장의 상업 +%d",
    29185: "교역항의 상업 +%d", 29186: "금산 마을의 상업 +%d",
    29187: "은산 마을의 상업 +%d", 29188: "마목장의 기마 LV +%d",
    29189: "대장간 마을의 철포 LV +%d", 29190: "절의 상업 +%d",
    29191: "남만사의 상업 +%d", 29192: "온천향의 병력 회복 속도 +%d％",
    29193: "도호쿠 지방 성의 상업 +%d％", 29194: "간토 지방 성의 상업 +%d％",
    29195: "호쿠리쿠 지방 성의 상업 +%d％", 29196: "고신 지방 성의 상업 +%d％",
    29197: "도카이 지방 성의 상업 +%d％", 29198: "긴키 지방 성의 상업 +%d％",
    29199: "주고쿠 지방 성의 상업 +%d％", 29200: "시코쿠 지방 성의 상업 +%d％",
    29201: "규슈 지방 성의 상업 +%d％", 29203: "설비 및 요충지 피해 증가",
    29204: "조략 성공률 상승", 29205: "성하 시설 건설 속도 상승",
    29206: "“%s” 정책 발령 가능", 29207: "“%s” 정책 발령 가능",
    29208: "다이묘 군단의 최대 노동력 +%d",
}
TRANSLATIONS.update({entry_id: "개발 완료" for entry_id in range(28760, 28769)})
TRANSLATIONS.update({entry_id: "명소" for entry_id in range(28789, 28794)})
TRANSLATIONS.update({entry_id: "제압 공적" for entry_id in range(28844, 28847)})
TRANSLATIONS.update({entry_id: "전투 공적" for entry_id in range(28847, 28850)})
TRANSLATIONS.update({entry_id: "조략 공적" for entry_id in range(28850, 28853)})
TRANSLATIONS.update({entry_id: "내정 공적" for entry_id in range(28853, 28856)})

for start, end, replacement in (
    (28929, 28939, "자세력의 거점 %d개"),
    (28939, 28949, "자세력의 무장 %d명"),
    (28949, 28959, "자세력의 위신 %d"),
    (28959, 28969, "발령 중인 정책 LV 합계 %d"),
    (28969, 28979, "자세력의 숙로 %d명"),
    (28979, 28989, "자세력의 총 석고 %d"),
    (28989, 28999, "자세력의 총 상업 %d"),
    (28999, 29009, "건설 완료된 성하 시설 %d개"),
    (29009, 29019, "개발률 100％인 성 %d개 보유"),
    (29019, 29029, "자세력의 병력 상한 %d"),
    (29029, 29039, "자세력이 보유한 가보 %d개"),
    (29039, 29044, "자세력의 명소 %d개"),
    (29044, 29049, "자세력의 대농촌 %d개"),
    (29049, 29054, "자세력의 대시장 %d개"),
    (29054, 29059, "자세력의 교역항 %d개"),
    (29059, 29064, "자세력의 금산 마을 %d개"),
    (29064, 29069, "자세력의 은산 마을 %d개"),
    (29069, 29074, "자세력의 마목장 %d개"),
    (29074, 29079, "자세력의 대장간 마을 %d개"),
    (29079, 29084, "자세력의 절 %d개"),
    (29084, 29089, "자세력의 남만사 %d개"),
    (29089, 29094, "자세력의 온천향 %d개"),
    (29094, 29097, "LV4 제압 공적 별호를 지닌 무장 %d명"),
    (29097, 29100, "LV4 전투 공적 별호를 지닌 무장 %d명"),
    (29100, 29103, "LV4 조략 공적 별호를 지닌 무장 %d명"),
    (29103, 29106, "LV4 내정 공적 별호를 지닌 무장 %d명"),
):
    TRANSLATIONS.update({entry_id: replacement for entry_id in range(start, end)})

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "71A3A52AB486759F672D6FFFF4EB5E5BD9463C1BCB5C84C20BDABB20CFDEA130",
    "SC": "EBBD40D439EAF692A133135BBE8466278214235A400DE3CF010BE99F2B0F0E66",
    "EN": "839DC3DD99A8F7D6515271F0839293AC7D086D04E6B01D2A9916B067FEEE3FA8",
    "TC": "3FF2096EA071C91A24F81D7F9A49C99514CA230B1FEE00564A21204FBBEE45E3",
}

BATCH05_OVERLAY_LOGICAL_PATH = base.SELF_OVERLAY_LOGICAL_PATH
OWNER_OVERLAYS = base.OWNER_OVERLAYS + (
    (
        BATCH05_OVERLAY_LOGICAL_PATH,
        "FF19DBE0D56CDB7C8ED1DE70F0BA0820C29F4D62FF1939BF77970983EB9564E5",
        300,
        base.SELECTED_IDS_SHA256,
    ),
)
EXPECTED_OWNER_AUTHORED_COUNT = 22_002
EXPECTED_OWNER_UNION_COUNT = 21_930
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "C88BA7EDDAC7D4B132AAA90D294D24F54A25EBF335578D72714AE72EB022E16A"
SOURCE_SC_HASHES: dict[int, str] = {}
ORIGINAL_INITIALIZE_AND_VALIDATE_CONTEXT = base.ORIGINAL_INITIALIZE_AND_VALIDATE_CONTEXT


def classify_structural_prefix(
    tables: dict[str, Any], target_ids: set[int], owner_ids: set[int]
) -> dict[str, tuple[int, ...]]:
    groups: dict[str, list[int]] = {reason: [] for reason in STRUCTURAL_EXCLUSION_PINS}
    unexpected_semantic: list[int] = []
    for entry_id in sorted(target_ids - owner_ids - set(SELECTED_IDS)):
        sc = tables["SC"].texts[entry_id]
        if sc.strip().lower() == "dummy":
            groups["placeholder_dummy_not_a_translatable_display_message"].append(entry_id)
        elif engine.ASCII_LOOKUP_RE.fullmatch(sc.strip()) and re.search(r"[A-Za-z]", sc):
            groups["romanized_or_phonetic_lookup_key"].append(entry_id)
        elif not engine.has_semantic_alphanumeric(sc):
            groups["format_or_control_only_token"].append(entry_id)
        else:
            unexpected_semantic.append(entry_id)
    if unexpected_semantic:
        raise BatchError(f"unselected semantic targets remain: {unexpected_semantic[:20]}")
    frozen = {reason: tuple(ids) for reason, ids in groups.items()}
    for reason, pin in STRUCTURAL_EXCLUSION_PINS.items():
        ids = frozen[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise BatchError(f"structural exclusion group changed: {reason}")
    all_excluded = tuple(sorted(entry_id for ids in frozen.values() for entry_id in ids))
    if len(all_excluded) != EXCLUDED_COUNT or hash_json(list(all_excluded)) != EXCLUDED_IDS_SHA256:
        raise BatchError("combined structural exclusion scope changed")
    return frozen


def validate_selection(
    target_ids: set[int], owner_ids: set[int], structural: dict[str, tuple[int, ...]]
) -> dict[str, Any]:
    if (
        len(SELECTED_IDS) != 278
        or tuple(sorted(set(SELECTED_IDS))) != SELECTED_IDS
        or hash_json(list(SELECTED_IDS)) != SELECTED_IDS_SHA256
    ):
        raise BatchError("selected ID scope changed")
    if set(SELECTED_IDS) - target_ids or set(SELECTED_IDS) & owner_ids:
        raise BatchError("selection is not exact-target-only and owner-disjoint")
    excluded = {entry_id for ids in structural.values() for entry_id in ids}
    remaining = target_ids - owner_ids
    if remaining != set(SELECTED_IDS) | excluded:
        raise BatchError("final selection and structural exclusions do not exhaust remaining targets")
    return {
        "first_id": SELECTED_IDS[0],
        "last_id": SELECTED_IDS[-1],
        "remaining_target_count_before_batch": len(remaining),
        "selected_count": len(SELECTED_IDS),
        "structural_exclusion_count": len(excluded),
        "remaining_semantic_count_after_batch": 0,
        "final_semantic_completion_after_batch05": True,
    }


def initialize_and_validate_context(
    tables: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_source: dict[str, set[str]] = {}
    for entry_id in SELECTED_IDS:
        by_source.setdefault(tables["SC"].texts[entry_id], set()).add(TRANSLATIONS[entry_id])
    if any(len(replacements) != 1 for replacements in by_source.values()):
        raise BatchError("repeated SC source groups have inconsistent Korean replacements")
    return ORIGINAL_INITIALIZE_AND_VALIDATE_CONTEXT(tables)


def validate_progress_catalog(
    progress_path: Path,
    owner_ids: set[int],
    target_ids: set[int],
    registration_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    progress, _ = common.load_json_strict(progress_path)
    matches = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(matches) != 1 or not isinstance(matches[0].get("overlay_globs"), list):
        raise BatchError("progress must contain one PK msgdata resource")
    expected_owner_paths = {row[0] for row in OWNER_OVERLAYS}
    prior_paths: list[str] = []
    successor_ids: list[int] = []
    successor_paths: list[str] = []
    self_count = 0
    for logical_path in matches[0]["overlay_globs"]:
        if not isinstance(logical_path, str):
            raise BatchError("progress contains a non-string overlay path")
        path = engine.resolve_registration_path(registration_root, logical_path)
        if logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
            continue
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if not path.is_file() or path.read_bytes() != encode_json(engine.make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
            continue
        if not path.is_file():
            raise BatchError(f"successor overlay is missing: {logical_path}")
        successor, _ = common.load_json_strict(path)
        resource, stock, entries = common.validate_overlay_shape(successor)
        if resource != RESOURCE or stock != engine.make_overlay()["stock_sc"]:
            raise BatchError("successor targets another resource or stock pin")
        successor_paths.append(logical_path)
        successor_ids.extend(entry["id"] for entry in entries)
    if self_count > 1 or set(prior_paths) != expected_owner_paths or len(prior_paths) != len(expected_owner_paths):
        raise BatchError("progress prior-owner set or self registration changed")
    if len(successor_paths) != len(set(successor_paths)) or len(successor_ids) != len(set(successor_ids)):
        raise BatchError("successor paths or IDs overlap")
    if set(successor_ids) - target_ids or set(successor_ids) & (owner_ids | set(SELECTED_IDS)):
        raise BatchError("successor contains a non-target or overlapping ID")
    return {
        "batch05_registered": BATCH05_OVERLAY_LOGICAL_PATH in prior_paths,
        "self_registered": self_count == 1,
        "successor_registration_count": len(successor_paths),
        "successor_entry_count": len(successor_ids),
    }


def patch_engine() -> None:
    values = {
        "SCRIPT_PATH": SCRIPT_PATH,
        "WORKSTREAM_ROOT": WORKSTREAM_ROOT,
        "REPO_ROOT": REPO_ROOT,
        "GAME_ROOT": GAME_ROOT,
        "BATCH_ID": BATCH_ID,
        "OVERLAY_NAME": OVERLAY_NAME,
        "EVIDENCE_NAME": EVIDENCE_NAME,
        "REVIEW_NAME": REVIEW_NAME,
        "VALIDATION_NAME": VALIDATION_NAME,
        "SELF_OVERLAY_LOGICAL_PATH": SELF_OVERLAY_LOGICAL_PATH,
        "SELECTED_IDS": SELECTED_IDS,
        "SELECTED_IDS_SHA256": SELECTED_IDS_SHA256,
        "STRUCTURAL_EXCLUSION_PINS": STRUCTURAL_EXCLUSION_PINS,
        "EXCLUDED_COUNT": EXCLUDED_COUNT,
        "EXCLUDED_IDS_SHA256": EXCLUDED_IDS_SHA256,
        "TRANSLATIONS": TRANSLATIONS,
        "OFFICIAL_SELECTED_ROWSET_SHA256": OFFICIAL_SELECTED_ROWSET_SHA256,
        "OWNER_OVERLAYS": OWNER_OVERLAYS,
        "EXPECTED_OWNER_AUTHORED_COUNT": EXPECTED_OWNER_AUTHORED_COUNT,
        "EXPECTED_OWNER_UNION_COUNT": EXPECTED_OWNER_UNION_COUNT,
        "EXPECTED_OWNER_DUPLICATE_COUNT": EXPECTED_OWNER_DUPLICATE_COUNT,
        "EXPECTED_OWNER_IDS_SHA256": EXPECTED_OWNER_IDS_SHA256,
        "SOURCE_SC_HASHES": SOURCE_SC_HASHES,
        "classify_structural_prefix": classify_structural_prefix,
        "validate_selection": validate_selection,
        "initialize_and_validate_context": initialize_and_validate_context,
        "validate_progress_catalog": validate_progress_catalog,
    }
    for name, value in values.items():
        setattr(engine, name, value)


patch_engine()

load_pinned_table = engine.load_pinned_table
load_owner_catalog = engine.load_owner_catalog
load_target_catalog = engine.load_target_catalog
validate_overlay = engine.validate_overlay
script_counts = engine.script_counts
build = engine.build


def main() -> int:
    patch_engine()
    return engine.main()


if __name__ == "__main__":
    raise SystemExit(main())
