#!/usr/bin/env python3
"""Build source-free Korean msgdata faction-label batch1 (3032-3221)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
PATCH_ROOT = WORKSPACE_ROOT / "KR_PATCH_WORK"
TOOLS_DIR = PATCH_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgdata_faction_labels_3032_3221.v0.1"
OVERLAY_NAME = "msgdata_ko_faction_labels_3032_3221.v0.1.json"
EVIDENCE_NAME = "alignment_evidence.v0.1.json"
REVIEW_NAME = "review_index.v0.1.json"
VALIDATION_NAME = "validation.v0.1.json"
STRING_COUNT = 29_210
SCOPE_START = 3032
SCOPE_END = 3221
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()

RESOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgdata.bin",
        "wrapper_size": 267_385,
        "wrapper_sha256": "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
        "raw_size": 499_760,
        "raw_sha256": "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "wrapper_size": 273_734,
        "wrapper_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431_044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "wrapper_size": 267_550,
        "wrapper_sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744_236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
    },
}

EXISTING_OVERLAY_PATHS = (
    "KR_PATCH_WORK/data/public/msgdata_ko_officer_names_0000_2399.v0.1.json",
    "KR_PATCH_WORK/workstreams/castle_names/public/castle_names_ko_9151_9542.v0.2.json",
    "KR_PATCH_WORK/workstreams/province_names/public/province_names_ko_13975_14046.v0.2.json",
)

GROUPS = (
    {
        "group_id": "regional_and_maritime_factions",
        "title_ko": "국인·수군·역할 라벨",
        "start_id": 3032,
        "end_id": 3221,
        "selected_count": 190,
    },
)

TRANSLATIONS: dict[int, str] = {
    3032: "시모구니중",
    3033: "아카이시중",
    3034: "도와다중",
    3035: "시치노헤중",
    3036: "오마중",
    3037: "구지중",
    3038: "히에누키중",
    3039: "와가중",
    3040: "가시야마중",
    3041: "이시노마키중",
    3042: "구마가네중",
    3043: "후쿠시마중",
    3044: "도이중",
    3045: "가타히라중",
    3046: "시로이시중",
    3047: "와타리중",
    3048: "나라하중",
    3049: "시오마쓰중",
    3050: "가시마중",
    3051: "가바야마중",
    3052: "돗코중",
    3053: "도시마중",
    3054: "유리중",
    3055: "사케노베중",
    3056: "이와미중",
    3057: "유노오중",
    3058: "야치중",
    3059: "아라토중",
    3060: "오구니중",
    3061: "도조중",
    3062: "마카베중",
    3063: "미토중",
    3064: "고가네중",
    3065: "시와쿠 수군",
    3066: "우시키중",
    3067: "아와노중",
    3068: "이오노중",
    3069: "아카하타중",
    3070: "오야마중",
    3071: "사루가쿄중",
    3072: "우스이중",
    3073: "요코세중",
    3074: "지치부중",
    3075: "에도중",
    3076: "가쓰누마중",
    3077: "하나와중",
    3078: "마쓰다중",
    3079: "시오노중",
    3080: "우라가중",
    3081: "후마당",
    3082: "가와우치중",
    3083: "군나이중",
    3084: "사쿠중",
    3085: "나가누마중",
    3086: "미쓰쿠리중",
    3087: "오미중",
    3088: "하타야마중",
    3089: "네즈중",
    3090: "마쓰오카중",
    3091: "아게키타중",
    3092: "미나미아게키타중",
    3093: "야스다중",
    3094: "도카마치중",
    3095: "다카데라중",
    3096: "노키자루중",
    3097: "시오바라중",
    3098: "네이중",
    3099: "우오즈중",
    3100: "유사중",
    3101: "마쓰야마중",
    3102: "시라미네중",
    3103: "도리고에중",
    3104: "호리에중",
    3105: "모리데라중",
    3106: "미카타중",
    3107: "이시베중",
    3108: "오가와중",
    3109: "가쓰라야마중",
    3110: "후지노미야중",
    3111: "야나토리중",
    3112: "미쓰케중",
    3113: "쓰쿠데중",
    3114: "다미네중",
    3115: "다이조중",
    3116: "가리야중",
    3117: "가와나미중",
    3118: "이와쿠라중",
    3119: "나루미중",
    3120: "도코나메중",
    3121: "가시모중",
    3122: "쓰마기중",
    3123: "기타가타중",
    3124: "후와중",
    3125: "다카하라중",
    3126: "나카지마중",
    3127: "고즈쿠리중",
    3128: "간베중",
    3129: "도바 수군",
    3130: "이누카미중",
    3131: "고카중",
    3132: "간자키중",
    3133: "오미조중",
    3134: "아사즈마중",
    3135: "마키시마중",
    3136: "호쿠레이중",
    3137: "고카중",
    3138: "후쿠치야마중",
    3139: "슈치중",
    3140: "가타노중",
    3141: "도키중",
    3142: "마리야쓰중",
    3143: "요노중",
    3144: "이가중",
    3145: "오치중",
    3146: "도이치중",
    3147: "네고로중",
    3148: "나루세중",
    3149: "니시와키중",
    3150: "다쓰노중",
    3151: "오나바라중",
    3152: "고토중",
    3153: "고쿠라중",
    3154: "오사후네중",
    3155: "니이미중",
    3156: "기비중",
    3157: "와치중",
    3158: "시토미야마중",
    3159: "마키노오중",
    3160: "무쿠나시중",
    3161: "세노중",
    3162: "하나하라중",
    3163: "도쿠야마중",
    3164: "니호중",
    3165: "헤키중",
    3166: "와지마중",
    3167: "만바중",
    3168: "가시마중",
    3169: "요시오카중",
    3170: "쓰쓰미중",
    3171: "오다카중",
    3172: "아카나중",
    3173: "마쓰에중",
    3174: "오치중",
    3175: "다카쓰중",
    3176: "이누이중",
    3177: "다키미야중",
    3178: "아리마중",
    3179: "이사와중",
    3180: "무라카미 수군",
    3181: "사기노모리중",
    3182: "오즈중",
    3183: "스쿠모중",
    3184: "하타중",
    3185: "게라중",
    3186: "구몬중",
    3187: "조스이중",
    3188: "우베중",
    3189: "마쓰무레중",
    3190: "미나미군중",
    3191: "기즈키중",
    3192: "무나카타중",
    3193: "우사군중",
    3194: "아소중",
    3195: "다카오중",
    3196: "나가이와중",
    3197: "미쓰세중",
    3198: "쓰쿠시중",
    3199: "다카시로중",
    3200: "사세보중",
    3201: "다쿠마중",
    3202: "아카호시중",
    3203: "야쓰시로중",
    3204: "다카치호중",
    3205: "마쓰오중",
    3206: "이노중",
    3207: "쓰루다중",
    3208: "구시키노중",
    3209: "게도인중",
    3210: "다네가시마중",
    3211: "이지치중",
    3212: "네지메중",
    3213: "보급",
    3214: "대장",
    3215: "이데우라중",
    3216: "무로가중",
    3217: "노시마 수군",
    3218: "구루시마 수군",
    3219: "미나카와중",
    3220: "스와중",
    3221: "나에기중",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3042: ["kumagane_place_reading_requires_glossary_review"],
    3052: ["dokko_term_reading_requires_glossary_review"],
    3065: ["shiwaku_navy_name_requires_glossary_review"],
    3098: ["nei_place_reading_requires_glossary_review"],
    3099: ["sc_jp_uozu_vs_en_matsukura_alignment_requires_review"],
    3127: ["kozukuri_place_reading_requires_glossary_review"],
    3131: ["koka_place_reading_requires_glossary_review"],
    3137: ["goka_and_koka_homophone_requires_review"],
    3192: ["munakata_standard_reading_over_en_variant_requires_review"],
    3213: ["supplier_role_label_requires_runtime_context_review"],
    3214: ["leader_role_label_requires_runtime_context_review"],
    3217: ["noshima_navy_name_requires_glossary_review"],
    3218: ["kurushima_navy_name_requires_glossary_review"],
}

CJK_RE = re.compile(r"[\u3400-\u9FFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF]")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    excluded = set(EXCLUDED_INTERNAL_IDS)
    selected = [
        entry_id
        for entry_id in range(SCOPE_START, SCOPE_END + 1)
        if entry_id not in excluded
    ]
    if selected != sorted(TRANSLATIONS):
        raise ValueError("translation ids must exactly cover the selected range")
    return selected


def group_for(entry_id: int) -> str:
    for group in GROUPS:
        if int(group["start_id"]) <= entry_id <= int(group["end_id"]):
            return str(group["group_id"])
    raise ValueError(f"no group for ID {entry_id}")


def source_structure(text: str) -> dict[str, Any]:
    inv = common.message_invariants(text)
    return {
        "esc": inv["esc"],
        "line_breaks": inv["line_breaks"],
        "printf": inv["printf"],
        "unknown_percent_count": inv["unknown_percent_count"],
        "control_count": len(inv["controls"]),
        "pua": inv["pua"],
        "leading_whitespace_utf16le_sha256": common.text_hash(inv["leading_whitespace"]),
        "trailing_whitespace_utf16le_sha256": common.text_hash(inv["trailing_whitespace"]),
    }


def public_script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def load_stock(path: Path, language: str) -> dict[str, Any]:
    pin = RESOURCE_PINS[language]
    wrapper = path.read_bytes()
    if len(wrapper) != pin["wrapper_size"] or sha256(wrapper) != pin["wrapper_sha256"]:
        raise ValueError(f"{language} wrapper does not match the pinned release")
    _, raw = decompress_wrapper(wrapper)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise ValueError(f"{language} raw msgdata does not match the pinned release")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise ValueError(
            f"{language} string count is {table.string_count}, expected {STRING_COUNT}"
        )
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError(f"{language} parse/rebuild is not byte-identical")
    return {"language": language, "wrapper": wrapper, "raw": raw, "table": table}


def installed_resource_snapshot() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for relative in (
        "MSG_PK/SC/msgdata.bin",
        "MSG_PK/JP/msgdata.bin",
        "MSG_PK/EN/msgdata.bin",
    ):
        path = WORKSPACE_ROOT / relative
        blob = path.read_bytes()
        values[relative] = {"size": len(blob), "sha256": sha256(blob)}
    return values


def existing_overlay_snapshot() -> dict[str, Any]:
    union: set[int] = set()
    total_entries = 0
    rows: list[dict[str, Any]] = []
    for relative in EXISTING_OVERLAY_PATHS:
        path = WORKSPACE_ROOT / relative
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object)
        entries = value.get("entries")
        if not isinstance(entries, list):
            raise ValueError(f"existing overlay has no entries list: {relative}")
        ids = [int(entry["id"]) for entry in entries if isinstance(entry, dict) and "id" in entry]
        if len(ids) != len(entries) or len(ids) != len(set(ids)):
            raise ValueError(f"existing overlay has invalid or duplicate IDs: {relative}")
        blob = path.read_bytes()
        rows.append(
            {
                "path": relative,
                "sha256": sha256(blob),
                "entry_count": len(ids),
                "min_id": min(ids),
                "max_id": max(ids),
            }
        )
        total_entries += len(ids)
        union.update(ids)
    overlap = set(selected_ids()) & union
    if overlap:
        raise ValueError(f"selected IDs overlap existing overlays: {sorted(overlap)}")
    return {
        "overlays": rows,
        "effective_unique_id_count": len(union),
        "cross_overlay_duplicate_id_count": total_entries - len(union),
        "selected_overlap_ids": [],
    }


def build_overlay(stock_sc: dict[str, Any], tables: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ids = selected_ids()
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        if not source_sc:
            raise ValueError(f"SC source is empty at selected ID {entry_id}")
        if any(not tables[language].texts[entry_id] for language in ("JP", "EN")):
            raise ValueError(f"cross-language source is empty at selected ID {entry_id}")
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        if problems:
            invariant_failures.append({"id": entry_id, "problems": problems})
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "group_id": group_for(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(tables[language].texts[entry_id]),
                        "structure": source_structure(tables[language].texts[entry_id]),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgdata.bin",
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(stock_sc["wrapper"]),
            "packed_sha256": sha256(stock_sc["wrapper"]),
            "raw_size": len(stock_sc["raw"]),
            "raw_sha256": sha256(stock_sc["raw"]),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)
    return overlay, evidence_entries


def reconstruct_sc_target(stock_sc: dict[str, Any]) -> dict[str, Any]:
    table = stock_sc["table"]
    texts = list(table.texts)
    for entry_id in selected_ids():
        source = texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        if common.invariant_mismatches(source, replacement):
            raise ValueError(f"source invariants changed while rebuilding ID {entry_id}")
        texts[entry_id] = replacement
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ValueError("Korean target parse/rebuild verification failed")
    rebuilt_wrapper = recompress_wrapper(rebuilt_raw, stock_sc["wrapper"])
    _, wrapper_raw = decompress_wrapper(rebuilt_wrapper)
    if wrapper_raw != rebuilt_raw:
        raise ValueError("Korean target wrapper roundtrip verification failed")
    return {
        "wrapper": rebuilt_wrapper,
        "raw": rebuilt_raw,
        "changed_count": sum(
            1 for entry_id in selected_ids() if table.texts[entry_id] != texts[entry_id]
        ),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    before = installed_resource_snapshot()
    loaded = {
        language: load_stock(path.resolve(), language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value["table"] for language, value in loaded.items()}
    existing = existing_overlay_snapshot()
    overlay, evidence_entries = build_overlay(loaded["SC"], tables)

    first_target = reconstruct_sc_target(loaded["SC"])
    second_target = reconstruct_sc_target(loaded["SC"])
    if first_target["wrapper"] != second_target["wrapper"] or first_target["raw"] != second_target["raw"]:
        raise ValueError("independent Korean SC reconstructions are not byte-identical")
    if first_target["changed_count"] != len(selected_ids()):
        raise ValueError("every selected translation must change the SC source")

    boundary_ids = (3031, 3032, 3212, 3213, 3214, 3215, 3221, 3222)
    evidence = {
        "schema": "nobu16.kr.msgdata-faction-label-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgdata",
        "alignment_basis": [
            "same_resource_role",
            "same_29210_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "range_boundaries_crosschecked_in_sc_jp_en",
        ],
        "source_files": {
            language: {
                **RESOURCE_PINS[language],
                "string_count": STRING_COUNT,
            }
            for language in ("SC", "JP", "EN")
        },
        "groups": list(GROUPS),
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msgdata-faction-label-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(selected_ids()),
        "entries": [
            {
                "id": entry_id,
                "group_id": group_for(entry_id),
                "status": "translated",
                "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
                "automated_draft": True,
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
            }
            for entry_id in selected_ids()
        ],
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    overlay_meta = write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}")
    evidence_meta = write_json(out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}")
    review_meta = write_json(out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}")
    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free = {
        name: public_script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(counts != {"cjk_unified_count": 0, "kana_count": 0} for counts in source_free.values()):
        raise ValueError("public artifact contains source-language CJK or kana")

    validation = {
        "schema": "nobu16.kr.msgdata-faction-label-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(selected_ids()),
            "selected_ids_sha256": sha256(
                json.dumps(selected_ids(), separators=(",", ":")).encode("utf-8")
            ),
            "excluded_internal_entry_count": len(EXCLUDED_INTERNAL_IDS),
            "excluded_internal_ids_sha256": sha256(
                json.dumps(list(EXCLUDED_INTERNAL_IDS), separators=(",", ":")).encode("utf-8")
            ),
        },
        "existing_overlay_exclusion": existing,
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(selected_ids()) * 3,
            "manual_semantic_crosschecks": len(selected_ids()),
        },
        "replacement_invariants": {
            "checked": len(selected_ids()),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
            ],
        },
        "reconstruction": {
            "source_parse_rebuild_byte_identical": {
                language: True for language in ("SC", "JP", "EN")
            },
            "sc_overlay_rebuild_a_b_byte_identical": True,
            "changed_entry_count": first_target["changed_count"],
            "target": {
                "wrapper_size": len(first_target["wrapper"]),
                "wrapper_sha256": sha256(first_target["wrapper"]),
                "raw_size": len(first_target["raw"]),
                "raw_sha256": sha256(first_target["raw"]),
                "complete_target_included": False,
            },
        },
        "source_free_scan": source_free,
        "translation_status": {
            "translated_draft": len(selected_ids()),
            "human_review_required": len(selected_ids()),
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
        },
        "safety": {
            "installed_game_files_modified": False,
            "other_workstream_modified": False,
            "global_progress_modified": False,
            "commit_or_push_performed": False,
        },
        "installed_msgdata_before": before,
        "installed_msgdata_after": installed_resource_snapshot(),
        "artifacts": {
            "overlay": overlay_meta,
            "alignment_evidence": evidence_meta,
            "review_index": review_meta,
        },
    }
    if validation["installed_msgdata_before"] != validation["installed_msgdata_after"]:
        raise ValueError("installed msgdata changed while the batch was built")
    validation_meta = write_json(out_root / VALIDATION_NAME, validation, VALIDATION_NAME)
    return {
        "out_root": out_root,
        "entry_count": len(selected_ids()),
        "artifacts": {
            "overlay": overlay_meta,
            "alignment_evidence": evidence_meta,
            "review_index": review_meta,
            "generation_validation": validation_meta,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=PATCH_ROOT / "backups" / "officer_name_probe_v0_1" / "msgdata.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgdata.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgdata.bin"
    )
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
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
