#!/usr/bin/env python3
"""Build the two PK msgdata translations excluded from automatic Switch recovery.

The builder validates pinned PK JP/SC/EN/TC resources and their two source rows,
but publishes only hashes, formatting contracts, and project-authored Korean.
It never writes a complete game resource; target reconstruction is in memory.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
TOOLS_ROOT = REPO_ROOT / "tools"
UPSTREAM_ROOT = REPO_ROOT / "workstreams" / "switch_msgdata_v11"
sys.path[:0] = [str(TOOLS_ROOT), str(UPSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgdata_v11 as upstream  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "pk_msgdata_native_completion_2.v1"
RESOURCE = "MSG_PK/SC/msgdata.bin"
STRING_COUNT = 29_210
OVERLAY_NAME = "msgdata_ko_pk_native_completion_2.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_completion_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_completion_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = (
    f"workstreams/msgdata_pk_native_completion/public/{OVERLAY_NAME}"
)
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")
STOCK_SC_RELATIVE = Path(
    "KR_PATCH_BACKUP/file_only_transaction/pk-full-messages-seoulhangang-v1/"
    "originals/MSG_PK/SC/msgdata.bin"
)

OFFICIAL_PINS = {
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "size": 273_734,
        "sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431_044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
    },
    "SC": {
        "logical_path": RESOURCE,
        "size": 516_796,
        "sha256": "DFFC1FA9E8D175085568C14A407B9CB4BE81CF1416DA4485A64CA330D908ADA5",
        "raw_size": 514_752,
        "raw_sha256": "5982D520BF2E66260943DE61D0CB7F1135D1BA81A211E917E3F426C58D9125D6",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "size": 267_550,
        "sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744_236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
    },
    "TC": {
        "logical_path": "MSG_PK/TC/msgdata.bin",
        "size": 270_032,
        "sha256": "A3743D318383C5D6E4D16F20B5228337DB0AE9124D144E4FBF3D4AC660FFFC5E",
        "raw_size": 442_224,
        "raw_sha256": "4D0CEB95818CC9C17623299B2B104482FED03ACCD27116604F8E29BB4C9D7684",
    },
}

ROW_HASHES = {
    22_594: {
        "JP": "4F6DD1462604D53B087212AE25101241F4153BE7A0DCCA0A358E721BC5A627D3",
        "SC": "BFC6FA69C497111C0E94254D5E9937D3F1947B72AB69F15328900EA2FEB2AC4E",
        "EN": "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
        "TC": "B8C6E88B55D4FB88F85721279BE5725F9E6C22B2346992E2D3AA868BBC0558B4",
    },
    25_546: {
        "JP": "2B976EF32A04A29EC1C8ADC45B2507C5D4E5CB1EC71C0275B461FCE152027B74",
        "SC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
        "EN": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
        "TC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
    },
}

TRANSLATIONS = {
    22_594: "성하 시설 \x1bC3%s\x1bCZ의 상업%+d",
    25_546: "부대 능력 증가",
}
EXPECTED_IDS = (22_594, 25_546)
EXPECTED_IDS_SHA256 = "3AF6019509AC61D8A40353E3537EA33EE1D46EA6650732FDE4DBBDD76288C63E"

OWNER_OVERLAYS = (
    ("data/public/msgdata_ko_officer_names_0000_2399.v0.1.json", "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3", 3_831, "ADBE4F9A948FD4440D5D997D0D8ADD2088696F1A30147932D9A9948754AD7D6E"),
    ("workstreams/castle_names/public/castle_names_ko_9151_9542.v0.2.json", "0CEFDE11008F4503198903E1FA25ACDDB120F6B407405EF9ACE2B01B39577E5E", 392, "474F7B7EA14CA96FF70EBCD63D1FF2CBC0E3CE5BC89ECDD4B9EB8D25E67CE850"),
    ("workstreams/province_names/public/province_names_ko_13975_14046.v0.2.json", "2EF65EBDEF21521857477EA180E7FBC7AB92F1626FC69D06BD6262E97BFDBDF5", 72, "92FC19CAC52F04FD5D0DEC3F98F0C929B232DDD41F1D9C2F94059260E9C57A8A"),
    ("workstreams/msgdata/public/msgdata_ko_faction_labels_3032_3221.v0.1.json", "A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244", 190, "BFE9A2B0651D15EB08DA4DD5E1B0C31FDC6BB7E670B1ACF8ED551F7F6C5A44FD"),
    ("workstreams/msgdata/public/msgdata_ko_name_components_3222_3315.v0.1.json", "9B887DE854B6ADE847036F1D757925AFFA9BD84FD041ADAB0CE23DA0D3DAC09A", 94, "17FE6A25C8D2A4EBE5FE311C3154576D4811F983014F43CF7FB2034557524F54"),
    ("workstreams/switch_msgdata_v11/public/msgdata_ko_switch_v11_strict_transfer.v0.1.json", "1C748373DFF712E52BA11459E032E3611ED5151EF18633E592452D3A2A78392E", 16_176, "B8AC5996A1D9A6231E8A22AC130C077E0F11830F181FF66FA5FB6929C6FB34BB"),
    ("workstreams/switch_msgdata_v13_invariant_recovery/public/msgdata_ko_switch_v13_invariant_recovery_145.v1.json", "0372E73879BD2E3C927F69375079AA6EE507E2FF2824E9AE8E8525E109CCC982", 145, "8BBA6F1E8AC5867BFB0361D4A58D3DAF023BAB559CFEE5044520810A39E79BD0"),
)
EXPECTED_OWNER_AUTHORED_COUNT = 20_900
EXPECTED_OWNER_UNION_COUNT = 20_828
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "FED59D449BEF313A34EAD498DA7DD240DC17BD4A528306A40BC7136DB84663B9"

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
CUSTOM_BRACKET_RE = re.compile(r"\[[A-Za-z0-9_]+\]")


class NativeCompletionError(ValueError):
    """Raised when an official input or the two-row contract changes."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def script_counts(text: str) -> dict[str, int]:
    return {"cjk_unified_count": len(CJK_RE.findall(text)), "kana_count": len(KANA_RE.findall(text))}


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def load_pinned_table(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["sha256"]:
        raise NativeCompletionError(f"{label} packed resource differs from its pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise NativeCompletionError(f"{label} raw resource differs from its pin")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT or rebuild_message_table(table, table.texts) != raw:
        raise NativeCompletionError(f"{label} table layout or round trip changed")
    return packed, raw, table


def make_entries() -> list[dict[str, Any]]:
    return [
        {"id": entry_id, "source_sc_utf16le_sha256": ROW_HASHES[entry_id]["SC"], "ko": TRANSLATIONS[entry_id]}
        for entry_id in EXPECTED_IDS
    ]


def make_overlay() -> dict[str, Any]:
    pin = OFFICIAL_PINS["SC"]
    return {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(EXPECTED_IDS),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {
            "size": pin["size"], "packed_sha256": pin["sha256"],
            "raw_size": pin["raw_size"], "raw_sha256": pin["raw_sha256"],
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": make_entries(),
    }


def load_owner_catalog() -> dict[str, Any]:
    union: set[int] = set()
    authored = 0
    rows: list[dict[str, Any]] = []
    for logical_path, expected_hash, expected_count, expected_ids_hash in OWNER_OVERLAYS:
        path = REPO_ROOT / logical_path
        overlay, blob = common.load_json_strict(path)
        ids = [entry.get("id") for entry in overlay.get("entries", [])]
        if sha256(blob) != expected_hash or len(ids) != expected_count:
            raise NativeCompletionError(f"owner overlay changed: {logical_path}")
        if any(type(entry_id) is not int for entry_id in ids) or len(ids) != len(set(ids)):
            raise NativeCompletionError(f"owner overlay IDs invalid: {logical_path}")
        if hash_json(sorted(ids)) != expected_ids_hash:
            raise NativeCompletionError(f"owner overlay ID set changed: {logical_path}")
        resource = overlay.get("resource") or (overlay.get("target") or {}).get("resource")
        if resource != RESOURCE:
            raise NativeCompletionError(f"owner overlay targets another resource: {logical_path}")
        union.update(ids)
        authored += len(ids)
        rows.append({"path": logical_path, "sha256": expected_hash, "entry_count": len(ids), "ids_sha256": expected_ids_hash})
    if (authored, len(union), authored - len(union), hash_json(sorted(union))) != (
        EXPECTED_OWNER_AUTHORED_COUNT, EXPECTED_OWNER_UNION_COUNT,
        EXPECTED_OWNER_DUPLICATE_COUNT, EXPECTED_OWNER_IDS_SHA256,
    ):
        raise NativeCompletionError("owner overlay union changed")
    if set(EXPECTED_IDS) & union:
        raise NativeCompletionError("native completion IDs overlap an owner overlay")
    return {
        "ids": union,
        "snapshot": {
            "overlays": rows, "authored_entry_count": authored,
            "effective_unique_id_count": len(union),
            "cross_overlay_duplicate_id_count": authored - len(union),
            "effective_ids_sha256": hash_json(sorted(union)),
        },
    }


def validate_progress_catalog(progress_path: Path, owner_ids: set[int]) -> dict[str, Any]:
    progress, _ = common.load_json_strict(progress_path)
    matches = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(matches) != 1 or not isinstance(matches[0].get("overlay_globs"), list):
        raise NativeCompletionError("progress must contain one PK msgdata resource")
    expected_owner_paths = {row[0] for row in OWNER_OVERLAYS}
    prior_paths: list[str] = []
    successor_ids: list[int] = []
    self_count = 0
    for pattern in matches[0]["overlay_globs"]:
        if not isinstance(pattern, str):
            raise NativeCompletionError("progress contains a non-string overlay path")
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise NativeCompletionError(f"progress overlay {pattern!r} resolved to {len(paths)} files")
        logical_path = paths[0].relative_to(REPO_ROOT).as_posix()
        if logical_path != pattern:
            raise NativeCompletionError("progress paths must be exact repo-relative paths")
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if paths[0].read_bytes() != encode_json(make_overlay()):
                raise NativeCompletionError("self registration is not the exact deterministic overlay")
            self_count += 1
        elif logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
        else:
            overlay, _ = common.load_json_strict(paths[0])
            resource, _stock, entries = common.validate_overlay_shape(overlay)
            if resource != RESOURCE:
                raise NativeCompletionError("successor overlay targets another resource")
            successor_ids.extend(int(entry["id"]) for entry in entries)
    if self_count > 1 or set(prior_paths) != expected_owner_paths or len(prior_paths) != len(expected_owner_paths):
        raise NativeCompletionError("progress prior-owner set or self-registration count changed")
    if len(successor_ids) != len(set(successor_ids)):
        raise NativeCompletionError("successor overlays overlap each other")
    if set(successor_ids) & (owner_ids | set(EXPECTED_IDS)):
        raise NativeCompletionError("successor overlays overlap this completion or its pinned owners")
    if set(EXPECTED_IDS) & owner_ids:
        raise NativeCompletionError("native completion IDs are already claimed")
    return {"self_registered": self_count == 1, "self_registration_count": self_count, "self_excluded_from_prior_claims": True}


def validate_context(tables: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []
    for entry_id in EXPECTED_IDS:
        texts = {language: table.texts[entry_id] for language, table in tables.items()}
        hashes = {language: common.text_hash(text) for language, text in texts.items()}
        if hashes != ROW_HASHES[entry_id]:
            raise NativeCompletionError(f"official multilingual row hash changed at id {entry_id}")
        sc = texts["SC"]
        ko = TRANSLATIONS[entry_id]
        if not common.has_semantic_text(sc) or common.invariant_mismatches(sc, ko):
            raise NativeCompletionError(f"SC target visibility or invariant contract failed at id {entry_id}")
        if CUSTOM_BRACKET_RE.findall(sc) != CUSTOM_BRACKET_RE.findall(ko):
            raise NativeCompletionError(f"custom bracket tokens changed at id {entry_id}")
        if script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0} or not HANGUL_RE.search(ko):
            raise NativeCompletionError(f"Korean replacement is not source-script-free at id {entry_id}")
        contracts = {language: common.message_invariants(text) for language, text in texts.items()}
        if entry_id == 22_594:
            if contracts["SC"] != contracts["TC"] or contracts["JP"] == contracts["SC"]:
                raise NativeCompletionError("id 22594 multilingual contract conflict changed")
            decision = {
                "semantic_basis_languages": ["SC", "TC"],
                "contract_basis_language": "SC",
                "conflicting_semantic_candidate_rejected": True,
                "sc_esc_printf_contract_preserved": True,
            }
            risk = "SC/TC 의미를 채택하고 상충하는 JP/Switch 의미를 폐기; 런타임 화면 검수 필요"
        else:
            if len({hashes[language] for language in ("SC", "EN", "TC")}) != 1:
                raise NativeCompletionError("id 25546 SC/EN/TC placeholder consensus changed")
            if contracts["JP"]["printf"] != ["%d"] or contracts["SC"]["printf"]:
                raise NativeCompletionError("id 25546 uncertain printf contract changed")
            if common.printf_tokens(ko) != ([], 0):
                raise NativeCompletionError("id 25546 must not introduce an unproved printf token")
            decision = {
                "semantic_basis_languages": ["JP"],
                "contract_basis_languages": ["SC", "EN", "TC"],
                "unproved_printf_token_intentionally_omitted": True,
                "dynamic_value_precision_degraded_for_safety": True,
            }
            risk = "공식 SC/EN/TC에 인자 계약이 없어 수치 표시는 의도적으로 생략; 런타임 화면 검수 필요"
        evidence.append({
            "id": entry_id,
            "official_utf16le_sha256": hashes,
            "official_format_contracts": contracts,
            "ko_utf16le_sha256": common.text_hash(ko),
            "stock_visible_target": True,
            "pk_sc_invariants_preserved": True,
            "custom_bracket_tokens_preserved": True,
            "source_script_free": True,
            **decision,
        })
        review.append({
            "id": entry_id, "status": "translated", "human_review_required": True,
            "runtime_reviewed": False, "stock_visible_target": True,
            "pk_sc_invariants_preserved": True, "review_note": risk,
        })
    return evidence, review


def validate_overlay(overlay: dict[str, Any], stock_table: Any, owner_ids: set[int]) -> None:
    resource, stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE or stock["string_count"] != STRING_COUNT:
        raise NativeCompletionError("overlay targets the wrong resource")
    ids = [entry["id"] for entry in entries]
    if tuple(ids) != EXPECTED_IDS or hash_json(ids) != EXPECTED_IDS_SHA256 or set(ids) & owner_ids:
        raise NativeCompletionError("overlay ID scope or owner disjointness changed")
    for entry in entries:
        source = stock_table.texts[entry["id"]]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise NativeCompletionError(f"stock source hash changed at id {entry['id']}")
        if common.invariant_mismatches(source, entry["ko"]):
            raise NativeCompletionError(f"overlay invariant mismatch at id {entry['id']}")


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    paths = {"pk_jp": args.stock_pk_jp, "pk_sc": args.stock_pk_sc, "pk_en": args.stock_pk_en, "pk_tc": args.stock_pk_tc}
    paths.update({f"owner_{index}": REPO_ROOT / row[0] for index, row in enumerate(OWNER_OVERLAYS)})
    return {label: sha256(path.read_bytes()) for label, path in paths.items()}


def build(args: argparse.Namespace) -> dict[str, Any]:
    owners = load_owner_catalog()
    validate_progress_catalog(args.progress, owners["ids"])
    before = input_snapshot(args)
    packed_sc, _, sc_table = load_pinned_table(args.stock_pk_sc, OFFICIAL_PINS["SC"], "PK SC msgdata")
    tables = {"SC": sc_table}
    for language, path in (("JP", args.stock_pk_jp), ("EN", args.stock_pk_en), ("TC", args.stock_pk_tc)):
        _, _, tables[language] = load_pinned_table(path, OFFICIAL_PINS[language], f"PK {language} msgdata")
    evidence_entries, review_entries = validate_context(tables)
    overlay = make_overlay()
    validate_overlay(overlay, sc_table, owners["ids"])
    target_a = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    target_b = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    if target_a != target_b:
        raise NativeCompletionError("in-memory target reconstruction is not deterministic")

    evidence = {
        "schema": "nobu16.kr.msgdata-pk-native-completion-evidence.v1",
        "batch_id": BATCH_ID, "resource": RESOURCE,
        "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "method": "manual_pk_jp_sc_en_tc_context_resolution_after_switch_v13_safe_exclusion",
        "selected_entry_count": len(EXPECTED_IDS), "selected_ids_sha256": EXPECTED_IDS_SHA256,
        "owner_catalog": owners["snapshot"], "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-native-completion-review.v1",
        "batch_id": BATCH_ID, "resource": RESOURCE,
        "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "summary": {"translated_count": 2, "human_review_required_count": 2, "runtime_reviewed_count": 0},
        "entries": review_entries,
    }
    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}")
    artifacts["alignment_evidence"] = write_json(out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}")
    artifacts["review_index"] = write_json(out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}")
    for name, artifact in artifacts.items():
        if sum(script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")).values()):
            raise NativeCompletionError(f"{name} contains CJK unified or kana")
    after = input_snapshot(args)
    if before != after:
        raise NativeCompletionError("read-only input changed during generation")
    validation = {
        "schema": "nobu16.kr.msgdata-pk-native-completion-validation.v1",
        "batch_id": BATCH_ID, "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {"resource": RESOURCE, "selected_entry_count": 2, "selected_ids": list(EXPECTED_IDS), "selected_ids_sha256": EXPECTED_IDS_SHA256, "stock_visible_target_count": 2, "owner_overlap_count": 0},
        "official_resource_pins": OFFICIAL_PINS,
        "owner_catalog": owners["snapshot"],
        "progress_integration_policy": {"pre_integration_unregistered_allowed": True, "post_integration_exact_self_registration_allowed": True, "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH, "self_overlay_excluded_from_prior_claims": True},
        "target_reconstruction": target_a,
        "reproducibility": {"in_memory_target_a_b_equal": True, "isolated_artifact_a_b_required": True},
        "input_snapshot_before": before, "input_snapshot_after": after,
        "source_free_scan": {name: script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")) for name, artifact in artifacts.items()},
        "safety": {"commercial_source_text_included": False, "complete_game_resource_included": False, "global_progress_modified": False, "global_readme_modified": False, "font_modified": False, "installed_game_files_modified": False, "deployment_performed": False, "commit_or_push_performed": False},
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = script_counts(encode_json(validation).decode("utf-8"))
    if any(sum(counts.values()) for counts in validation["source_free_scan"].values()):
        raise NativeCompletionError("validation source-free scan failed")
    artifacts["generation_validation"] = write_json(out_root / VALIDATION_NAME, validation, VALIDATION_NAME)
    return {"out_root": out_root, "entry_count": 2, "artifacts": artifacts, "target_reconstruction": target_a}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK/JP/msgdata.bin")
    parser.add_argument("--stock-pk-sc", type=Path, default=GAME_ROOT / STOCK_SC_RELATIVE)
    parser.add_argument("--stock-pk-en", type=Path, default=GAME_ROOT / "MSG_PK/EN/msgdata.bin")
    parser.add_argument("--stock-pk-tc", type=Path, default=GAME_ROOT / "MSG_PK/TC/msgdata.bin")
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
