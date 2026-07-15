#!/usr/bin/env python3
"""Create a source-free PK msgev cleanup overlay for 20 prior exclusions.

The preceding Switch v1.1 transfer deliberately excluded twenty otherwise
structurally compatible entries because its Korean values still contained CJK
ideographs or kana.  This builder retains the same PC-PK compatibility gates,
then applies project-reviewed Korean-only normalizations for those exact IDs.

The Switch archive and PC resources are read-only inputs.  The builder emits
only a source-free overlay and audit metadata; it never extracts the archive,
writes a complete resource, or changes an installed game file.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
UPSTREAM_ROOT = REPO_ROOT / "workstreams" / "switch_msgev_v11"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(UPSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgev_v11 as upstream  # noqa: E402


BATCH_ID = "switch-v11-pk-msgev-cjk-kana-cleanup-20.v1"
OVERLAY_NAME = "msgev_ko_switch_v11_cjk_kana_cleanup_20.v1.json"
EVIDENCE_NAME = "switch_v11_cjk_kana_cleanup_alignment.v1.json"
REVIEW_NAME = "switch_v11_cjk_kana_cleanup_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
RESOURCE = upstream.RESOURCE

UPSTREAM_OVERLAY_RELATIVE = Path(
    "workstreams/switch_msgev_v11/public/msgev_ko_switch_v11_ported_7025.v1.json"
)
UPSTREAM_OVERLAY_SHA256 = (
    "71652CACEB757BFFF47FB119789150BD841DD9FF6B6AC180D5B2AA1B06231703"
)
UPSTREAM_OVERLAY_ENTRY_COUNT = 7_025
UPSTREAM_OVERLAY_IDS_SHA256 = upstream.EXPECTED_SELECTED_IDS_SHA256
EXPECTED_EFFECTIVE_OWNER_COUNT = 12_494
EXPECTED_EFFECTIVE_OWNER_IDS_SHA256 = (
    "D12F718C5083B720F46C84F88E487E5C2695595347B1162DC0D2F0D411033854"
)

CANDIDATE_IDS = (
    6531,
    6587,
    6704,
    7166,
    7177,
    7260,
    7340,
    7442,
    7732,
    7755,
    7834,
    8283,
    8341,
    8818,
    8904,
    9149,
    9324,
    9330,
    9473,
    9708,
)
EXPECTED_CANDIDATE_IDS_SHA256 = (
    "F9B2C54B499583605D1D8748747123DE1C4FF2C3C990383FD0E672DF8D7BCFDB"
)
EXPECTED_UNIQUE_JP_TO_KO_COUNT = 20
EXPECTED_UNIQUE_JP_TO_KO_IDS_SHA256 = EXPECTED_CANDIDATE_IDS_SHA256

# These project-reviewed strings deliberately contain Hangul and ordinary
# punctuation only.  Control codes, dynamic tokens, and line breaks retain the
# PK SC layout.  No source-language text is emitted by this workstream.
TRANSLATIONS: dict[int, str] = {
    6531: "\x1bCB오다 가문\x1bCZ·\x1bCA노부나가\x1bCZ 거성——",
    6587: (
        "\x1bCA우지쿠니\x1bCZ는 출가하고,\n"
        "\x1bCA우지노리\x1bCZ·\x1bCA우지나오\x1bCZ는 \x1bCC고야산\x1bCZ에서 칩거하게 된다.\n"
        "이로써 전국 다이묘·\x1bCB고호조씨\x1bCZ는 멸망했다."
    ),
    6704: (
        "\x1bCA오다 노부나가\x1bCZ로부터 재흥을 인정받아,\n"
        "\x1bCB모리\x1bCZ와 접하는 최전선의 \x1bCC고즈키성\x1bCZ을 맡은\n"
        "\x1bCA아마고 가쓰히사\x1bCZ·\x1bCA야마나카 시카노스케\x1bCZ 주종…"
    ),
    7166: "\x1bCC가스가야마\x1bCZ 성하·\x1bCA[b1672]\x1bCZ 저택——",
    7177: (
        "\x1bCC하리마국\x1bCZ·\x1bCC고즈키성\x1bCZ을 함락시킨 \x1bCB오다가\x1bCZ에서는,\n"
        "새로운 성주를 누구로 할지,\n"
        "\x1bCA노부나가\x1bCZ와 중신들 사이에 논의가 오가고 있었다."
    ),
    7260: (
        "길이 십팔 간, 대포 여러 문을 갖추고, 얇은 철판으로\n"
        "배의 바깥을 뒤덮은, 거대한 대아타케부네 여섯 척이\n"
        "마침내 완성된 것이다."
    ),
    7340: "\x1bCB오다 가문\x1bCZ·\x1bCA[bs754]\x1bCZ 진중——",
    7442: (
        "\x1bCA겐뇨\x1bCZ·\x1bCA뇨슌니\x1bCZ 부부를 비롯해 \x1bCB혼간지\x1bCZ의 주요\n"
        "인사들은 \x1bCC이시야마\x1bCZ를 떠나 \x1bCC기슈 사기노모리\x1bCZ로 향했다.\n"
        "그러나…"
    ),
    7732: (
        "\x1bCA오다\x1bCZ·\x1bCA[bs1871]\x1bCZ 연합군의 맹공으로,\n"
        "\x1bCB다케다가\x1bCZ는 완전히 붕괴했다."
    ),
    7755: "\x1bCC다카마쓰성\x1bCZ·성 안——",
    7834: (
        "\x1bCC야마자키\x1bCZ·\x1bCC덴노잔\x1bCZ 땅에서 맞선 \x1bCA미쓰히데\x1bCZ와 \x1bCA히데요시\x1bCZ는\n"
        "결전에 이르렀다. 기세가 앞선 \x1bCA히데요시\x1bCZ군이\n"
        "점차 \x1bCA아케치\x1bCZ의 군세를 압박해 갔다."
    ),
    8283: (
        "\x1bCC고마키야마\x1bCZ 전선 이외에도 각지에서\n"
        "\x1bCA히데요시\x1bCZ 측, \x1bCA노부카쓰\x1bCZ·\x1bCA[bm1871]\x1bCZ 측의 군세가 충돌하였으나\n"
        "어느 쪽도 결정적인 승패는 나지 않았다."
    ),
    8341: "\x1bCC셋쓰국\x1bCZ·\x1bCC이시야마 고보\x1bCZ.",
    8818: (
        "관백 \x1bCA히데요시\x1bCZ는 여러 나라의 다이묘에게, 제멋대로의 영토 다툼을\n"
        "금하고, 그것을 '소부지'라 칭하였다.\n"
        "이를 거스르는 자는 관백의 토벌을 받는다."
    ),
    8904: (
        "관백 전하께서는 강녕하시온지…\n"
        "\x1bCA시마즈 요시히사\x1bCZ, 개명하여 입도 \x1bCA류하쿠\x1bCZ이옵니다."
    ),
    9149: (
        "\x1bCA모리 모토나리\x1bCZ의 아들이라 하면, 적남·\x1bCA다카모토\x1bCZ 외에\n"
        "\x1bCA깃카와 모토하루\x1bCZ·\x1bCA고바야카와 다카카게\x1bCZ 형제가 유명하지만\n"
        "그 외에도 자식을 두고 있었다."
    ),
    9324: (
        "\x1bCB아시카가 쇼군가\x1bCZ·\x1bCB간레이 호소카와 가문\x1bCZ 각각의 내분이\n"
        "오래 이어져 혼돈이 극에 달한 \x1bCC기나이\x1bCZ에서는\n"
        "새로이 \x1bCB미요시 가문\x1bCZ이 주가를 능가하는 힘을 지녔다."
    ),
    9330: (
        "\x1bCC동국\x1bCZ으로 눈을 돌리면, 서로 다투어 온\n"
        "\x1bCB이마가와\x1bCZ·\x1bCB다케다\x1bCZ·\x1bCB호조\x1bCZ의 유력 세 다이묘가,\n"
        "이해를 넘어 손을 잡으려 움직이기 시작하고 있었다…"
    ),
    9473: (
        "\x1bCA다카마사\x1bCZ의 이복동생인 \x1bCA마고시로\x1bCZ와 \x1bCA기헤이지\x1bCZ 등\n"
        "다른 자식에게 자연히 애정이 옮겨 갔다.\n"
        "\x1bCA도시마사\x1bCZ·\x1bCA다카마사\x1bCZ 부자는 소원해져 갔다."
    ),
    9708: (
        "\x1bCA시바타 가쓰이에\x1bCZ·\x1bCA[b754]\x1bCZ 등 중신들도,\n"
        "\x1bCA노부나가\x1bCZ의 생환 소식을 받고,\n"
        "잇따라 \x1bCA미쓰히데\x1bCZ 토벌군에 참가했다."
    ),
}


class CleanupError(ValueError):
    """Raised when the reviewed cleanup contract is not satisfied."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_free_counts(blob: bytes) -> dict[str, int]:
    return upstream.source_free_counts(blob)


def contains_forbidden_source_script(value: str) -> bool:
    """Reject every Han and kana range covered by the public-artifact scan."""

    return source_free_counts(value.encode("utf-8"))["han_or_kana_count"] != 0


def unique_switch_jp_to_ko_mapping(
    sources: dict[str, dict[str, Any]], candidate_ids: tuple[int, ...]
) -> dict[int, dict[str, int]]:
    """Prove that each selected JP source has exactly one semantic KO mapping.

    The PC/Switch numeric-id equality gate alone is intentionally not treated
    as a semantic mapping proof.  For every selected base-JP string, gather
    all Switch values at equal JP strings that contain semantic Hangul.  A
    candidate is portable only if that set has one value and it is the value
    at the candidate's own numeric ID.  Only counts and hashes leave this
    function; no upstream text is written to public artifacts.
    """

    base_jp = sources["base_jp"]["table"]
    switch_ko = sources["switch_ko"]["table"]
    if base_jp.string_count != switch_ko.string_count:
        raise CleanupError("Switch Korean and PC base JP table counts differ")

    semantic_values: dict[str, set[str]] = defaultdict(set)
    jp_occurrences: dict[str, int] = defaultdict(int)
    for jp_value, ko_value in zip(base_jp.texts, switch_ko.texts):
        jp_occurrences[jp_value] += 1
        if upstream.has_meaningful_hangul(ko_value):
            semantic_values[jp_value].add(ko_value)

    mapping: dict[int, dict[str, int]] = {}
    for entry_id in candidate_ids:
        jp_value = base_jp.texts[entry_id]
        mapped_values = semantic_values[jp_value]
        own_value = switch_ko.texts[entry_id]
        if own_value not in mapped_values:
            raise CleanupError(f"id {entry_id}: Switch Korean is absent from JP-to-KO map")
        if len(mapped_values) != 1:
            raise CleanupError(f"id {entry_id}: JP source has ambiguous Switch KO mappings")
        mapping[entry_id] = {
            "jp_occurrence_count": jp_occurrences[jp_value],
            "semantic_ko_mapping_count": len(mapped_values),
        }
    return mapping


def input_snapshot(game_root: Path, repo_root: Path, archive_path: Path) -> dict[str, str]:
    snapshot = upstream.input_snapshot(game_root, repo_root, archive_path)
    predecessor = repo_root / UPSTREAM_OVERLAY_RELATIVE
    snapshot["upstream_public_overlay"] = sha256(predecessor.read_bytes())
    return snapshot


def load_predecessor_overlay(repo_root: Path) -> dict[str, Any]:
    path = repo_root / UPSTREAM_OVERLAY_RELATIVE
    overlay, blob = common.load_json_strict(path)
    if sha256(blob) != UPSTREAM_OVERLAY_SHA256:
        raise CleanupError("upstream Switch msgev overlay SHA-256 does not match pin")
    resource, stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise CleanupError("upstream Switch overlay does not target PK msgev")
    ids = [int(entry["id"]) for entry in entries]
    if len(ids) != UPSTREAM_OVERLAY_ENTRY_COUNT or hash_json(ids) != UPSTREAM_OVERLAY_IDS_SHA256:
        raise CleanupError("upstream Switch overlay entry set does not match pin")
    return {
        "path": UPSTREAM_OVERLAY_RELATIVE.as_posix(),
        "sha256": sha256(blob),
        "entry_count": len(ids),
        "ids_sha256": hash_json(ids),
        "stock_sc": stock,
        "ids": ids,
    }


def effective_existing_catalog(repo_root: Path, predecessor: dict[str, Any]) -> dict[str, Any]:
    base_catalog = upstream.existing_msgev_catalog_snapshot(repo_root)
    base_ids = set(base_catalog["ids"])
    upstream_ids = set(predecessor["ids"])
    overlap = sorted(base_ids & upstream_ids)
    if overlap:
        raise CleanupError("upstream Switch overlay overlaps earlier public PK msgev catalogs")
    ids = sorted(base_ids | upstream_ids)
    if len(ids) != EXPECTED_EFFECTIVE_OWNER_COUNT:
        raise CleanupError("effective PK msgev catalog count does not match pin")
    if hash_json(ids) != EXPECTED_EFFECTIVE_OWNER_IDS_SHA256:
        raise CleanupError("effective PK msgev catalog IDs do not match pin")
    return {
        "unique_id_count": len(ids),
        "ids_sha256": hash_json(ids),
        "cross_catalog_overlap_count": 0,
        "prior_catalog": {key: value for key, value in base_catalog.items() if key != "ids"},
        "upstream_switch_overlay": {
            key: predecessor[key]
            for key in ("path", "sha256", "entry_count", "ids_sha256")
        },
        "ids": ids,
    }


def validate_candidate_contract(
    sources: dict[str, dict[str, Any]],
    base_catalog: dict[str, Any],
    effective_catalog: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, int], list[int], dict[int, dict[str, int]]]:
    # Re-run the upstream gate with its original catalog.  It confirms that
    # exactly these 20 IDs were excluded only by the CJK/kana source filter.
    _selected, stages, excluded_ids, _bracket_mismatch = upstream.select_portable_entries(
        sources, base_catalog
    )
    if tuple(excluded_ids) != CANDIDATE_IDS:
        raise CleanupError("upstream source-script exclusion IDs changed")
    if hash_json(excluded_ids) != EXPECTED_CANDIDATE_IDS_SHA256:
        raise CleanupError("cleanup candidate IDs do not match pin")
    if tuple(sorted(TRANSLATIONS)) != CANDIDATE_IDS:
        raise CleanupError("manual cleanup translations do not match the candidate ID set")
    jp_to_ko_mapping = unique_switch_jp_to_ko_mapping(sources, CANDIDATE_IDS)
    if len(jp_to_ko_mapping) != EXPECTED_UNIQUE_JP_TO_KO_COUNT:
        raise CleanupError("unique Switch JP-to-KO mapping count does not match pin")
    if hash_json(sorted(jp_to_ko_mapping)) != EXPECTED_UNIQUE_JP_TO_KO_IDS_SHA256:
        raise CleanupError("unique Switch JP-to-KO mapping IDs do not match pin")

    owner_ids = set(effective_catalog["ids"])
    switch = sources["switch_ko"]["table"]
    base_jp = sources["base_jp"]["table"]
    pk_jp = sources["pk_jp"]["table"]
    pk_sc = sources["pk_sc_stock"]["table"]
    selected: list[dict[str, Any]] = []
    bracket_mismatch_ids: list[int] = []
    for entry_id in CANDIDATE_IDS:
        if entry_id in owner_ids:
            raise CleanupError(f"id {entry_id}: overlaps an effective public PK msgev overlay")
        switch_ko = switch.texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        if not upstream.has_meaningful_hangul(switch_ko):
            raise CleanupError(f"id {entry_id}: upstream source is no longer meaningful Korean")
        if not contains_forbidden_source_script(switch_ko):
            raise CleanupError(f"id {entry_id}: upstream source no longer needs cleanup")
        if contains_forbidden_source_script(replacement):
            raise CleanupError(f"id {entry_id}: cleanup replacement contains forbidden source script")
        if not upstream.has_meaningful_hangul(replacement):
            raise CleanupError(f"id {entry_id}: cleanup replacement lacks meaningful Korean")
        if base_jp.texts[entry_id] != pk_jp.texts[entry_id]:
            raise CleanupError(f"id {entry_id}: PC base JP no longer equals PK JP")
        if switch_ko == base_jp.texts[entry_id]:
            raise CleanupError(f"id {entry_id}: Switch Korean no longer differs from common JP")
        mismatches = common.invariant_mismatches(pk_sc.texts[entry_id], replacement)
        if mismatches:
            raise CleanupError(f"id {entry_id}: PK SC invariant mismatch: {mismatches}")
        if upstream.BRACKET_TOKEN_RE.findall(pk_sc.texts[entry_id]) != upstream.BRACKET_TOKEN_RE.findall(replacement):
            bracket_mismatch_ids.append(entry_id)
        selected.append(
            {
                "id": entry_id,
                "ko": replacement,
                "source_sc_utf16le_sha256": common.text_hash(pk_sc.texts[entry_id]),
                "switch_ko_utf16le_sha256": common.text_hash(switch_ko),
                "cleanup_ko_utf16le_sha256": common.text_hash(replacement),
                "base_jp_utf16le_sha256": common.text_hash(base_jp.texts[entry_id]),
                "pk_jp_utf16le_sha256": common.text_hash(pk_jp.texts[entry_id]),
                "pk_sc_structure": upstream.source_structure(pk_sc.texts[entry_id]),
                "cleanup_ko_structure": upstream.source_structure(replacement),
            }
        )
    if bracket_mismatch_ids:
        raise CleanupError(
            "cleanup replacements do not preserve PK SC bracket tokens: "
            f"{bracket_mismatch_ids}"
        )
    return selected, stages, bracket_mismatch_ids, jp_to_ko_mapping


def reconstruct_pk_sc_target(
    pk_sc_source: dict[str, Any], selected: list[dict[str, Any]]
) -> dict[str, Any]:
    return upstream.reconstruct_pk_sc_target(pk_sc_source, selected)


def write_json(path: Path, value: Any) -> bytes:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return blob


def build_once(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    before = input_snapshot(game_root, repo_root, archive_path)
    sources = upstream.load_sources(game_root, repo_root, archive_path)
    predecessor = load_predecessor_overlay(repo_root)
    base_catalog = upstream.existing_msgev_catalog_snapshot(repo_root)
    effective_catalog = effective_existing_catalog(repo_root, predecessor)
    selected, stages, bracket_mismatch_ids, jp_to_ko_mapping = validate_candidate_contract(
        sources, base_catalog, effective_catalog
    )
    ids = [int(entry["id"]) for entry in selected]
    if len(ids) != len(CANDIDATE_IDS) or hash_json(ids) != EXPECTED_CANDIDATE_IDS_SHA256:
        raise CleanupError("selected cleanup entries do not match pin")
    target = reconstruct_pk_sc_target(sources["pk_sc_stock"], selected)

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(selected),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            key: upstream.SOURCE_PINS["pk_sc_stock"][key]
            for key in ("size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
        },
        "defaults": {"status": "translated"},
        "entries": [
            {
                "id": int(entry["id"]),
                "source_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "ko": entry["ko"],
            }
            for entry in selected
        ],
    }
    common.validate_overlay_shape(overlay)

    evidence = {
        "schema": "nobu16.kr.switch-msgev-cjk-kana-cleanup-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_release": upstream.SWITCH_RELEASE,
        "predecessor": {
            "path": predecessor["path"],
            "sha256": predecessor["sha256"],
            "entry_count": predecessor["entry_count"],
            "ids_sha256": predecessor["ids_sha256"],
            "role": "strict_switch_v11_port_with_source_script_exclusion",
        },
        "source_files": {name: dict(pin) for name, pin in upstream.SOURCE_PINS.items()},
        "selection_method": [
            "candidate_is_exact_member_of_predecessor_cjk_kana_exclusion_set",
            "pc_base_jp_equals_pc_pk_jp_at_same_numeric_id",
            "switch_patch_value_has_meaningful_hangul_and_differs_from_common_jp",
            "same_jp_source_has_exactly_one_semantic_switch_ko_mapping",
            "project_reviewed_cleanup_value_has_meaningful_hangul_and_no_cjk_or_kana",
            "cleanup_value_matches_pk_sc_printf_esc_control_and_linebreak_invariants",
            "cleanup_value_preserves_pk_sc_bracket_tokens",
            "effective_public_pk_msgev_id_exclusion",
        ],
        "selection": {
            "upstream_selection_stages": stages,
            "candidate_count": len(selected),
            "candidate_ids_sha256": hash_json(ids),
            "upstream_source_script_exclusion_count": len(CANDIDATE_IDS),
            "upstream_source_script_exclusion_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
            "strict_unique_jp_to_ko_mapping_count": len(jp_to_ko_mapping),
            "strict_unique_jp_to_ko_mapping_ids_sha256": hash_json(
                sorted(jp_to_ko_mapping)
            ),
            "cleanup_output_forbidden_script_count": 0,
            "cleanup_output_embedded_nul_count": 0,
            "bracket_token_mismatch_count": len(bracket_mismatch_ids),
            "bracket_token_mismatch_ids_sha256": hash_json(bracket_mismatch_ids),
            "switch_to_pc_numeric_id_mapping": "identity_for_ids_0_through_17867",
            "jp_original_equality_scope": "PC_base_JP_and_PC_PK_JP",
        },
        "effective_public_catalog_exclusion": {
            key: value for key, value in effective_catalog.items() if key != "ids"
        },
        "entry_count": len(selected),
        "entries": [
            {
                "id": int(entry["id"]),
                "switch_ko_utf16le_sha256": entry["switch_ko_utf16le_sha256"],
                "cleanup_ko_utf16le_sha256": entry["cleanup_ko_utf16le_sha256"],
                "base_jp_utf16le_sha256": entry["base_jp_utf16le_sha256"],
                "pk_jp_utf16le_sha256": entry["pk_jp_utf16le_sha256"],
                "pk_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "base_jp_equals_pk_jp": True,
                "switch_ko_differs_from_jp": True,
                "switch_jp_to_ko_is_unique": True,
                "switch_jp_occurrence_count": jp_to_ko_mapping[int(entry["id"])][
                    "jp_occurrence_count"
                ],
                "switch_semantic_ko_mapping_count": jp_to_ko_mapping[int(entry["id"])][
                    "semantic_ko_mapping_count"
                ],
                "upstream_switch_value_has_cjk_or_kana": True,
                "cleanup_value_has_cjk_or_kana": False,
                "pk_sc_invariants_match": True,
                "bracket_tokens_match": int(entry["id"]) not in bracket_mismatch_ids,
                "pk_sc_structure": entry["pk_sc_structure"],
                "cleanup_ko_structure": entry["cleanup_ko_structure"],
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgev-cjk-kana-cleanup-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "project_reviewed_cleanup_pending_pc_runtime_review",
        "entry_count": len(selected),
        "entries": [
            {
                "id": int(entry["id"]),
                "status": "translated",
                "translation_origin": "switch_v11_cjk_kana_cleanup_project_review",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": [
                    "pc_pk_runtime_layout_review",
                    "switch_to_pc_context_review",
                    "manual_cjk_kana_cleanup_review",
                ],
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }

    out_root = out_root.resolve()
    overlay_blob = write_json(out_root / "public" / OVERLAY_NAME, overlay)
    evidence_blob = write_json(out_root / "evidence" / EVIDENCE_NAME, evidence)
    review_blob = write_json(out_root / "review" / REVIEW_NAME, review)
    source_free_scan = {
        "overlay": source_free_counts(overlay_blob),
        "alignment_evidence": source_free_counts(evidence_blob),
        "review_index": source_free_counts(review_blob),
    }
    expected_free = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    if any(value != expected_free for value in source_free_scan.values()):
        raise CleanupError("generated public artifact contains forbidden source script")

    artifacts = {
        "overlay": {
            "path": f"public/{OVERLAY_NAME}",
            "size": len(overlay_blob),
            "sha256": sha256(overlay_blob),
        },
        "alignment_evidence": {
            "path": f"evidence/{EVIDENCE_NAME}",
            "size": len(evidence_blob),
            "sha256": sha256(evidence_blob),
        },
        "review_index": {
            "path": f"review/{REVIEW_NAME}",
            "size": len(review_blob),
            "sha256": sha256(review_blob),
        },
    }
    validation = {
        "schema": "nobu16.kr.switch-msgev-cjk-kana-cleanup-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "selection": evidence["selection"],
        "source_release": upstream.SWITCH_RELEASE,
        "source_alignment": {
            "source_string_counts": {
                name: int(pin["string_count"]) for name, pin in upstream.SOURCE_PINS.items()
            },
            "pc_base_jp_to_pk_jp_exact_match_count": stages["base_jp_equals_pk_jp_count"],
            "strict_unique_jp_to_ko_mapping_count": len(jp_to_ko_mapping),
            "cleanup_entry_reference_hash_count": len(selected) * 5,
            "pk_sc_parse_rebuild_byte_exact": True,
            "switch_patch_parse_rebuild_byte_exact": True,
            "official_source_text_embedded": False,
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_tokens",
            ],
        },
        "effective_public_catalog_exclusion": {
            "existing_unique_id_count": effective_catalog["unique_id_count"],
            "existing_ids_sha256": effective_catalog["ids_sha256"],
            "selected_overlap_count": 0,
        },
        "source_script_cleanup": {
            "predecessor_excluded_count": len(CANDIDATE_IDS),
            "predecessor_excluded_ids_sha256": EXPECTED_CANDIDATE_IDS_SHA256,
            "selected_entries_are_cjk_kana_free": True,
        },
        "reconstruction": {
            "complete_target_included": False,
            "changed_entry_count": target["changed_entry_count"],
            "target": target,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "switch_archive_extracted": False,
            "complete_game_resource_emitted": False,
            "installed_game_files_modified": False,
            "base_msg_sc_modified": False,
            "font_files_modified": False,
            "root_readme_or_progress_modified": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
        },
    }
    validation_blob = write_json(out_root / VALIDATION_NAME, validation)
    if source_free_counts(validation_blob) != expected_free:
        raise CleanupError("validation is not source-free")

    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise CleanupError("an input resource changed while building")
    return {
        "entry_count": len(selected),
        "selected_ids_sha256": hash_json(ids),
        "target": target,
        "files": {
            f"public/{OVERLAY_NAME}": overlay_blob,
            f"evidence/{EVIDENCE_NAME}": evidence_blob,
            f"review/{REVIEW_NAME}": review_blob,
            VALIDATION_NAME: validation_blob,
        },
    }


def build_reproducibly(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    game_root = game_root.resolve()
    repo_root = repo_root.resolve()
    archive_path = archive_path.resolve()
    out_root = out_root.resolve()
    before = input_snapshot(game_root, repo_root, archive_path)
    with tempfile.TemporaryDirectory(prefix="nobu16-msgev-cleanup-a-") as first_directory:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-cleanup-b-") as second_directory:
            first = build_once(game_root, repo_root, archive_path, Path(first_directory))
            second = build_once(game_root, repo_root, archive_path, Path(second_directory))
            if first["files"] != second["files"]:
                raise CleanupError("isolated builds are not byte-identical")
    final = build_once(game_root, repo_root, archive_path, out_root)
    if final["files"] != first["files"]:
        raise CleanupError("final build differs from isolated build")
    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise CleanupError("an input resource changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=REPO_ROOT / upstream.SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root, args.repo_root, args.archive, args.out_root
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"cleanup_entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['wrapper_sha256']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
