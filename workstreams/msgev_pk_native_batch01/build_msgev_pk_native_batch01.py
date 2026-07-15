#!/usr/bin/env python3
"""Build the first 100-row native PK ``msgev`` review batch.

The batch freezes the first one hundred exact PK/SC target IDs not claimed by
the current progress catalog.  Literal names and narrative rows are translated
from the pinned PK SC/JP/EN/TC alignment.  Dynamic substitution tokens,
internal script keys, speaker identifiers, and non-lexical punctuation-only
rows are documented but deliberately left unclaimed because changing them
would either corrupt runtime lookup or create fake translation progress.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
NATIVE13_ROOT = REPO_ROOT / "workstreams" / "switch_msgev_v13_native_contract_recovery"
sys.path[:0] = [str(NATIVE13_ROOT), str(TOOLS_ROOT)]

import build_switch_msgev_v13_native_contract_recovery as base  # noqa: E402


common = base.common
strict = base.strict
BATCH_ID = "msgev-pk-native-batch01-8.v1"
RESOURCE = "MSG_PK/SC/msgev.bin"

CANDIDATE_IDS = [
    2_581,
    2_953,
    2_954,
    2_955,
    2_959,
    2_960,
    2_964,
    2_965,
    2_967,
    2_972,
    2_973,
    2_974,
    2_975,
    2_976,
    2_977,
    2_978,
    2_979,
    2_980,
    2_981,
    2_982,
    2_983,
    2_984,
    2_985,
    2_986,
    2_987,
    2_988,
    2_989,
    2_990,
    2_991,
    2_992,
    2_993,
    2_994,
    2_995,
    2_996,
    2_997,
    3_000,
    3_001,
    3_002,
    3_003,
    3_004,
    3_005,
    3_006,
    3_105,
    3_106,
    3_107,
    3_108,
    3_109,
    3_116,
    3_309,
    3_310,
    3_314,
    3_315,
    3_319,
    3_320,
    3_324,
    3_325,
    3_329,
    3_330,
    3_334,
    3_335,
    3_339,
    3_340,
    3_344,
    3_345,
    3_349,
    3_350,
    6_503,
    6_506,
    6_512,
    6_696,
    6_697,
    6_698,
    6_699,
    6_986,
    6_989,
    7_013,
    7_075,
    7_105,
    7_119,
    7_225,
    7_295,
    7_303,
    7_304,
    7_324,
    7_358,
    7_411,
    7_419,
    7_455,
    7_467,
    7_484,
    7_497,
    7_510,
    7_523,
    7_541,
    7_586,
    7_677,
    7_700,
    7_790,
    7_816,
    7_828,
]
EXPECTED_CANDIDATE_IDS_SHA256 = (
    "FD49D3BA09ADF8116F1ACD817C33569D93C8E952B0271CB4F79BFF1F560672BF"
)

SELECTED_IDS = [2_581, 3_105, 3_106, 3_107, 3_108, 6_986, 7_677, 7_828]
EXPECTED_SELECTED_IDS_SHA256 = (
    "54515802F2DE57ACA59985B84CEBFBE073F3C54403ADFDC892E21A9530197C6F"
)
EXCLUDED_IDS = sorted(set(CANDIDATE_IDS) - set(SELECTED_IDS))
EXPECTED_EXCLUDED_IDS_SHA256 = (
    "96F17D586211FB707DA28B11682F07306DB8E2555E1CD03A0AAE260C44142E72"
)

DYNAMIC_TOKEN_ONLY_IDS = [
    2_953,
    2_954,
    2_955,
    2_959,
    2_960,
    2_964,
    2_965,
    2_967,
    *range(2_972, 2_998),
    3_109,
    3_116,
]
INTERNAL_SPEAKER_KEY_IDS = list(range(3_000, 3_007))
INTERNAL_EVENT_KEY_IDS = [
    3_309,
    3_310,
    3_314,
    3_315,
    3_319,
    3_320,
    3_324,
    3_325,
    3_329,
    3_330,
    3_334,
    3_335,
    3_339,
    3_340,
    3_344,
    3_345,
    3_349,
    3_350,
]
DYNAMIC_TOKEN_PUNCTUATION_IDS = [6_512, 7_816]
PUNCTUATION_ONLY_IDS = [
    6_503,
    6_506,
    6_696,
    6_697,
    6_698,
    6_699,
    6_989,
    7_013,
    7_075,
    7_105,
    7_119,
    7_225,
    7_295,
    7_303,
    7_304,
    7_324,
    7_358,
    7_411,
    7_419,
    7_455,
    7_467,
    7_484,
    7_497,
    7_510,
    7_523,
    7_541,
    7_586,
    7_700,
    7_790,
]

EXCLUSION_CLASSES: dict[str, dict[str, Any]] = {
    "dynamic_substitution_token_only": {
        "ids": DYNAMIC_TOKEN_ONLY_IDS,
        "ids_sha256": "8F938EE0D55B00410DA051C5FB25C3D6A03DB0D7BE96305C4F4CBF3B2DCE9C35",
    },
    "internal_speaker_lookup_key": {
        "ids": INTERNAL_SPEAKER_KEY_IDS,
        "ids_sha256": "DCFA8857788FE1D57FC736A63BB35842829CDF3B4E556BBCF07801E9D789F39E",
    },
    "internal_event_lookup_key": {
        "ids": INTERNAL_EVENT_KEY_IDS,
        "ids_sha256": "CBD6A8F8CB20A423BE5D38411A6AB667ACECB736DCE08404B714ABDC1882D9FA",
    },
    "dynamic_token_with_nonlexical_punctuation": {
        "ids": DYNAMIC_TOKEN_PUNCTUATION_IDS,
        "ids_sha256": "EB777212C19F61EDE6DD65A01FCD7BACB8233AAAF173A3AD7446D3DA9C8E7E00",
    },
    "nonlexical_punctuation_only": {
        "ids": PUNCTUATION_ONLY_IDS,
        "ids_sha256": "3D958F8F4976C12C1192A6B994AD034AB3079F588F5C944865F6F4518B38513E",
    },
}

OVERLAY_NAME = "msgev_ko_pk_native_batch01_8.v1.json"
EVIDENCE_NAME = "msgev_pk_native_batch01_alignment.v1.json"
REVIEW_NAME = "msgev_pk_native_batch01_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgev_pk_native_batch01/public/{OVERLAY_NAME}"
TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")

EXPECTED_TARGET_COUNT = 12_906
EXPECTED_TARGET_IDS_SHA256 = base.EXPECTED_TARGET_IDS_SHA256
EXPECTED_PRIOR_PATH_COUNT = 33
EXPECTED_PRIOR_PATHS_SHA256 = (
    "FB92F35DB8E05681F1DD867D26EB5982AFE04555E506EC6B72C4288A32C59F95"
)
EXPECTED_PRIOR_CLAIM_COUNT = 13_020
EXPECTED_PRIOR_CLAIM_IDS_SHA256 = (
    "EE20E900D4E50A0A35E945497693070D95E78F25E6CAE0077F533F77E929BBE0"
)
EXPECTED_PRIOR_TARGET_COUNT = 11_422
EXPECTED_PRIOR_TARGET_IDS_SHA256 = (
    "013D5E2B0F4F5F80FC13901D978E908A32A1D0AE7817EC33F57F3112789A0C82"
)
EXPECTED_PRIOR_OUTSIDE_TARGET_COUNT = 1_598
EXPECTED_PRIOR_OUTSIDE_TARGET_IDS_SHA256 = base.EXPECTED_PRIOR_OUTSIDE_TARGET_IDS_SHA256
EXPECTED_PRE_BATCH_GAP_COUNT = 1_484
EXPECTED_PRE_BATCH_GAP_IDS_SHA256 = (
    "5DF2D48250EDDE18F962515214B6868861D3BC382347B203954C15682CB25C63"
)

# Filled after deterministic generation and used only for post-registration
# self validation.
EXPECTED_OVERLAY_SHA256 = (
    "049A0A885F4E02F9975D7585567F3B3066DCA05C76642A07860314AA6726964D"
)

TRANSLATIONS: dict[int, str] = {
    2_581: "유키 히데야스",
    3_105: "우키타 아사히",
    3_106: "아키타 사네스에",
    3_107: "사나다 노부유키",
    3_108: "니시오 니자에몬",
    6_986: (
        "\x1bCA[b826]\x1bCZ와 \x1bCA아라키 무라시게\x1bCZ는 오랜 지인이었다.\n"
        "\x1bCA무라시게\x1bCZ의 모반을 막기 위해,\n"
        "그는 홀로 \x1bCC아리오카성\x1bCZ에 들어갔다."
    ),
    7_677: (
        "\x1bCA[bm1871]\x1bCZ에게 몸을 의탁한 옛 \x1bCB다케다 가문\x1bCZ의 가신들은\n"
        "특히 \x1bCA나오마사\x1bCZ를 두려워하여 \x1bCA[bm1871]\x1bCZ에게 호소하며,\n"
        "이에야스가 이 문제를 해결해 주길 바랐다."
    ),
    7_828: (
        "\x1bCA미쓰히데\x1bCZ는 \x1bCC혼노지\x1bCZ의 변으로 옛 주군을 멸하고 새로운\n"
        "천하인이 되었지만, 그의 앞을 가로막은 자는\n"
        "\x1bCA히데요시\x1bCZ였다. 어쩌면 이것도 필연이었을지 모른다."
    ),
}

DECISIONS: dict[int, dict[str, str]] = {
    2_581: {"kind": "proper_name", "basis": "official_pk_four_language_alignment"},
    3_105: {"kind": "proper_name", "basis": "official_pk_four_language_alignment"},
    3_106: {"kind": "proper_name", "basis": "official_pk_four_language_alignment"},
    3_107: {"kind": "proper_name", "basis": "official_pk_four_language_alignment"},
    3_108: {"kind": "proper_name", "basis": "official_pk_four_language_alignment"},
    6_986: {"kind": "narrative", "basis": "official_pk_sc_jp_tc_en_context"},
    7_677: {"kind": "narrative", "basis": "official_pk_sc_jp_tc_en_context"},
    7_828: {"kind": "narrative", "basis": "official_pk_sc_jp_tc_en_context"},
}

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
DYNAMIC_ONLY_RE = re.compile(r"\[bm?\d+\]")
INTERNAL_SPEAKER_RE = re.compile(
    r"(?:0daimyou|1announcer|6announcer_C|5announcer_B|4announcer_K|3user|2meishu)"
)


class NativeBatchError(ValueError):
    """Raised when selection, source, translation, or safety pins change."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def artifact_metadata(relative: str, blob: bytes) -> dict[str, Any]:
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _safe_out_root(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise NativeBatchError("output must remain inside the patch workspace") from exc
    return resolved


def load_target_catalog(path: Path, repo_root: Path) -> dict[str, Any]:
    catalog, blob = common.load_json_strict(path)
    if catalog.get("schema") != "nobu16.kr.translation-target-keys.v0.1":
        raise NativeBatchError("translation target catalog schema changed")
    if catalog.get("source_free") is not True or catalog.get("contains_source_text") is not False:
        raise NativeBatchError("translation target catalog is not source-free")
    resources = catalog.get("resources")
    rows = (
        [row for row in resources if row.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(rows) != 1:
        raise NativeBatchError("target catalog has no unique msgev row")
    row = rows[0]
    ids = row.get("target_ids")
    if not isinstance(ids, list) or any(type(value) is not int for value in ids):
        raise NativeBatchError("msgev target IDs are invalid")
    typed = [int(value) for value in ids]
    if typed != sorted(set(typed)):
        raise NativeBatchError("msgev target IDs are not sorted and unique")
    if (
        len(typed) != EXPECTED_TARGET_COUNT
        or hash_json(typed) != EXPECTED_TARGET_IDS_SHA256
        or row.get("target_count") != EXPECTED_TARGET_COUNT
        or row.get("target_keys_sha256") != EXPECTED_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("msgev exact target set differs from its pin")
    return {
        "path": _repo_relative(path, repo_root),
        "catalog_sha256": sha256(blob),
        "entry_count": len(typed),
        "ids_sha256": hash_json(typed),
        "ids": set(typed),
    }


def _load_overlay(path: Path) -> tuple[dict[str, Any], bytes, list[int]]:
    overlay, blob = common.load_json_strict(path)
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise NativeBatchError(f"overlay targets another resource: {path}")
    return overlay, blob, [int(entry["id"]) for entry in entries]


def audit_progress_registration(
    progress_path: Path, repo_root: Path, target_ids: set[int]
) -> dict[str, Any]:
    progress, _blob = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    rows = (
        [row for row in resources if row.get("path") == RESOURCE]
        if isinstance(resources, list)
        else []
    )
    if len(rows) != 1:
        raise NativeBatchError("progress catalog has no unique msgev row")
    patterns = rows[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise NativeBatchError("msgev progress overlay paths are invalid")

    if len(patterns) != len(set(patterns)):
        raise NativeBatchError("msgev progress overlay paths are duplicated")
    if patterns.count(SELF_OVERLAY_PATH) > 1:
        raise NativeBatchError("self overlay is registered more than once")

    nonself = [pattern for pattern in patterns if pattern != SELF_OVERLAY_PATH]
    predecessor_patterns = nonself[:EXPECTED_PRIOR_PATH_COUNT]
    if (
        len(predecessor_patterns) != EXPECTED_PRIOR_PATH_COUNT
        or hash_json(predecessor_patterns) != EXPECTED_PRIOR_PATHS_SHA256
    ):
        raise NativeBatchError("prior msgev progress path set/order changed")

    prior_ids: list[int] = []
    all_registered_ids: list[int] = []
    self_count = 0
    for pattern in patterns:
        paths = sorted(repo_root.glob(pattern))
        if len(paths) != 1:
            raise NativeBatchError(
                f"progress overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        logical = _repo_relative(path, repo_root)
        if logical != pattern:
            raise NativeBatchError("msgev progress paths must be exact repo-relative paths")
        overlay, overlay_blob, ids = _load_overlay(path)
        if logical == SELF_OVERLAY_PATH:
            if overlay.get("overlay_id") != BATCH_ID or ids != SELECTED_IDS:
                raise NativeBatchError("self registration overlay identity changed")
            if hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise NativeBatchError("self registration ID hash changed")
            if (
                EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__"
                and sha256(overlay_blob) != EXPECTED_OVERLAY_SHA256
            ):
                raise NativeBatchError("self registration overlay hash changed")
            self_count += 1
        elif pattern in predecessor_patterns:
            prior_ids.extend(ids)
        all_registered_ids.extend(ids)

    if len(all_registered_ids) != len(set(all_registered_ids)):
        raise NativeBatchError("registered msgev overlays overlap")
    if len(prior_ids) != len(set(prior_ids)):
        raise NativeBatchError("prior msgev overlays overlap")
    claims = set(prior_ids)
    if (
        len(claims) != EXPECTED_PRIOR_CLAIM_COUNT
        or hash_json(sorted(claims)) != EXPECTED_PRIOR_CLAIM_IDS_SHA256
    ):
        raise NativeBatchError("prior msgev claim set changed")
    target_claims = claims & target_ids
    outside_claims = claims - target_ids
    if (
        len(target_claims) != EXPECTED_PRIOR_TARGET_COUNT
        or hash_json(sorted(target_claims)) != EXPECTED_PRIOR_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("prior msgev target-intersection claims changed")
    if (
        len(outside_claims) != EXPECTED_PRIOR_OUTSIDE_TARGET_COUNT
        or hash_json(sorted(outside_claims)) != EXPECTED_PRIOR_OUTSIDE_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("prior msgev outside-target claims changed")
    gap_ids = sorted(target_ids - claims)
    if (
        len(gap_ids) != EXPECTED_PRE_BATCH_GAP_COUNT
        or hash_json(gap_ids) != EXPECTED_PRE_BATCH_GAP_IDS_SHA256
    ):
        raise NativeBatchError("pre-batch exact target gap changed")
    if gap_ids[: len(CANDIDATE_IDS)] != CANDIDATE_IDS:
        raise NativeBatchError("candidate set is not the first 100 unclaimed target IDs")
    successor_ids = set(all_registered_ids) - claims - (
        set(SELECTED_IDS) if self_count else set()
    )
    if successor_ids & set(CANDIDATE_IDS):
        raise NativeBatchError("a successor overlay overlaps this batch candidate range")
    if claims.intersection(SELECTED_IDS):
        raise NativeBatchError("selected IDs overlap a prior overlay")
    if not set(CANDIDATE_IDS).issubset(target_ids):
        raise NativeBatchError("candidate set contains an outside-target ID")

    return {
        "prior_overlay_path_count": len(predecessor_patterns),
        "prior_overlay_paths_sha256": hash_json(predecessor_patterns),
        "prior_claim_count": len(claims),
        "prior_claim_ids_sha256": hash_json(sorted(claims)),
        "prior_target_intersection_count": len(target_claims),
        "prior_target_intersection_ids_sha256": hash_json(sorted(target_claims)),
        "prior_outside_target_count": len(outside_claims),
        "prior_outside_target_ids_sha256": hash_json(sorted(outside_claims)),
        "pre_batch_gap_count": len(gap_ids),
        "pre_batch_gap_ids_sha256": hash_json(gap_ids),
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
        "selected_count": len(SELECTED_IDS),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "excluded_count": len(EXCLUDED_IDS),
        "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
        "selected_prior_overlap_count": 0,
        "selected_target_intersection_count": len(SELECTED_IDS),
        "selected_outside_target_count": 0,
        "target_coverage_after_registration": len(target_claims) + len(SELECTED_IDS),
        "target_gap_after_registration": len(gap_ids) - len(SELECTED_IDS),
        "self_registration_states_allowed": ["absent", "one_exact_path"],
        "self_excluded_from_prior_claims": True,
        "registration_order_independent": True,
        "ids": claims,
    }


def exclusion_reason_by_id() -> dict[int, str]:
    result: dict[int, str] = {}
    for reason, descriptor in EXCLUSION_CLASSES.items():
        ids = list(descriptor["ids"])
        if hash_json(ids) != descriptor["ids_sha256"]:
            raise NativeBatchError(f"exclusion class {reason} ID hash changed")
        for entry_id in ids:
            if entry_id in result:
                raise NativeBatchError("exclusion classes overlap")
            result[entry_id] = reason
    if sorted(result) != EXCLUDED_IDS:
        raise NativeBatchError("exclusion classes do not exactly partition exclusions")
    return result


def _has_letter_or_number(text: str) -> bool:
    return any(unicodedata.category(character)[0] in {"L", "N"} for character in text)


def _remove_runtime_tokens(text: str) -> str:
    value = common.ESC_RE.sub("", text)
    return base.BRACKET_TOKEN_RE.sub("", value)


def validate_exclusion_shape(
    entry_id: int, reason: str, sources: dict[str, Any]
) -> None:
    values = {
        language: sources[language]["table"].texts[entry_id]
        for language in ("SC", "JP", "EN", "TC")
    }
    sc = values["SC"]
    if reason == "dynamic_substitution_token_only":
        if len(set(values.values())) != 1 or DYNAMIC_ONLY_RE.fullmatch(sc) is None:
            raise NativeBatchError(f"ID {entry_id} is no longer a pure dynamic token")
    elif reason == "internal_speaker_lookup_key":
        if len(set(values.values())) != 1 or INTERNAL_SPEAKER_RE.fullmatch(sc) is None:
            raise NativeBatchError(f"ID {entry_id} is no longer an internal speaker key")
    elif reason == "internal_event_lookup_key":
        if len(set(values.values())) != 1 or not sc.startswith("event_ending_region_"):
            raise NativeBatchError(f"ID {entry_id} is no longer an internal event key")
    elif reason == "dynamic_token_with_nonlexical_punctuation":
        if not base.BRACKET_TOKEN_RE.search(sc) or _has_letter_or_number(_remove_runtime_tokens(sc)):
            raise NativeBatchError(f"ID {entry_id} is no longer token plus punctuation")
    elif reason == "nonlexical_punctuation_only":
        if _has_letter_or_number(sc) or common.ESC_RE.search(sc) or base.BRACKET_TOKEN_RE.search(sc):
            raise NativeBatchError(f"ID {entry_id} is no longer punctuation-only")
    else:
        raise NativeBatchError(f"unknown exclusion reason {reason}")


def switch_alignment_status(sources: dict[str, Any], entry_id: int) -> dict[str, Any]:
    buckets = strict.exact_jp_buckets(
        {
            "pk_jp": sources["JP"],
            "base_jp": sources["base_jp"],
            "switch_ko": sources["switch_ko"],
        }
    )
    jp = sources["JP"]["table"].texts[entry_id]
    rows = buckets.get(common.text_hash(jp), [])
    exact = [row for row in rows if row["jp"] == jp]
    meaningful = strict.resolve_unique_meaningful_ko(exact, jp) if exact else None
    if rows or exact or meaningful is not None:
        raise NativeBatchError(f"ID {entry_id} unexpectedly gained a Switch exact mapping")
    return {
        "exact_japanese_hash_bucket_count": 0,
        "exact_japanese_value_count": 0,
        "meaningful_switch_korean_count": 0,
        "switch_exact_mapping_available": False,
    }


def validate_translation(source_sc: str, translation: str, entry_id: int) -> dict[str, Any]:
    if not common.has_semantic_text(source_sc):
        raise NativeBatchError(f"ID {entry_id} is not a visible PK SC target")
    if not common.has_semantic_text(translation) or HANGUL_RE.search(translation) is None:
        raise NativeBatchError(f"ID {entry_id} lacks meaningful Hangul")
    if strict.upstream.contains_cjk_or_kana(translation):
        raise NativeBatchError(f"ID {entry_id} contains CJK or Kana")
    problems = common.invariant_mismatches(source_sc, translation)
    if problems:
        raise NativeBatchError(f"ID {entry_id} PK SC invariants differ: {problems}")
    source_brackets = base.BRACKET_TOKEN_RE.findall(source_sc)
    target_brackets = base.BRACKET_TOKEN_RE.findall(translation)
    if source_brackets != target_brackets:
        raise NativeBatchError(f"ID {entry_id} custom bracket sequence differs")
    return {
        "pk_sc_invariants_preserved": True,
        "custom_bracket_tokens_preserved": True,
        "custom_bracket_token_count": len(source_brackets),
        "source_script_free": True,
    }


def derive_candidate_partition(
    sources: dict[str, Any], target_ids: set[int], prior_ids: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if len(CANDIDATE_IDS) != 100 or hash_json(CANDIDATE_IDS) != EXPECTED_CANDIDATE_IDS_SHA256:
        raise NativeBatchError("candidate ID set differs from its pin")
    if hash_json(SELECTED_IDS) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeBatchError("selected ID set differs from its pin")
    if hash_json(EXCLUDED_IDS) != EXPECTED_EXCLUDED_IDS_SHA256:
        raise NativeBatchError("excluded ID set differs from its pin")
    if set(SELECTED_IDS) | set(EXCLUDED_IDS) != set(CANDIDATE_IDS):
        raise NativeBatchError("selected/excluded partition does not cover candidates")
    if sorted(TRANSLATIONS) != SELECTED_IDS or sorted(DECISIONS) != SELECTED_IDS:
        raise NativeBatchError("translation and decision tables do not cover selected IDs")

    reasons = exclusion_reason_by_id()
    entries: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    review_exclusions: list[dict[str, Any]] = []
    for entry_id in CANDIDATE_IDS:
        if entry_id not in target_ids or entry_id in prior_ids:
            raise NativeBatchError(f"ID {entry_id} is not an unclaimed exact target")
        hashes = {
            language: common.text_hash(sources[language]["table"].texts[entry_id])
            for language in ("SC", "JP", "EN", "TC")
        }
        if entry_id in reasons:
            reason = reasons[entry_id]
            validate_exclusion_shape(entry_id, reason, sources)
            evidence_rows.append(
                {
                    "id": entry_id,
                    "status": "excluded",
                    "official_pk_utf16le_sha256": hashes,
                    "exclusion_reason": reason,
                    "preserve_stock_value": True,
                    "overlay_claim_created": False,
                    "selected_within_exact_target_key": True,
                }
            )
            review_exclusions.append(
                {
                    "id": entry_id,
                    "status": "excluded",
                    "reason": reason,
                    "runtime_safety_decision": "preserve_stock_value",
                    "progress_claim_created": False,
                }
            )
            continue

        source_sc = sources["SC"]["table"].texts[entry_id]
        translation = TRANSLATIONS[entry_id]
        checks = validate_translation(source_sc, translation, entry_id)
        switch_status = switch_alignment_status(sources, entry_id)
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": hashes["SC"],
                "ko": translation,
            }
        )
        evidence_rows.append(
            {
                "id": entry_id,
                "status": "translated",
                "official_pk_utf16le_sha256": hashes,
                "ko_utf16le_sha256": common.text_hash(translation),
                "translation_kind": DECISIONS[entry_id]["kind"],
                "semantic_basis": DECISIONS[entry_id]["basis"],
                "official_multilingual_context_reviewed": True,
                "selected_within_exact_target_key": True,
                "selected_within_stock_visible_target": True,
                "disjoint_from_prior_overlays": True,
                **switch_status,
                **checks,
            }
        )

    if [entry["id"] for entry in entries] != SELECTED_IDS:
        raise NativeBatchError("derived selected entries changed")
    if [entry["id"] for entry in review_exclusions] != EXCLUDED_IDS:
        raise NativeBatchError("derived exclusions changed")
    return entries, evidence_rows, review_exclusions


def actual_input_snapshot(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
) -> dict[str, str]:
    source_pins = base.SOURCE_PINS
    paths = {
        "switch_archive": archive_path,
        "base_jp": game_root / strict.upstream.SOURCE_PINS["base_jp"]["logical_path"],
        "pk_sc": repo_root / source_pins["SC"]["logical_path"],
        "pk_jp": game_root / source_pins["JP"]["logical_path"],
        "pk_en": game_root / source_pins["EN"]["logical_path"],
        "pk_tc": game_root / source_pins["TC"]["logical_path"],
        "target_catalog": target_path,
        "progress_catalog": progress_path,
    }
    return {name: sha256(path.read_bytes()) for name, path in paths.items()}


def build_once(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    target = load_target_catalog(target_path, repo_root)
    progress = audit_progress_registration(progress_path, repo_root, target["ids"])
    sources = base.load_sources(game_root, repo_root, archive_path)
    entries, evidence_rows, review_exclusions = derive_candidate_partition(
        sources, target["ids"], progress["ids"]
    )
    rebuilt_a = base.reconstruct_target(sources, entries)
    rebuilt_b = base.reconstruct_target(sources, entries)
    if rebuilt_a != rebuilt_b:
        raise NativeBatchError("in-memory target reconstruction is not deterministic")

    source_public = {
        language: sources[language]["public_pin"]
        for language in ("SC", "JP", "EN", "TC")
    }
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            key: source_public["SC"][key]
            for key in (
                "size",
                "packed_sha256",
                "raw_size",
                "raw_sha256",
                "string_count",
            )
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)

    target_public = {key: value for key, value in target.items() if key != "ids"}
    progress_public = {key: value for key, value in progress.items() if key != "ids"}
    class_summary = {
        reason: {
            "count": len(descriptor["ids"]),
            "ids_sha256": descriptor["ids_sha256"],
        }
        for reason, descriptor in EXCLUSION_CLASSES.items()
    }
    evidence = {
        "schema": "nobu16.kr.msgev-pk-native-batch01-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "candidate_count": len(CANDIDATE_IDS),
            "candidate_ids": CANDIDATE_IDS,
            "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
            "translated_count": len(entries),
            "translated_ids": SELECTED_IDS,
            "translated_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
            "excluded_count": len(review_exclusions),
            "excluded_ids": EXCLUDED_IDS,
            "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
            "candidate_partition_complete": True,
        },
        "official_source_files": source_public,
        "switch_release_checked": strict.SWITCH_RELEASE,
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "translation_policy": {
            "method": "native_korean_from_official_pk_multilingual_context",
            "semantic_context_languages": ["SC", "JP", "EN", "TC"],
            "switch_exact_mapping_checked": True,
            "switch_exact_mapping_available_for_translated_rows": False,
            "runtime_contract_authority": "pk_sc",
            "excluded_runtime_keys_are_not_translation_progress": True,
            "published_source_material": "hashes_only",
        },
        "entry_count": len(evidence_rows),
        "entries": evidence_rows,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.msgev-pk-native-batch01-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "quality_state": "native_semantic_review_complete_runtime_review_pending",
        "candidate_count": len(CANDIDATE_IDS),
        "translated_count": len(entries),
        "excluded_count": len(review_exclusions),
        "translated": [
            {
                "id": row["id"],
                "status": "translated",
                "translation_kind": row["translation_kind"],
                "semantic_basis": row["semantic_basis"],
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
                "source_script_free": True,
                "prior_overlay_disjoint": True,
                "exact_target": True,
                "runtime_reviewed": False,
            }
            for row in evidence_rows
            if row["status"] == "translated"
        ],
        "excluded": review_exclusions,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }

    values = {
        f"public/{OVERLAY_NAME}": overlay,
        f"evidence/{EVIDENCE_NAME}": evidence,
        f"review/{REVIEW_NAME}": review,
    }
    files = {relative: encode_json(value) for relative, value in values.items()}
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    scans = {relative: strict.source_free_counts(blob) for relative, blob in files.items()}
    if any(scan != expected_scan for scan in scans.values()):
        raise NativeBatchError("a generated public artifact contains source script")
    artifacts = {
        relative: artifact_metadata(relative, blob) for relative, blob in files.items()
    }
    validation = {
        "schema": "nobu16.kr.msgev-pk-native-batch01-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": evidence["scope"],
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "replacement_invariants": {
            "checked": len(entries),
            "failures": 0,
            "pk_sc_contract_preserved_count": len(entries),
            "custom_bracket_contract_preserved_count": len(entries),
            "source_script_free_count": len(entries),
        },
        "target_reconstruction": rebuilt_a,
        "source_free_scan": scans,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "pre_and_post_self_registration_must_be_byte_identical": True,
            "in_memory_target_a_b_equal": True,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "base_msg_sc_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
            "font_modified": False,
            "commit_or_push_performed": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_blob = encode_json(validation)
    if strict.source_free_counts(validation_blob) != expected_scan:
        raise NativeBatchError("generated validation contains source script")
    files[VALIDATION_NAME] = validation_blob

    for relative, blob in files.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)

    target_after = load_target_catalog(target_path, repo_root)
    progress_after = audit_progress_registration(
        progress_path, repo_root, target_after["ids"]
    )
    after = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    if before != after:
        raise NativeBatchError("a read-only input changed during generation")
    if target_after != target or progress_after != progress:
        raise NativeBatchError("target or progress ownership changed during generation")
    return {
        "candidate_count": len(CANDIDATE_IDS),
        "entry_count": len(entries),
        "excluded_count": len(review_exclusions),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "target": rebuilt_a,
        "files": files,
        "artifacts": {
            **artifacts,
            VALIDATION_NAME: artifact_metadata(VALIDATION_NAME, validation_blob),
        },
    }


def build_reproducibly(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    target_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    out_root = _safe_out_root(out_root, repo_root)
    before = actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    )
    tmp_root = repo_root / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b01-a-", dir=tmp_root
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b01-b-", dir=tmp_root
    ) as second_dir:
        first = build_once(
            game_root,
            repo_root,
            archive_path,
            target_path,
            progress_path,
            Path(first_dir),
        )
        second = build_once(
            game_root,
            repo_root,
            archive_path,
            target_path,
            progress_path,
            Path(second_dir),
        )
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise NativeBatchError("isolated builds are not byte-identical")
    final = build_once(
        game_root, repo_root, archive_path, target_path, progress_path, out_root
    )
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise NativeBatchError("final build differs from isolated builds")
    if (
        actual_input_snapshot(game_root, repo_root, archive_path, target_path, progress_path)
        != before
    ):
        raise NativeBatchError("a read-only input changed across the reproducible build")
    return final


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=REPO_ROOT / strict.SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE
    )
    parser.add_argument(
        "--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root,
            args.repo_root,
            args.archive,
            args.target_catalog,
            args.progress,
            args.out_root,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"candidates={result['candidate_count']}")
    print(f"translated={result['entry_count']}")
    print(f"excluded={result['excluded_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for relative, artifact in sorted(result["artifacts"].items()):
        print(f"{relative}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
