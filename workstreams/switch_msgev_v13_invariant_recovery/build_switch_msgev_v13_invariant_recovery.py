#!/usr/bin/env python3
"""Repair the safe part of the 261-row Switch-derived PK msgev residual.

The strict v1.3 exact-Japanese-hash recovery leaves 261 stock-visible rows at
its source-script and PK/SC formatting gates.  This builder preserves the
Switch Korean visible stream while restoring only mechanically provable PC
PK/SC structure:

* Japanese middle dot is normalized to the source-free Korean middle dot;
* equal-length ESC token sequences are replaced ordinally with the SC tokens;
* line-break *types/counts* are restored without moving any whitespace boundary;
* missing trailing whitespace is copied from the SC contract.

Rows whose ESC token count differs, or whose custom bracket-token sequence
differs, are excluded.  No sentence fragment or placeholder is rearranged.
Only a source-free overlay and audit metadata are emitted; complete game
resources remain read-only and are reconstructed in memory for verification.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
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
TOOLS_ROOT = REPO_ROOT / "tools"
STRICT_ROOT = REPO_ROOT / "workstreams" / "switch_msgev_v13_jp_hash_recovery"
sys.path[:0] = [str(TOOLS_ROOT), str(STRICT_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgev_v13_jp_hash_recovery as strict  # noqa: E402


BATCH_ID = "switch-v13-pk-msgev-invariant-recovery-248.v1"
OVERLAY_NAME = "msgev_ko_switch_v13_invariant_recovery_248.v1.json"
EVIDENCE_NAME = "switch_v13_msgev_invariant_recovery_alignment.v1.json"
REVIEW_NAME = "switch_v13_msgev_invariant_recovery_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
RESOURCE = strict.RESOURCE

SELF_OVERLAY_LOGICAL_PATH = (
    f"workstreams/switch_msgev_v13_invariant_recovery/public/{OVERLAY_NAME}"
)
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")
TARGET_CATALOG_RELATIVE = Path("data/public/translation_target_keys.v0.1.json")
STRICT_OVERLAY_LOGICAL_PATH = (
    "workstreams/switch_msgev_v13_jp_hash_recovery/public/"
    "msgev_ko_switch_v13_exact_jp_hash_recovery_245.v1.json"
)
STRICT_OVERLAY_SHA256 = (
    "BE5D7147E24573775713E4D4C3F31BE0029C41885FFB0DD3507BBA17610FD62D"
)
STRICT_OVERLAY_ENTRY_COUNT = 245
STRICT_OVERLAY_IDS_SHA256 = strict.EXPECTED_SELECTED_IDS_SHA256

# Filled after the first deterministic generation.  It is used only when the
# exact self path is present in the global progress catalog.
EXPECTED_OVERLAY_SHA256 = (
    "D2757409D426148CE2E636828F4693830D66A661236C4F6E816DD0D028D48F1C"
)

EXPECTED_PRIOR_PROGRESS_PATH_COUNT = 31
EXPECTED_PRIOR_PROGRESS_PATHS_SHA256 = (
    "6F4099D009F2134A5494A6317212C251C98CCA65815897D978DC868308BFA5A0"
)
EXPECTED_PRIOR_OWNER_COUNT = 12_759
EXPECTED_PRIOR_OWNER_IDS_SHA256 = (
    "929EB6EFB87F400F1F5F29E3919CA4D77B9D18BB286DA38F6889F936308F7F7C"
)

EXPECTED_TARGET_COUNT = 12_906
EXPECTED_TARGET_IDS_SHA256 = strict.EXPECTED_STOCK_VISIBLE_IDS_SHA256
EXPECTED_RESIDUAL_COUNT = 261
EXPECTED_RESIDUAL_IDS_SHA256 = (
    "3801D57790256C559045092F33764320E133BE7766F8AF32F884AD38D6E9BEB2"
)
EXPECTED_SELECTED_COUNT = 248
EXPECTED_SELECTED_IDS_SHA256 = (
    "C3B4DD558398729877C9861CF917B1C4BE2567B87CE460763FA68C7A529459D0"
)

EXPECTED_GATE_SOURCE_SCRIPT_COUNT = 4
EXPECTED_GATE_SOURCE_SCRIPT_IDS = (7_240, 7_649, 8_249, 9_461)
EXPECTED_GATE_SOURCE_SCRIPT_IDS_SHA256 = (
    "BB969DF289D8AF7256C9EEF5B97211F4C16062D3394483FDFB893AD94BB87619"
)
EXPECTED_GATE_INVARIANT_COUNT = 257
EXPECTED_GATE_INVARIANT_IDS_SHA256 = (
    "8685192614BE873A49693441DB47B614582A4EC570745CF99CADE23CA13D6076"
)

ESC_COUNT_EXCLUSION_IDS = (
    6_829,
    6_833,
    7_027,
    7_633,
    7_823,
    7_953,
    8_094,
    8_959,
    9_331,
    9_336,
    10_888,
)
ESC_COUNT_EXCLUSION_IDS_SHA256 = (
    "BADAB3AC0004BA1F7095498A6BCEF892707649217D6F426E91EF3A330B40C965"
)
BRACKET_EXCLUSION_IDS = (8_642, 9_340, 10_888)
BRACKET_EXCLUSION_IDS_SHA256 = (
    "BF807B50C14A7644B060467A87E3B6EDDA1E7AD90CF3121C743D34403055EE11"
)
EXCLUSION_CLASS_OVERLAP_IDS = (10_888,)
EXCLUSION_CLASS_OVERLAP_IDS_SHA256 = (
    "32DA574BFD69935183474214D76A69B54A2E5AC4A6B27AD10017C927DFAA4A49"
)
EXPECTED_EXCLUDED_COUNT = 13
EXPECTED_EXCLUDED_IDS = tuple(
    sorted(set(ESC_COUNT_EXCLUSION_IDS) | set(BRACKET_EXCLUSION_IDS))
)
EXPECTED_EXCLUDED_IDS_SHA256 = (
    "FBEB52131D74798885BD0BC311399EB1F054EFB0CB716BE8DFE0AD1133897C72"
)

EXPECTED_OPERATION_COMBINATIONS = {
    "line_break_template": 172,
    "esc_token_template": 61,
    "esc_token_template+line_break_template": 5,
    "trailing_whitespace_template": 4,
    "middle_dot_normalization+esc_token_template": 4,
    "line_break_template+trailing_whitespace_template": 2,
}
EXPECTED_OPERATION_CLASS_COUNTS = {
    "middle_dot_normalization": 4,
    "esc_token_template": 70,
    "line_break_template": 179,
    "trailing_whitespace_template": 6,
}

MIDDLE_DOT_JP = "\u30fb"
MIDDLE_DOT_KO = "\u00b7"
WHITESPACE_RUN_RE = re.compile(r"\s+")


class RecoveryError(ValueError):
    """Raised when a source pin, residual set, or safe repair contract changes."""


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


def source_free_counts(blob: bytes) -> dict[str, int]:
    return strict.source_free_counts(blob)


def canonical_visible_stream(text: str) -> str:
    """Remove formatting while retaining visible character and word order."""

    value = common.ESC_RE.sub("", text).replace(MIDDLE_DOT_JP, MIDDLE_DOT_KO)
    return WHITESPACE_RUN_RE.sub(" ", value).strip()


def _semantic_positions(text: str) -> tuple[list[int], int]:
    """Return visible-nonwhitespace prefix counts and total, excluding ESC."""

    excluded = [False] * len(text)
    for match in common.ESC_RE.finditer(text):
        for index in range(match.start(), match.end()):
            excluded[index] = True
    prefix = [0]
    for index, character in enumerate(text):
        increment = int(not excluded[index] and not character.isspace())
        prefix.append(prefix[-1] + increment)
    return prefix, prefix[-1]


def restore_line_break_template(source_sc: str, switch_ko: str) -> tuple[str, dict[str, Any]]:
    """Restore break count/types without changing a whitespace boundary.

    Every existing line break is first converted to one ordinary whitespace
    character.  The SC break sequence is then placed on existing interior
    whitespace boundaries.  The chosen ordered subset minimizes exact
    proportional distance from the SC anchors; ties use the lowest indexes.
    Thus no visible character, word boundary, or fragment is moved.
    """

    source_breaks = common.message_invariants(source_sc)["line_breaks"]
    switch_breaks = common.message_invariants(switch_ko)["line_breaks"]
    if source_breaks == switch_breaks:
        raise RecoveryError("line-break repair was requested for an equal template")

    source_prefix, source_total = _semantic_positions(source_sc)
    source_ratios = [
        Fraction(source_prefix[match.start()], max(source_total, 1))
        for match in common.LINE_BREAK_RE.finditer(source_sc)
    ]
    base = common.LINE_BREAK_RE.sub(" ", switch_ko)
    base_prefix, base_total = _semantic_positions(base)
    esc_indexes = {
        index
        for match in common.ESC_RE.finditer(base)
        for index in range(match.start(), match.end())
    }
    candidates: list[tuple[int, Fraction]] = []
    for index, character in enumerate(base):
        if not character.isspace() or not (0 < index < len(base) - 1):
            continue
        if index in esc_indexes or base[index - 1].isspace():
            continue
        candidates.append(
            (index, Fraction(base_prefix[index], max(base_total, 1)))
        )
    if len(candidates) < len(source_ratios):
        raise RecoveryError("not enough existing interior whitespace anchors")

    if source_ratios:
        scored = (
            (
                sum(
                    abs(candidate[index][1] - source_ratios[index])
                    for index in range(len(source_ratios))
                ),
                tuple(item[0] for item in candidate),
                candidate,
            )
            for candidate in itertools.combinations(candidates, len(source_ratios))
        )
        _cost, selected_indexes, _selected = min(scored)
    else:
        selected_indexes = ()

    characters = list(base)
    for index, token in zip(selected_indexes, source_breaks, strict=True):
        characters[index] = token
    repaired = "".join(characters)
    if canonical_visible_stream(repaired) != canonical_visible_stream(switch_ko):
        raise RecoveryError("line-break repair changed the canonical visible stream")
    return repaired, {
        "source_break_count": len(source_breaks),
        "switch_break_count_before": len(switch_breaks),
        "selected_existing_whitespace_anchor_count": len(selected_indexes),
        "visible_stream_preserved": True,
        "word_boundary_order_preserved": True,
    }


def replace_esc_tokens_ordinally(source_sc: str, switch_ko: str) -> tuple[str, dict[str, Any]]:
    source_tokens = common.message_invariants(source_sc)["esc"]
    switch_tokens = common.message_invariants(switch_ko)["esc"]
    if source_tokens == switch_tokens:
        raise RecoveryError("ESC repair was requested for an equal template")
    if len(source_tokens) != len(switch_tokens):
        raise RecoveryError("ESC token counts differ")
    replacements = iter(source_tokens)
    repaired = common.ESC_RE.sub(lambda _match: next(replacements), switch_ko)
    if canonical_visible_stream(repaired) != canonical_visible_stream(switch_ko):
        raise RecoveryError("ESC token repair changed the canonical visible stream")
    if common.message_invariants(repaired)["esc"] != source_tokens:
        raise RecoveryError("ESC token sequence was not restored exactly")
    return repaired, {
        "source_esc_token_count": len(source_tokens),
        "switch_esc_token_count_before": len(switch_tokens),
        "ordinal_token_positions_preserved": True,
        "visible_stream_preserved": True,
    }


def load_target_catalog(repo_root: Path) -> dict[str, Any]:
    path = repo_root / TARGET_CATALOG_RELATIVE
    catalog, blob = common.load_json_strict(path)
    if catalog.get("schema") != "nobu16.kr.translation-target-keys.v0.1":
        raise RecoveryError("translation target catalog schema changed")
    if catalog.get("source_free") is not True or catalog.get("contains_source_text") is not False:
        raise RecoveryError("translation target catalog is not source-free")
    resources = catalog.get("resources")
    if not isinstance(resources, list):
        raise RecoveryError("translation target catalog has no resources")
    rows = [row for row in resources if row.get("path") == RESOURCE]
    if len(rows) != 1:
        raise RecoveryError("translation target catalog must have one PK msgev row")
    row = rows[0]
    ids = row.get("target_ids")
    if not isinstance(ids, list) or any(type(item) is not int for item in ids):
        raise RecoveryError("PK msgev target IDs are invalid")
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise RecoveryError("PK msgev target IDs are not sorted and unique")
    if len(ids) != EXPECTED_TARGET_COUNT or hash_json(ids) != EXPECTED_TARGET_IDS_SHA256:
        raise RecoveryError("PK msgev exact target set changed")
    if row.get("target_count") != EXPECTED_TARGET_COUNT:
        raise RecoveryError("PK msgev target count metadata changed")
    if row.get("target_keys_sha256") != EXPECTED_TARGET_IDS_SHA256:
        raise RecoveryError("PK msgev target hash metadata changed")
    return {
        "path": TARGET_CATALOG_RELATIVE.as_posix(),
        "sha256": sha256(blob),
        "entry_count": len(ids),
        "ids_sha256": hash_json(ids),
        "ids": set(ids),
    }


def _load_overlay_ids(path: Path) -> tuple[list[int], str, dict[str, Any]]:
    overlay, blob = common.load_json_strict(path)
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise RecoveryError(f"owner overlay targets another resource: {path}")
    ids = [int(entry["id"]) for entry in entries]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise RecoveryError(f"owner overlay IDs are not sorted and unique: {path}")
    return ids, sha256(blob), overlay


def validate_progress_catalog(progress_path: Path, repo_root: Path) -> dict[str, Any]:
    """Validate the pinned predecessors plus later disjoint successors.

    The actual self-registration state is deliberately not emitted, so an
    otherwise identical pre- and post-registration build is byte-identical.
    Later batches are validated and ignored for this historical derivation;
    otherwise every appended overlay would make its predecessors impossible
    to reproduce.
    """

    progress, _blob = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise RecoveryError("translation progress has no resources")
    rows = [row for row in resources if row.get("path") == RESOURCE]
    if len(rows) != 1:
        raise RecoveryError("translation progress must have one PK msgev row")
    patterns = rows[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise RecoveryError("PK msgev progress overlay_globs are invalid")

    prior_paths: list[str] = []
    prior_ids: list[int] = []
    successor_ids: set[int] = set()
    self_count = 0
    predecessor_boundary_seen = False
    self_path = repo_root / SELF_OVERLAY_LOGICAL_PATH
    self_ids, self_hash, self_overlay = _load_overlay_ids(self_path)
    if self_overlay.get("overlay_id") != BATCH_ID:
        raise RecoveryError("checked self overlay_id changed")
    if len(self_ids) != EXPECTED_SELECTED_COUNT or hash_json(self_ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise RecoveryError("checked self overlay ID set changed")
    if EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__" and self_hash != EXPECTED_OVERLAY_SHA256:
        raise RecoveryError("checked self overlay SHA-256 changed")
    selected_ids = set(self_ids)
    for pattern in patterns:
        resolved = sorted(repo_root.glob(pattern))
        if len(resolved) != 1:
            raise RecoveryError(
                f"progress overlay glob {pattern!r} resolved to {len(resolved)} files"
            )
        path = resolved[0]
        logical = path.relative_to(repo_root).as_posix()
        ids, blob_hash, overlay = _load_overlay_ids(path)
        if logical == SELF_OVERLAY_LOGICAL_PATH:
            if pattern != SELF_OVERLAY_LOGICAL_PATH:
                raise RecoveryError("self overlay must use its exact logical path")
            if overlay.get("overlay_id") != BATCH_ID:
                raise RecoveryError("self registration overlay_id changed")
            if len(ids) != EXPECTED_SELECTED_COUNT or hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
                raise RecoveryError("self registration ID set changed")
            if EXPECTED_OVERLAY_SHA256 != "__PIN_AFTER_GENERATION__" and blob_hash != EXPECTED_OVERLAY_SHA256:
                raise RecoveryError("self registration overlay SHA-256 changed")
            self_count += 1
            continue
        if predecessor_boundary_seen:
            if pattern != logical:
                raise RecoveryError("successor overlays must use exact logical paths")
            policy = overlay.get("distribution_policy")
            if not isinstance(policy, dict) or policy.get("contains_commercial_source_text") is not False or policy.get("contains_complete_game_resource") is not False:
                raise RecoveryError(f"successor overlay is not source-free: {logical}")
            overlap = selected_ids & set(ids)
            if overlap:
                raise RecoveryError(
                    f"successor overlay overlaps this batch at {min(overlap)}: {logical}"
                )
            duplicate = successor_ids & set(ids)
            if duplicate:
                raise RecoveryError(
                    f"successor overlays overlap at {min(duplicate)}: {logical}"
                )
            successor_ids.update(ids)
            continue
        prior_paths.append(logical)
        prior_ids.extend(ids)
        if logical == STRICT_OVERLAY_LOGICAL_PATH:
            predecessor_boundary_seen = True

    if self_count > 1:
        raise RecoveryError("self overlay is registered more than once")
    if not predecessor_boundary_seen:
        raise RecoveryError("strict predecessor boundary is absent from progress")
    if len(prior_paths) != EXPECTED_PRIOR_PROGRESS_PATH_COUNT:
        raise RecoveryError("prior msgev progress path count changed")
    if hash_json(prior_paths) != EXPECTED_PRIOR_PROGRESS_PATHS_SHA256:
        raise RecoveryError("prior msgev progress path order/set changed")
    if STRICT_OVERLAY_LOGICAL_PATH not in prior_paths:
        raise RecoveryError("strict 245-row predecessor is absent from progress")
    if len(prior_ids) != len(set(prior_ids)):
        raise RecoveryError("prior msgev owner overlays overlap")
    owner_ids = sorted(prior_ids)
    if len(owner_ids) != EXPECTED_PRIOR_OWNER_COUNT:
        raise RecoveryError("prior msgev owner count changed")
    if hash_json(owner_ids) != EXPECTED_PRIOR_OWNER_IDS_SHA256:
        raise RecoveryError("prior msgev owner ID set changed")
    successor_owner_overlap = successor_ids & set(owner_ids)
    if successor_owner_overlap:
        raise RecoveryError(
            f"successor overlay overlaps a pinned predecessor at {min(successor_owner_overlap)}"
        )
    strict_path = repo_root / STRICT_OVERLAY_LOGICAL_PATH
    strict_ids, strict_hash, _strict_overlay = _load_overlay_ids(strict_path)
    if strict_hash != STRICT_OVERLAY_SHA256:
        raise RecoveryError("strict 245-row predecessor SHA-256 changed")
    if len(strict_ids) != STRICT_OVERLAY_ENTRY_COUNT:
        raise RecoveryError("strict 245-row predecessor count changed")
    if hash_json(strict_ids) != STRICT_OVERLAY_IDS_SHA256:
        raise RecoveryError("strict 245-row predecessor IDs changed")
    return {
        "prior_overlay_path_count": len(prior_paths),
        "prior_overlay_paths_sha256": hash_json(prior_paths),
        "prior_owner_count": len(owner_ids),
        "prior_owner_ids_sha256": hash_json(owner_ids),
        "self_registration_states_allowed": ["absent", "one_exact_path"],
        "self_excluded_from_prior_owner_set": True,
        "ids": set(owner_ids),
    }


def derive_residual_pool(
    sources: dict[str, dict[str, Any]], owner_ids: set[int], target_ids: set[int]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pk_jp = sources["pk_jp"]["table"]
    pk_sc = sources["pk_sc_stock"]["table"]
    buckets = strict.exact_jp_buckets(sources)
    rows: list[dict[str, Any]] = []
    gate_source_script_ids: list[int] = []
    gate_invariant_ids: list[int] = []
    raw_script_ids: list[int] = []
    raw_invariant_ids: list[int] = []

    for entry_id in sorted(target_ids - owner_ids):
        jp = pk_jp.texts[entry_id]
        jp_hash = common.text_hash(jp)
        hash_rows = buckets.get(jp_hash, [])
        exact_rows = [row for row in hash_rows if row["jp"] == jp]
        if not exact_rows:
            continue
        if len(exact_rows) != len(hash_rows):
            raise RecoveryError("Japanese hash bucket contains mixed exact values")
        ko = strict.resolve_unique_meaningful_ko(exact_rows, jp)
        if ko is None:
            continue
        source_script = strict.upstream.contains_cjk_or_kana(ko)
        problems = common.invariant_mismatches(pk_sc.texts[entry_id], ko)
        if source_script:
            gate_source_script_ids.append(entry_id)
        elif problems:
            gate_invariant_ids.append(entry_id)
        else:
            continue
        if source_script:
            raw_script_ids.append(entry_id)
        if problems:
            raw_invariant_ids.append(entry_id)
        rows.append(
            {
                "id": entry_id,
                "jp_hash": jp_hash,
                "sc": pk_sc.texts[entry_id],
                "ko": ko,
                "base_jp_coordinate_ids": sorted(
                    int(row["coordinate"]) for row in exact_rows
                ),
                "source_script": source_script,
                "invariant_problem_keys": [
                    problem.split(":", 1)[0] for problem in problems
                ],
            }
        )

    ids = [int(row["id"]) for row in rows]
    if len(ids) != EXPECTED_RESIDUAL_COUNT or hash_json(ids) != EXPECTED_RESIDUAL_IDS_SHA256:
        raise RecoveryError("261-row residual pool changed")
    if gate_source_script_ids != list(EXPECTED_GATE_SOURCE_SCRIPT_IDS):
        raise RecoveryError("source-script gate ID set changed")
    if hash_json(gate_source_script_ids) != EXPECTED_GATE_SOURCE_SCRIPT_IDS_SHA256:
        raise RecoveryError("source-script gate ID hash changed")
    if len(gate_invariant_ids) != EXPECTED_GATE_INVARIANT_COUNT:
        raise RecoveryError("invariant gate count changed")
    if hash_json(gate_invariant_ids) != EXPECTED_GATE_INVARIANT_IDS_SHA256:
        raise RecoveryError("invariant gate ID set changed")
    if len(raw_script_ids) != 4 or len(raw_invariant_ids) != 261:
        raise RecoveryError("raw residual predicate counts changed")
    if set(raw_script_ids) - set(raw_invariant_ids):
        raise RecoveryError("source-script residual is no longer inside raw invariant set")
    summary = {
        "residual_count": len(ids),
        "residual_ids_sha256": hash_json(ids),
        "upstream_precedence_gate_classes": {
            "source_script": len(gate_source_script_ids),
            "sc_invariant_after_source_script_gate": len(gate_invariant_ids),
            "class_overlap_count": 0,
            "class_union_count": len(ids),
        },
        "raw_predicates_on_full_residual": {
            "source_script_count": len(raw_script_ids),
            "sc_invariant_mismatch_count": len(raw_invariant_ids),
            "intersection_count": len(set(raw_script_ids) & set(raw_invariant_ids)),
            "union_count": len(set(raw_script_ids) | set(raw_invariant_ids)),
        },
    }
    return rows, summary


def repair_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    source_sc = str(row["sc"])
    original_ko = str(row["ko"])
    repaired = original_ko
    operations: list[str] = []
    details: dict[str, Any] = {}

    source_brackets = strict.upstream.BRACKET_TOKEN_RE.findall(source_sc)
    switch_brackets = strict.upstream.BRACKET_TOKEN_RE.findall(original_ko)
    if source_brackets != switch_brackets:
        raise RecoveryError("custom bracket token sequence differs")

    if strict.upstream.contains_cjk_or_kana(repaired):
        source_chars = [
            character
            for character in repaired
            if strict.upstream.contains_cjk_or_kana(character)
        ]
        if not source_chars or any(character != MIDDLE_DOT_JP for character in source_chars):
            raise RecoveryError("source-script residual is not middle-dot-only")
        repaired = repaired.replace(MIDDLE_DOT_JP, MIDDLE_DOT_KO)
        operations.append("middle_dot_normalization")
        details["middle_dot_count"] = len(source_chars)

    source_invariants = common.message_invariants(source_sc)
    repaired_invariants = common.message_invariants(repaired)
    if source_invariants["esc"] != repaired_invariants["esc"]:
        repaired, esc_details = replace_esc_tokens_ordinally(source_sc, repaired)
        operations.append("esc_token_template")
        details["esc_token_template"] = esc_details

    repaired_invariants = common.message_invariants(repaired)
    if source_invariants["line_breaks"] != repaired_invariants["line_breaks"]:
        repaired, break_details = restore_line_break_template(source_sc, repaired)
        operations.append("line_break_template")
        details["line_break_template"] = break_details

    repaired_invariants = common.message_invariants(repaired)
    if source_invariants["trailing_whitespace"] != repaired_invariants["trailing_whitespace"]:
        if repaired_invariants["trailing_whitespace"]:
            raise RecoveryError("Switch Korean has non-empty incompatible trailing whitespace")
        repaired += source_invariants["trailing_whitespace"]
        operations.append("trailing_whitespace_template")
        details["trailing_whitespace_code_unit_count"] = len(
            source_invariants["trailing_whitespace"]
        )

    if not operations:
        raise RecoveryError("residual row needed no explicit repair")
    if canonical_visible_stream(repaired) != canonical_visible_stream(original_ko):
        raise RecoveryError("repair changed visible text or word-boundary order")
    problems_after = common.invariant_mismatches(source_sc, repaired)
    if problems_after:
        raise RecoveryError(f"repair did not restore SC invariants: {problems_after}")
    if strict.upstream.BRACKET_TOKEN_RE.findall(repaired) != source_brackets:
        raise RecoveryError("repair changed custom bracket tokens")
    if strict.upstream.contains_cjk_or_kana(repaired):
        raise RecoveryError("repair retains CJK unified or kana")
    if not strict.upstream.has_meaningful_hangul(repaired):
        raise RecoveryError("repair lacks meaningful Hangul")
    return repaired, {
        "operations": operations,
        "operation_combination": "+".join(operations),
        "visible_stream_preserved": True,
        "word_boundary_order_preserved": True,
        "pk_sc_invariants_preserved": True,
        "custom_bracket_tokens_preserved": True,
        "source_script_free": True,
        **details,
    }


def select_entries(
    rows: list[dict[str, Any]], owner_ids: set[int], target_ids: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    combination_counts: Counter[str] = Counter()
    operation_counts: Counter[str] = Counter()

    for row in rows:
        entry_id = int(row["id"])
        source_sc = str(row["sc"])
        switch_ko = str(row["ko"])
        source_esc = common.message_invariants(source_sc)["esc"]
        switch_esc = common.message_invariants(switch_ko)["esc"]
        source_brackets = strict.upstream.BRACKET_TOKEN_RE.findall(source_sc)
        switch_brackets = strict.upstream.BRACKET_TOKEN_RE.findall(switch_ko)
        reasons: list[str] = []
        if len(source_esc) != len(switch_esc):
            reasons.append("esc_token_count_mismatch_requires_segment_mapping")
        if source_brackets != switch_brackets:
            reasons.append("custom_bracket_sequence_mismatch_requires_fragment_mapping")
        if reasons:
            exclusions.append(
                {
                    "id": entry_id,
                    "reasons": reasons,
                    "stock_visible_target": True,
                    "automatic_repair_safe": False,
                    "sentence_or_placeholder_rearrangement_performed": False,
                }
            )
            continue

        repaired, repair = repair_row(row)
        source_coordinates = list(row["base_jp_coordinate_ids"])
        selected.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": repaired,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "pk_jp_utf16le_sha256": row["jp_hash"],
                "base_jp_utf16le_sha256": row["jp_hash"],
                "pk_sc_utf16le_sha256": common.text_hash(source_sc),
                "switch_ko_before_utf16le_sha256": common.text_hash(switch_ko),
                "repaired_ko_utf16le_sha256": common.text_hash(repaired),
                "canonical_visible_stream_utf16le_sha256": common.text_hash(
                    canonical_visible_stream(repaired)
                ),
                "base_jp_coordinate_count": len(source_coordinates),
                "base_jp_coordinate_ids_sha256": hash_json(source_coordinates),
                "exact_japanese_hash_and_in_memory_equality": True,
                "unique_meaningful_switch_korean": True,
                "stock_visible_target": True,
                **repair,
            }
        )
        combination_counts[repair["operation_combination"]] += 1
        operation_counts.update(repair["operations"])

    selected_ids = [int(entry["id"]) for entry in selected]
    excluded_ids = [int(entry["id"]) for entry in exclusions]
    if len(selected_ids) != EXPECTED_SELECTED_COUNT:
        raise RecoveryError("safe selected count changed")
    if hash_json(selected_ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise RecoveryError("safe selected ID set changed")
    if excluded_ids != list(EXPECTED_EXCLUDED_IDS):
        raise RecoveryError("honest exclusion ID set changed")
    if hash_json(excluded_ids) != EXPECTED_EXCLUDED_IDS_SHA256:
        raise RecoveryError("honest exclusion ID hash changed")
    if dict(combination_counts) != EXPECTED_OPERATION_COMBINATIONS:
        raise RecoveryError("operation combination histogram changed")
    if dict(operation_counts) != EXPECTED_OPERATION_CLASS_COUNTS:
        raise RecoveryError("operation class histogram changed")
    if set(selected_ids) & owner_ids:
        raise RecoveryError("selected IDs overlap prior owners")
    if not set(selected_ids).issubset(target_ids):
        raise RecoveryError("selected IDs are outside the exact target catalog")
    if set(selected_ids) & set(excluded_ids):
        raise RecoveryError("selected and excluded IDs overlap")
    if set(selected_ids) | set(excluded_ids) != {int(row["id"]) for row in rows}:
        raise RecoveryError("selected/excluded partition does not cover the residual")

    class_summary = {
        "selected_count": len(selected_ids),
        "selected_ids_sha256": hash_json(selected_ids),
        "excluded_count": len(excluded_ids),
        "excluded_ids_sha256": hash_json(excluded_ids),
        "operation_class_counts": dict(operation_counts),
        "operation_combination_counts": dict(combination_counts),
        "exclusion_classes": {
            "esc_token_count_mismatch": {
                "count": len(ESC_COUNT_EXCLUSION_IDS),
                "ids_sha256": ESC_COUNT_EXCLUSION_IDS_SHA256,
            },
            "custom_bracket_sequence_mismatch": {
                "count": len(BRACKET_EXCLUSION_IDS),
                "ids_sha256": BRACKET_EXCLUSION_IDS_SHA256,
            },
            "class_intersection": {
                "count": len(EXCLUSION_CLASS_OVERLAP_IDS),
                "ids_sha256": EXCLUSION_CLASS_OVERLAP_IDS_SHA256,
            },
            "class_union": {
                "count": len(excluded_ids),
                "ids_sha256": hash_json(excluded_ids),
            },
        },
        "selected_prior_owner_overlap_count": 0,
        "selected_target_catalog_intersection_count": len(selected_ids),
        "selected_outside_target_count": 0,
    }
    return selected, evidence_entries, exclusions, class_summary


def input_snapshot(
    game_root: Path, repo_root: Path, archive_path: Path, progress_path: Path
) -> dict[str, str]:
    values = strict.input_snapshot(game_root, repo_root, archive_path)
    values.update(
        {
            "strict_245_overlay": sha256(
                (repo_root / STRICT_OVERLAY_LOGICAL_PATH).read_bytes()
            ),
            "target_catalog": sha256(
                (repo_root / TARGET_CATALOG_RELATIVE).read_bytes()
            ),
            "progress_catalog": sha256(progress_path.read_bytes()),
        }
    )
    return values


def build_once(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    before = input_snapshot(game_root, repo_root, archive_path, progress_path)
    sources = strict.load_sources(game_root, repo_root, archive_path)
    owners = validate_progress_catalog(progress_path, repo_root)
    target = load_target_catalog(repo_root)
    rows, residual = derive_residual_pool(sources, owners["ids"], target["ids"])
    entries, evidence_entries, exclusions, selection = select_entries(
        rows, owners["ids"], target["ids"]
    )

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
            key: strict.upstream.SOURCE_PINS["pk_sc_stock"][key]
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
    rebuilt_a = strict.upstream.reconstruct_pk_sc_target(
        sources["pk_sc_stock"], entries
    )
    rebuilt_b = strict.upstream.reconstruct_pk_sc_target(
        sources["pk_sc_stock"], entries
    )
    if rebuilt_a != rebuilt_b:
        raise RecoveryError("in-memory PK SC target reconstruction is not deterministic")

    progress_policy = {
        key: value for key, value in owners.items() if key != "ids"
    }
    target_snapshot = {key: value for key, value in target.items() if key != "ids"}
    source_pin = dict(strict.upstream.SOURCE_PINS["switch_ko"])
    source_pin["logical_path"] = f"ZIP!/{strict.SWITCH_ENTRY}"
    switch_identity = {
        "v13_member_packed_sha256": source_pin["packed_sha256"],
        "v13_member_raw_sha256": source_pin["raw_sha256"],
        "v11_member_packed_sha256": strict.V11_TEXT_MEMBER["packed_sha256"],
        "v11_member_raw_sha256": strict.V11_TEXT_MEMBER["raw_sha256"],
        "v13_is_byte_identical_to_v11": True,
    }
    evidence = {
        "schema": "nobu16.kr.switch-msgev-v13-invariant-recovery-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "source_release": strict.SWITCH_RELEASE,
        "switch_text_identity": switch_identity,
        "source_files": {
            "switch_v13_ko": source_pin,
            "base_jp": dict(strict.upstream.SOURCE_PINS["base_jp"]),
            "pk_jp": dict(strict.upstream.SOURCE_PINS["pk_jp"]),
            "pk_sc_stock": dict(strict.upstream.SOURCE_PINS["pk_sc_stock"]),
        },
        "selection_method": [
            "start_from_the_exact_261_row_strict_recovery_residual",
            "require_exact_japanese_hash_then_in_memory_equality",
            "require_one_converged_meaningful_switch_korean_value",
            "require_membership_in_the_source_free_exact_target_catalog",
            "exclude_every_prior_owner_including_the_245_row_predecessor",
            "normalize_only_japanese_middle_dot_to_korean_middle_dot",
            "restore_equal_length_esc_tokens_ordinally_without_moving_positions",
            "restore_line_break_types_on_existing_whitespace_boundaries_only",
            "restore_missing_trailing_whitespace_from_the_sc_contract",
            "preserve_the_canonical_visible_stream_and_word_boundary_order",
            "exclude_esc_count_or_custom_bracket_sequence_mismatches",
            "never_rearrange_sentence_fragments_or_placeholders",
        ],
        "progress_integration_policy": progress_policy,
        "target_catalog": target_snapshot,
        "residual_pool": residual,
        "selection": selection,
        "entry_count": len(entries),
        "selected_ids_sha256": hash_json([entry["id"] for entry in entries]),
        "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.switch-msgev-v13-invariant-recovery-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "quality_state": "mechanically_repaired_pending_pc_runtime_review",
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "summary": {
            "residual_candidate_count": len(rows),
            "translated_count": len(entries),
            "excluded_count": len(exclusions),
            "runtime_reviewed_count": 0,
        },
        "entries": [
            {
                "id": entry["id"],
                "status": "translated",
                "translation_origin": "switch_v1.3_text_equals_v1.1_invariant_recovery",
                "human_review_required": True,
                "runtime_reviewed": False,
                "stock_visible_target": True,
                "visible_stream_and_word_boundary_order_preserved": True,
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
            }
            for entry in evidence_entries
        ],
        "exclusions": exclusions,
    }

    values = {
        f"public/{OVERLAY_NAME}": overlay,
        f"evidence/{EVIDENCE_NAME}": evidence,
        f"review/{REVIEW_NAME}": review,
    }
    files = {relative: encode_json(value) for relative, value in values.items()}
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    source_free_scan = {
        relative: source_free_counts(blob) for relative, blob in files.items()
    }
    if any(scan != expected_scan for scan in source_free_scan.values()):
        raise RecoveryError("a generated public artifact contains source script")
    artifacts = {
        relative: artifact_metadata(relative, blob) for relative, blob in files.items()
    }
    validation = {
        "schema": "nobu16.kr.switch-msgev-v13-invariant-recovery-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "entry_count": len(entries),
        "selected_ids_sha256": hash_json([entry["id"] for entry in entries]),
        "source_release": strict.SWITCH_RELEASE,
        "switch_text_identity": switch_identity,
        "progress_integration_policy": progress_policy,
        "target_catalog": target_snapshot,
        "residual_pool": residual,
        "selection": selection,
        "replacement_invariants": {
            "checked": len(entries),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_and_trailing_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_tokens",
            ],
            "canonical_visible_stream_preserved_count": len(entries),
            "word_boundary_order_preserved_count": len(entries),
            "sentence_fragment_rearrangement_count": 0,
            "placeholder_rearrangement_count": 0,
        },
        "reconstruction": {
            "complete_target_included": False,
            "changed_entry_count": rebuilt_a["changed_entry_count"],
            "target": rebuilt_a,
            "in_memory_a_b_equal": True,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "pre_and_post_self_registration_must_be_byte_identical": True,
        },
        "safety": {
            "switch_archive_extracted": False,
            "complete_game_resource_emitted": False,
            "installed_game_files_modified": False,
            "base_msg_sc_modified": False,
            "font_files_modified": False,
            "root_readme_or_progress_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
        },
    }
    validation_blob = encode_json(validation)
    if source_free_counts(validation_blob) != expected_scan:
        raise RecoveryError("generated validation contains source script")
    files[VALIDATION_NAME] = validation_blob

    out_root = out_root.resolve()
    for relative, blob in files.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    after = input_snapshot(game_root, repo_root, archive_path, progress_path)
    if before != after:
        raise RecoveryError("a read-only input changed while building")
    return {
        "entry_count": len(entries),
        "excluded_count": len(exclusions),
        "selected_ids_sha256": selection["selected_ids_sha256"],
        "excluded_ids_sha256": selection["excluded_ids_sha256"],
        "target": rebuilt_a,
        "files": files,
    }


def build_reproducibly(
    game_root: Path,
    repo_root: Path,
    archive_path: Path,
    progress_path: Path,
    out_root: Path,
) -> dict[str, Any]:
    game_root = game_root.resolve()
    repo_root = repo_root.resolve()
    archive_path = archive_path.resolve()
    progress_path = progress_path.resolve()
    out_root = out_root.resolve()
    before = input_snapshot(game_root, repo_root, archive_path, progress_path)
    with tempfile.TemporaryDirectory(prefix="nobu16-msgev-invariant-a-") as first_dir:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-invariant-b-") as second_dir:
            first = build_once(
                game_root, repo_root, archive_path, progress_path, Path(first_dir)
            )
            second = build_once(
                game_root, repo_root, archive_path, progress_path, Path(second_dir)
            )
            if first["files"] != second["files"]:
                raise RecoveryError("isolated builds are not byte-identical")
    final = build_once(game_root, repo_root, archive_path, progress_path, out_root)
    if final["files"] != first["files"]:
        raise RecoveryError("final build differs from isolated build")
    after = input_snapshot(game_root, repo_root, archive_path, progress_path)
    if before != after:
        raise RecoveryError("a read-only input changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=REPO_ROOT / strict.SWITCH_ARCHIVE_RELATIVE
    )
    parser.add_argument(
        "--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root,
            args.repo_root,
            args.archive,
            args.progress,
            args.out_root,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print(f"excluded={result['excluded_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"excluded_ids_sha256={result['excluded_ids_sha256']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
