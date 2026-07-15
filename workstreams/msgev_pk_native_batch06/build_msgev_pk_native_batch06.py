#!/usr/bin/env python3
"""Build the sixth and final safe-semantic PK ``msgev`` translation batch.

The batch translates every remaining safe semantic PK/SC target row after
batch05. Batch05 is an explicit predecessor whether or not root progress has
already registered it. Internal keys, runtime substitution tokens and other
structural rows remain stock; output publishes only source hashes plus Korean
replacements.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
BATCH05_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch05"
BATCH04_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch04"
BATCH03_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch03"
BATCH02_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch02"
BATCH01_ROOT = REPO_ROOT / "workstreams" / "msgev_pk_native_batch01"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(BATCH05_ROOT), str(BATCH04_ROOT), str(BATCH03_ROOT), str(BATCH02_ROOT), str(BATCH01_ROOT), str(TOOLS_ROOT)]

import build_msgev_pk_native_batch05 as previous  # noqa: E402


_TRANSLATIONS_SPEC = importlib.util.spec_from_file_location(
    "_nobu16_msgev_pk_native_batch06_translations",
    WORKSTREAM_ROOT / "translations.py",
)
if _TRANSLATIONS_SPEC is None or _TRANSLATIONS_SPEC.loader is None:
    raise RuntimeError("cannot load batch06 translation table")
_TRANSLATIONS_MODULE = importlib.util.module_from_spec(_TRANSLATIONS_SPEC)
_TRANSLATIONS_SPEC.loader.exec_module(_TRANSLATIONS_MODULE)
TRANSLATIONS = _TRANSLATIONS_MODULE.TRANSLATIONS
SELECTED_IDS = sorted(TRANSLATIONS)


batch01 = previous.batch01
base = previous.base
common = previous.common
strict = previous.strict
NativeBatchError = previous.NativeBatchError

BATCH_ID = "msgev-pk-native-batch06-260.v1"
RESOURCE = "MSG_PK/SC/msgev.bin"
OVERLAY_NAME = "msgev_ko_pk_native_batch06_260.v1.json"
EVIDENCE_NAME = "msgev_pk_native_batch06_alignment.v1.json"
REVIEW_NAME = "msgev_pk_native_batch06_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_PATH = f"workstreams/msgev_pk_native_batch06/public/{OVERLAY_NAME}"
EXPLICIT_PREDECESSOR_PATH = previous.SELF_OVERLAY_PATH
TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")

EXPECTED_TARGET_COUNT = 12_906
EXPECTED_TARGET_IDS_SHA256 = base.EXPECTED_TARGET_IDS_SHA256
EXPECTED_BASE_PREDECESSOR_PATH_COUNT = 37
EXPECTED_PREDECESSOR_PATHS_SHA256 = (
    "8365CF6198413E21A49FED9997C24247081C8B3E842DE92C5F947BDA4451CF91"
)
EXPECTED_BASE_PREDECESSOR_PATHS_SHA256 = (
    "8D09C8EF05CBFB14CF9688515FBDF91B1AEBFC0AB8532F1CD0F8AD815C49A0D7"
)
EXPECTED_PREDECESSOR_PATH_COUNT = 38
EXPECTED_PREDECESSOR_CLAIM_COUNT = 14_003
EXPECTED_PREDECESSOR_CLAIM_IDS_SHA256 = (
    "AA2105AC5212BA9683FB276584855F292067897FD9F4E642D4A81A64BB0EFA9C"
)
EXPECTED_PREDECESSOR_TARGET_COUNT = 12_405
EXPECTED_PREDECESSOR_TARGET_IDS_SHA256 = (
    "6F623197834E21DA72D4D7B40DC1C23647789EF91E862B9F1438A948E9104823"
)
EXPECTED_PREDECESSOR_OUTSIDE_TARGET_COUNT = 1_598
EXPECTED_PREDECESSOR_OUTSIDE_TARGET_IDS_SHA256 = (
    "5C050980004350E17D6B4E5BFC0151075CFDEBF1D41006A7E7FBE5BBC2B0E313"
)
EXPECTED_PRE_BATCH_GAP_COUNT = 501
EXPECTED_PRE_BATCH_GAP_IDS_SHA256 = (
    "48C3FA2D9A07EFD29015F40C19853559C411E17883EFB810B961993135965275"
)
EXPECTED_SELECTED_IDS_SHA256 = (
    "F2372A6D2D9623486D3C1D48B1F03687604718A279C6F43FF22C2F0E6DD9E477"
)
EXPECTED_CANDIDATE_COUNT = 501
EXPECTED_CANDIDATE_IDS_SHA256 = (
    "48C3FA2D9A07EFD29015F40C19853559C411E17883EFB810B961993135965275"
)
EXPECTED_EXCLUDED_COUNT = 241
EXPECTED_EXCLUDED_IDS_SHA256 = (
    "A58E26CCD1D7DD8F7505B0134FD3354E7001B6C91B27A1D7011EBAD29AA4D2B0"
)
EXPECTED_NEW_EXCLUDED_IDS_SHA256 = (
    "8C1F631AA190B9C703098BEFAAF46C3BDC9622EF9D29A72560A9BDB1F54C99F6"
)

EXPECTED_OVERLAY_SHA256 = (
    "94DAF36792E1BCAC12DDB5658DA91785B487D825939E2D7C94D381751C2D0BFF"
)

SWITCH_SEMANTIC_REUSE_IDS: list[int] = []
PK_NATIVE_IDS = SELECTED_IDS

NEW_PUNCTUATION_ONLY_IDS = [10_926]
NEW_CUSTOM_BRACKET_IDS = [
    10_805, 10_806, 10_807, 10_809, 10_827, 10_828, 10_829, 10_832,
    10_837, 10_840, 10_843, 10_845, 10_850, 10_851, 10_852, 10_853,
    10_905, 10_959, 10_960, 10_961,
]
NEW_INTERNAL_KEY_IDS = [
    14_550, 14_551, 14_552, 14_553, 14_554, 14_555, 14_556, 14_557,
    14_558, 14_559, 14_560, 14_561, 14_562, 14_563, 14_566, 14_567,
    14_568, 14_569, 14_570, 14_573, 14_574, 14_575, 14_576, 14_577,
    14_578, 14_580, 14_581, 14_582, 14_583, 14_584, 14_585, 14_586,
    14_587, 14_588, 14_589, 14_590, 14_591, 14_592, 14_593, 14_594,
    14_595, 14_597, 14_598, 14_600, 14_601, 14_602, 14_603, 14_604,
    14_605, 14_606, 14_630, 14_631, 14_632, 14_633, 14_634, 14_635,
    14_636, 14_637, 14_638, 14_639, 14_640, 14_641,
]
NEW_FORMAT_ONLY_IDS = [
    17_113, 17_114, 17_138, 17_139, 17_169, 17_179, 17_180, 17_236,
    17_261, 17_267, 17_445, 17_707, 17_709, 17_717, 17_729,
]
NEW_EXCLUDED_IDS = sorted(
    NEW_PUNCTUATION_ONLY_IDS
    + NEW_CUSTOM_BRACKET_IDS
    + NEW_INTERNAL_KEY_IDS
    + NEW_FORMAT_ONLY_IDS
)
EXCLUDED_IDS = sorted(set(previous.EXCLUDED_IDS) | set(NEW_EXCLUDED_IDS))
CANDIDATE_IDS = sorted(set(SELECTED_IDS) | set(EXCLUDED_IDS))

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


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


def _load_overlay(path: Path) -> tuple[dict[str, Any], bytes, list[int]]:
    overlay, blob = common.load_json_strict(path)
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise NativeBatchError(f"overlay targets another resource: {path}")
    return overlay, blob, [int(entry["id"]) for entry in entries]


def audit_progress_registration(
    progress_path: Path, repo_root: Path, target_ids: set[int]
) -> dict[str, Any]:
    """Freeze base ownership and add batch05 as an explicit predecessor.

    Root progress may not have registered batch05 yet.  Its exact pinned
    overlay is therefore loaded independently and counted exactly once in the
    logical predecessor set.  Exact self and later successor registration do
    not alter generated bytes.
    """

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
    if patterns.count(EXPLICIT_PREDECESSOR_PATH) > 1:
        raise NativeBatchError("batch05 overlay is registered more than once")

    without_owned = [
        pattern
        for pattern in patterns
        if pattern not in {SELF_OVERLAY_PATH, EXPLICIT_PREDECESSOR_PATH}
    ]
    base_patterns = without_owned[:EXPECTED_BASE_PREDECESSOR_PATH_COUNT]
    successor_patterns = without_owned[EXPECTED_BASE_PREDECESSOR_PATH_COUNT:]
    if (
        len(base_patterns) != EXPECTED_BASE_PREDECESSOR_PATH_COUNT
        or hash_json(base_patterns) != EXPECTED_BASE_PREDECESSOR_PATHS_SHA256
    ):
        raise NativeBatchError("pinned base msgev predecessor path set/order changed")
    logical_predecessor_patterns = [*base_patterns, EXPLICIT_PREDECESSOR_PATH]
    if (
        len(logical_predecessor_patterns) != EXPECTED_PREDECESSOR_PATH_COUNT
        or hash_json(logical_predecessor_patterns) != EXPECTED_PREDECESSOR_PATHS_SHA256
    ):
        raise NativeBatchError("logical predecessor path set/order changed")

    base_ids: list[int] = []
    all_registered_ids: list[int] = []
    for pattern in patterns:
        paths = sorted(repo_root.glob(pattern))
        if len(paths) != 1:
            raise NativeBatchError(
                f"progress overlay pattern {pattern!r} resolved to {len(paths)} files"
            )
        path = paths[0]
        if _repo_relative(path, repo_root) != pattern:
            raise NativeBatchError("msgev progress paths must be exact repo-relative paths")
        overlay, overlay_blob, ids = _load_overlay(path)
        if pattern == SELF_OVERLAY_PATH:
            if overlay.get("overlay_id") != BATCH_ID or ids != SELECTED_IDS:
                raise NativeBatchError("self registration overlay identity changed")
            if hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise NativeBatchError("self registration ID hash changed")
            if (
                EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__"
                and sha256(overlay_blob) != EXPECTED_OVERLAY_SHA256
            ):
                raise NativeBatchError("self registration overlay hash changed")
        elif pattern == EXPLICIT_PREDECESSOR_PATH:
            if (
                overlay.get("overlay_id") != previous.BATCH_ID
                or ids != previous.SELECTED_IDS
                or sha256(overlay_blob) != previous.EXPECTED_OVERLAY_SHA256
            ):
                raise NativeBatchError("registered batch05 overlay identity changed")
        elif pattern in base_patterns:
            base_ids.extend(ids)
        all_registered_ids.extend(ids)

    if len(all_registered_ids) != len(set(all_registered_ids)):
        raise NativeBatchError("registered msgev overlays overlap")

    explicit_path = repo_root / EXPLICIT_PREDECESSOR_PATH
    explicit_overlay, explicit_blob, explicit_ids = _load_overlay(explicit_path)
    if (
        explicit_overlay.get("overlay_id") != previous.BATCH_ID
        or explicit_ids != previous.SELECTED_IDS
        or sha256(explicit_blob) != previous.EXPECTED_OVERLAY_SHA256
    ):
        raise NativeBatchError("explicit batch05 predecessor identity changed")

    claims = set(base_ids) | set(explicit_ids)
    if len(claims) != len(base_ids) + len(explicit_ids):
        raise NativeBatchError("batch05 overlaps the pinned base predecessor set")
    if (
        len(claims) != EXPECTED_PREDECESSOR_CLAIM_COUNT
        or hash_json(sorted(claims)) != EXPECTED_PREDECESSOR_CLAIM_IDS_SHA256
    ):
        raise NativeBatchError("logical predecessor msgev claim set changed")
    target_claims = claims & target_ids
    outside_claims = claims - target_ids
    if (
        len(target_claims) != EXPECTED_PREDECESSOR_TARGET_COUNT
        or hash_json(sorted(target_claims)) != EXPECTED_PREDECESSOR_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("logical predecessor target claims changed")
    if (
        len(outside_claims) != EXPECTED_PREDECESSOR_OUTSIDE_TARGET_COUNT
        or hash_json(sorted(outside_claims))
        != EXPECTED_PREDECESSOR_OUTSIDE_TARGET_IDS_SHA256
    ):
        raise NativeBatchError("logical predecessor outside-target claims changed")
    gap_ids = sorted(target_ids - claims)
    if (
        len(gap_ids) != EXPECTED_PRE_BATCH_GAP_COUNT
        or hash_json(gap_ids) != EXPECTED_PRE_BATCH_GAP_IDS_SHA256
    ):
        raise NativeBatchError("pre-batch exact target gap changed")

    owned_registered = set(base_ids)
    if EXPLICIT_PREDECESSOR_PATH in patterns:
        owned_registered.update(explicit_ids)
    if SELF_OVERLAY_PATH in patterns:
        owned_registered.update(SELECTED_IDS)
    successor_ids = set(all_registered_ids) - owned_registered
    if successor_ids & (set(CANDIDATE_IDS) | claims):
        raise NativeBatchError("a successor overlay overlaps owned batch coordinates")
    if claims & set(SELECTED_IDS):
        raise NativeBatchError("selected IDs overlap a logical predecessor overlay")

    return {
        "predecessor_overlay_path_count": len(logical_predecessor_patterns),
        "predecessor_overlay_paths_sha256": hash_json(logical_predecessor_patterns),
        "base_predecessor_overlay_path_count": len(base_patterns),
        "base_predecessor_overlay_paths_sha256": hash_json(base_patterns),
        "explicit_batch05_overlay_sha256": sha256(explicit_blob),
        "predecessor_claim_count": len(claims),
        "predecessor_claim_ids_sha256": hash_json(sorted(claims)),
        "predecessor_target_intersection_count": len(target_claims),
        "predecessor_target_intersection_ids_sha256": hash_json(sorted(target_claims)),
        "predecessor_outside_target_count": len(outside_claims),
        "predecessor_outside_target_ids_sha256": hash_json(sorted(outside_claims)),
        "pre_batch_gap_count": len(gap_ids),
        "pre_batch_gap_ids_sha256": hash_json(gap_ids),
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
        "selected_count": len(SELECTED_IDS),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "excluded_count": len(EXCLUDED_IDS),
        "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
        "selected_predecessor_overlap_count": 0,
        "selected_target_intersection_count": len(SELECTED_IDS),
        "selected_outside_target_count": 0,
        "target_coverage_after_registration": len(target_claims) + len(SELECTED_IDS),
        "target_gap_after_registration": len(gap_ids) - len(SELECTED_IDS),
        "batch05_registration_states_allowed": ["absent", "one_exact_path"],
        "batch05_counted_exactly_once": True,
        "self_registration_states_allowed": ["absent", "one_exact_path"],
        "self_excluded_from_predecessor_claims": True,
        "successor_registration_tolerant": True,
        "ids": claims,
    }

def _has_letter_or_number(text: str) -> bool:
    return previous._has_letter_or_number(text)


def _remove_runtime_tokens(text: str) -> str:
    return previous._remove_runtime_tokens(text)


def _looks_like_internal_key(text: str) -> bool:
    stripped = _remove_runtime_tokens(text).strip()
    return bool(re.fullmatch(r"[A-Za-z0-9_./:+-]+", stripped))


def _looks_like_format_only(text: str) -> bool:
    if not common.PRINTF_RE.search(text):
        return False
    visible = common.PRINTF_RE.sub("", _remove_runtime_tokens(text))
    return not _has_letter_or_number(visible)


def exclusion_reason_by_id() -> dict[int, str]:
    reasons = dict(previous.exclusion_reason_by_id())
    for entry_id in NEW_PUNCTUATION_ONLY_IDS:
        reasons[entry_id] = "nonlexical_punctuation_only"
    for entry_id in NEW_CUSTOM_BRACKET_IDS:
        reasons[entry_id] = "runtime_custom_bracket_substitution"
    for entry_id in NEW_INTERNAL_KEY_IDS:
        reasons[entry_id] = "internal_ascii_key"
    for entry_id in NEW_FORMAT_ONLY_IDS:
        reasons[entry_id] = "runtime_printf_placeholder_only"
    if sorted(reasons) != EXCLUDED_IDS:
        raise NativeBatchError("exclusion reasons do not exactly cover exclusions")
    return reasons


def validate_exclusion_shape(
    entry_id: int, reason: str, sources: dict[str, Any]
) -> None:
    if entry_id in previous.EXCLUDED_IDS:
        previous.validate_exclusion_shape(entry_id, reason, sources)
        return
    sc = sources["SC"]["table"].texts[entry_id]
    if reason == "nonlexical_punctuation_only":
        if (
            _has_letter_or_number(sc)
            or common.ESC_RE.search(sc)
            or base.BRACKET_TOKEN_RE.search(sc)
        ):
            raise NativeBatchError(f"ID {entry_id} is no longer punctuation-only")
    elif reason == "runtime_custom_bracket_substitution":
        if not base.BRACKET_TOKEN_RE.search(sc):
            raise NativeBatchError(f"ID {entry_id} lost its custom bracket token")
    elif reason == "internal_ascii_key":
        if not _looks_like_internal_key(sc):
            raise NativeBatchError(f"ID {entry_id} is no longer an internal ASCII key")
    elif reason == "runtime_printf_placeholder_only":
        if not _looks_like_format_only(sc):
            raise NativeBatchError(f"ID {entry_id} is no longer printf-only")
    else:
        raise NativeBatchError(f"unknown new exclusion reason {reason}")


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


def audit_switch_reuse_for_selected(sources: dict[str, Any]) -> dict[str, Any]:
    """Prove that Switch v1.3 offers no safe semantic mapping for this batch."""

    buckets = strict.exact_jp_buckets(
        {
            "pk_jp": sources["JP"],
            "base_jp": sources["base_jp"],
            "switch_ko": sources["switch_ko"],
        }
    )
    exact_ids: list[int] = []
    same_index_semantic_ids: list[int] = []
    for entry_id in SELECTED_IDS:
        jp = sources["JP"]["table"].texts[entry_id]
        exact = [
            row
            for row in buckets.get(common.text_hash(jp), [])
            if row["jp"] == jp
            and common.has_semantic_text(row["jp"])
            and common.has_semantic_text(row["ko"])
        ]
        if exact:
            exact_ids.append(entry_id)
        if entry_id < len(sources["base_jp"]["table"].texts):
            switch_jp = sources["base_jp"]["table"].texts[entry_id]
            switch_ko = sources["switch_ko"]["table"].texts[entry_id]
            if common.has_semantic_text(switch_jp) and common.has_semantic_text(
                switch_ko
            ):
                same_index_semantic_ids.append(entry_id)
    return {
        "release": strict.SWITCH_RELEASE,
        "selected_checked_count": len(SELECTED_IDS),
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "exact_jp_semantic_mapping_count": len(exact_ids),
        "exact_jp_semantic_mapping_ids_sha256": hash_json(exact_ids),
        "same_index_semantic_candidate_count": len(same_index_semantic_ids),
        "same_index_semantic_candidate_ids_sha256": hash_json(same_index_semantic_ids),
        "reuse_count": 0,
        "decision": "official_pk_four_language_direct_translation",
        "checked_before_native_translation": True,
    }


def derive_candidate_partition(
    sources: dict[str, Any], target_ids: set[int], predecessor_ids: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if len(SELECTED_IDS) != 260 or hash_json(SELECTED_IDS) != EXPECTED_SELECTED_IDS_SHA256:
        raise NativeBatchError("selected ID set differs from its pin")
    if len(NEW_EXCLUDED_IDS) != 98 or hash_json(NEW_EXCLUDED_IDS) != EXPECTED_NEW_EXCLUDED_IDS_SHA256:
        raise NativeBatchError("new exclusion ID set differs from its pin")
    if len(EXCLUDED_IDS) != EXPECTED_EXCLUDED_COUNT or hash_json(EXCLUDED_IDS) != EXPECTED_EXCLUDED_IDS_SHA256:
        raise NativeBatchError("complete exclusion ID set differs from its pin")
    if len(CANDIDATE_IDS) != EXPECTED_CANDIDATE_COUNT or hash_json(CANDIDATE_IDS) != EXPECTED_CANDIDATE_IDS_SHA256:
        raise NativeBatchError("candidate ID set differs from its pin")
    if sorted(TRANSLATIONS) != SELECTED_IDS:
        raise NativeBatchError("translation table does not exactly cover selected IDs")
    if SWITCH_SEMANTIC_REUSE_IDS or len(PK_NATIVE_IDS) != 260:
        raise NativeBatchError("translation provenance partition changed")

    gaps = sorted(target_ids - predecessor_ids)
    lexical_ids = [
        entry_id
        for entry_id in gaps
        if entry_id not in previous.EXCLUDED_IDS
        and _has_letter_or_number(
            _remove_runtime_tokens(sources["SC"]["table"].texts[entry_id])
        )
        and not _looks_like_internal_key(sources["SC"]["table"].texts[entry_id])
        and not base.BRACKET_TOKEN_RE.search(sources["SC"]["table"].texts[entry_id])
        and not _looks_like_format_only(sources["SC"]["table"].texts[entry_id])
    ]
    if lexical_ids != SELECTED_IDS:
        raise NativeBatchError("selection no longer covers every remaining safe semantic gap row")
    candidate_ids = gaps
    if candidate_ids != CANDIDATE_IDS:
        raise NativeBatchError("complete remaining candidate partition changed")

    reasons = exclusion_reason_by_id()
    jp_buckets = strict.exact_jp_buckets(
        {
            "pk_jp": sources["JP"],
            "base_jp": sources["base_jp"],
            "switch_ko": sources["switch_ko"],
        }
    )
    entries: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    review_exclusions: list[dict[str, Any]] = []
    for entry_id in CANDIDATE_IDS:
        if entry_id not in target_ids or entry_id in predecessor_ids:
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
        if entry_id in SWITCH_SEMANTIC_REUSE_IDS:
            if entry_id >= len(sources["base_jp"]["table"].texts):
                raise NativeBatchError(f"ID {entry_id} has no same-index Switch row")
            switch_jp = sources["base_jp"]["table"].texts[entry_id]
            switch_ko = sources["switch_ko"]["table"].texts[entry_id]
            if not common.has_semantic_text(switch_jp) or not common.has_semantic_text(switch_ko):
                raise NativeBatchError(f"ID {entry_id} lost its semantic Switch evidence")
            provenance = {
                "translation_kind": "switch_same_index_semantic_reuse",
                "semantic_basis": "switch_v13_same_index_plus_official_pk_four_language_review",
                "switch_same_index_jp_utf16le_sha256": common.text_hash(switch_jp),
                "switch_same_index_ko_utf16le_sha256": common.text_hash(switch_ko),
                "adapted_to_exact_pk_sc_runtime_contract": True,
            }
        else:
            jp = sources["JP"]["table"].texts[entry_id]
            exact = [
                row
                for row in jp_buckets.get(common.text_hash(jp), [])
                if row["jp"] == jp
                and common.has_semantic_text(row["jp"])
                and common.has_semantic_text(row["ko"])
            ]
            provenance = {
                "translation_kind": "pk_native_event_translation",
                "semantic_basis": "official_pk_sc_jp_tc_en_context",
                "switch_exact_mapping_available": bool(exact),
                "switch_exact_mapping_count": len(exact),
            }
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
                "official_multilingual_context_reviewed": True,
                "selected_within_exact_target_key": True,
                "selected_within_stock_visible_target": True,
                "disjoint_from_predecessor_overlays": True,
                **provenance,
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
        "translation_table": WORKSTREAM_ROOT / "translations.py",
        "explicit_batch05_overlay": repo_root / EXPLICIT_PREDECESSOR_PATH,
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
    target = batch01.load_target_catalog(target_path, repo_root)
    progress = audit_progress_registration(progress_path, repo_root, target["ids"])
    sources = base.load_sources(game_root, repo_root, archive_path)
    switch_audit = audit_switch_reuse_for_selected(sources)
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
            for key in ("size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)

    target_public = {key: value for key, value in target.items() if key != "ids"}
    progress_public = {key: value for key, value in progress.items() if key != "ids"}
    reason_map = exclusion_reason_by_id()
    class_summary = {
        reason: {
            "count": sum(1 for value in reason_map.values() if value == reason),
            "ids_sha256": hash_json(
                sorted(entry_id for entry_id, value in reason_map.items() if value == reason)
            ),
        }
        for reason in sorted(set(reason_map.values()))
    }
    scope = {
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_ids": CANDIDATE_IDS,
        "candidate_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
        "translated_count": len(entries),
        "translated_ids": SELECTED_IDS,
        "translated_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "switch_semantic_reuse_count": 0,
        "pk_native_translation_count": len(PK_NATIVE_IDS),
        "excluded_count": len(review_exclusions),
        "excluded_ids": EXCLUDED_IDS,
        "excluded_ids_sha256": EXPECTED_EXCLUDED_IDS_SHA256,
        "new_excluded_count": len(NEW_EXCLUDED_IDS),
        "candidate_partition_complete": True,
    }
    evidence = {
        "schema": "nobu16.kr.msgev-pk-native-batch06-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": scope,
        "official_source_files": source_public,
        "switch_release_checked": strict.SWITCH_RELEASE,
        "switch_reuse_audit": switch_audit,
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "translation_policy": {
            "selection": "all_remaining_safe_semantic_gap_rows_after_batch05",
            "runtime_contract_authority": "pk_sc",
            "semantic_context_languages": ["SC", "JP", "TC", "EN"],
            "switch_reuse_checked_before_native_translation": True,
            "switch_reusable_selected_rows": 0,
            "pk_only_rows_translated_natively": True,
            "excluded_runtime_keys_are_not_translation_progress": True,
            "published_source_material": "hashes_only",
        },
        "entry_count": len(evidence_rows),
        "entries": evidence_rows,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.msgev-pk-native-batch06-review.v1",
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
                "predecessor_overlay_disjoint": True,
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
        "schema": "nobu16.kr.msgev-pk-native-batch06-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": scope,
        "target_catalog": target_public,
        "progress_registration_audit": progress_public,
        "exclusion_classes": class_summary,
        "switch_reuse_audit": switch_audit,
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
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
            "translation_table_path": "translations.py",
            "translation_table_sha256": sha256((WORKSTREAM_ROOT / "translations.py").read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "pre_and_post_batch05_and_self_registration_must_be_byte_identical": True,
            "successor_registration_tolerant": True,
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

    target_after = batch01.load_target_catalog(target_path, repo_root)
    progress_after = audit_progress_registration(progress_path, repo_root, target_after["ids"])
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
        prefix="nobu16-msgev-native-b05-a-", dir=tmp_root
    ) as first_dir, tempfile.TemporaryDirectory(
        prefix="nobu16-msgev-native-b05-b-", dir=tmp_root
    ) as second_dir:
        first = build_once(
            game_root, repo_root, archive_path, target_path, progress_path, Path(first_dir)
        )
        second = build_once(
            game_root, repo_root, archive_path, target_path, progress_path, Path(second_dir)
        )
        if first["files"] != second["files"] or first["target"] != second["target"]:
            raise NativeBatchError("isolated builds are not byte-identical")
    final = build_once(
        game_root, repo_root, archive_path, target_path, progress_path, out_root
    )
    if final["files"] != first["files"] or final["target"] != first["target"]:
        raise NativeBatchError("final build differs from isolated builds")
    if actual_input_snapshot(
        game_root, repo_root, archive_path, target_path, progress_path
    ) != before:
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
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
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
