#!/usr/bin/env python3
"""Create a PC-only closure ledger for the two core msggame resources.

The output is deliberately a coverage and disposition ledger, not a claim that
mechanical signals prove a Korean translation's semantics.  Each coordinate is
paired with the pinned pristine PC Japanese original and available PC-language
context.  Switch Korean and historic Korean text are never opened.

All source-bearing evidence is private below ``tmp``.  This script only reads
the Steam installation and never writes a game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_ORIGINAL_ROOT = (
    DEFAULT_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
DEFAULT_OUTPUT_ROOT = TMP / "translation_quality_core_msggame_closure_v1"
INVENTORY_SCRIPT = REPO / "workstreams" / "translation_quality_audit_v1" / "build_semantic_review_inventory_v1.py"
FROZEN_OVERLAY = (
    REPO
    / "workstreams"
    / "translation_quality_corrections_v1"
    / "public"
    / "translation_quality_corrections.v1.json"
)


class ClosureError(ValueError):
    """A baseline or audit-contract violation."""


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative_path: str
    pc_context_languages: tuple[str, ...]


SPECS = (
    ResourceSpec("base_msggame", "MSG/JP/msggame.bin", ("SC", "TC")),
    ResourceSpec("pk_msggame", "MSG_PK/JP/msggame.bin", ("EN", "SC", "TC")),
)

# These short source-side terms only prioritize manual semantic review.  They
# do not authorize an automatic rewrite and do not contain a game sentence.
RISK_MARKERS: Mapping[str, tuple[str, ...]] = {
    "administration_or_feudal_relation": ("知行", "所領", "陪臣", "家督", "養子", "隠居"),
    "war_outcome_or_capture": ("討死", "戦死", "落城", "降伏", "攻落", "捕縛"),
    "intrigue_or_defection": ("調略", "内応", "寝返り", "謀反", "離反", "出奔"),
    "office_or_rank": ("官位", "奉行", "宿老", "当主"),
    "negotiation_or_territory": ("仲介", "本拠", "領国", "要所", "城下"),
}

JP_PUNCTUATION_RE = re.compile(r"[、。]")


def load_inventory_module() -> Any:
    module_spec = importlib.util.spec_from_file_location("core_msggame_closure_inventory", INVENTORY_SCRIPT)
    if module_spec is None or module_spec.loader is None:
        raise ClosureError(f"cannot load PC-only inventory helper: {INVENTORY_SCRIPT}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module


INVENTORY = load_inventory_module()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_json(value: object) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest().upper()


def safe_under_tmp(path: Path) -> Path:
    root = TMP.resolve()
    resolved = path.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise ClosureError(f"output must remain below {root}: {resolved}")
    return resolved


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def deterministic_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def language_path(relative_path: str, language: str) -> Path:
    return INVENTORY.language_path(relative_path, language)


def coordinate_key(value: str) -> tuple[int, ...]:
    return INVENTORY.coordinate_sort_key(value)


def source_path_for(spec: ResourceSpec, original_root: Path) -> Path:
    inventory_spec = next(item for item in INVENTORY.SPECS if item.name == spec.name)
    return INVENTORY.source_path_for(inventory_spec, original_root)


def parse_msggame(path: Path) -> dict[str, str]:
    return INVENTORY.parse_msggame(path)


def source_risk_categories(source_jp: str) -> list[str]:
    return [category for category, markers in RISK_MARKERS.items() if any(marker in source_jp for marker in markers)]


def overlay_entries() -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any]]:
    if not FROZEN_OVERLAY.is_file():
        raise ClosureError(f"frozen PC-only overlay is missing: {FROZEN_OVERLAY}")
    payload = json.loads(FROZEN_OVERLAY.read_text(encoding="utf-8"))
    policy = payload.get("distribution_policy")
    if not isinstance(policy, dict) or policy.get("switch_korean_translation_used") is not False:
        raise ClosureError("frozen overlay does not assert a Switch-free policy")
    if policy.get("contains_commercial_source_text") is not False:
        raise ClosureError("frozen overlay unexpectedly contains source text")
    by_relative: dict[str, dict[str, dict[str, Any]]] = {}
    for resource in payload.get("resources", []):
        if not isinstance(resource, dict):
            raise ClosureError("invalid frozen overlay resource")
        baseline = resource.get("baseline")
        entries = resource.get("entries")
        if not isinstance(baseline, dict) or not isinstance(entries, list):
            raise ClosureError("invalid frozen overlay baseline or entries")
        relative = baseline.get("relative_path")
        if not isinstance(relative, str):
            raise ClosureError("frozen overlay resource lacks relative path")
        if relative in by_relative:
            raise ClosureError(f"duplicate frozen overlay resource: {relative}")
        row_by_coordinate: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise ClosureError(f"invalid frozen overlay entry: {relative}")
            coordinate = entry.get("coordinate")
            if not isinstance(coordinate, str) or coordinate in row_by_coordinate:
                raise ClosureError(f"invalid or duplicate frozen overlay coordinate: {relative}")
            for required in ("source_current_utf16le_sha256", "ko_utf16le_sha256", "ko"):
                if not isinstance(entry.get(required), str):
                    raise ClosureError(f"frozen overlay entry lacks {required}: {relative}:{coordinate}")
            if INVENTORY.sha256_text(entry["ko"]) != entry["ko_utf16le_sha256"]:
                raise ClosureError(f"frozen overlay proposed-text hash drift: {relative}:{coordinate}")
            row_by_coordinate[coordinate] = entry
        by_relative[relative] = {
            "entries": row_by_coordinate,
            "baseline_packed_sha256": baseline.get("packed_sha256"),
        }
    needed = {spec.relative_path for spec in SPECS}
    missing = needed.difference(by_relative)
    if missing:
        raise ClosureError(f"frozen overlay does not cover core resources: {sorted(missing)}")
    metadata = {
        "overlay_sha256": sha256_file(FROZEN_OVERLAY),
        "overlay_id": payload.get("overlay_id"),
        "switch_korean_translation_used": False,
        "read_for_status_only_not_semantic_source": True,
    }
    return by_relative, metadata


def inconsistent_source_coordinates(jp_rows: Mapping[str, str], ko_rows: Mapping[str, str]) -> set[str]:
    renderings: dict[str, set[str]] = defaultdict(set)
    coordinates: dict[str, list[str]] = defaultdict(list)
    for coordinate, source in jp_rows.items():
        if len(source.strip()) < 2:
            continue
        renderings[source].add(ko_rows[coordinate])
        coordinates[source].append(coordinate)
    result: set[str] = set()
    for source, values in renderings.items():
        if len(values) > 1:
            result.update(coordinates[source])
    return result


def overlay_state(entry: Mapping[str, Any], current_ko: str) -> str:
    current_hash = INVENTORY.sha256_text(current_ko)
    if current_hash == entry["source_current_utf16le_sha256"]:
        return "pending_in_current_steam_target"
    if current_hash == entry["ko_utf16le_sha256"]:
        return "already_applied_to_current_steam_target"
    return "baseline_drift_requires_rebase"


def classify(
    *,
    source_jp: str,
    current_ko: str,
    contexts: Mapping[str, str],
    expected_context_languages: tuple[str, ...],
    duplicate_source_coordinate: bool,
    frozen_entry: Mapping[str, Any] | None,
) -> tuple[str, str, str, list[str], list[str]]:
    """Return honest, mutually exclusive disposition fields.

    The final category intentionally does not infer semantic correctness from
    the absence of a machine-detectable signal.
    """
    flags = INVENTORY.review_flags(source_jp, current_ko, dict(contexts))
    risk_categories = source_risk_categories(source_jp)
    if duplicate_source_coordinate:
        flags.append("same_pristine_jp_multiple_current_ko")
    missing_contexts = [language for language in expected_context_languages if language not in contexts]
    if missing_contexts:
        flags.append("partial_pc_context_coordinate")
    if JP_PUNCTUATION_RE.search(current_ko):
        # This is intentionally observational: Japanese-style punctuation is
        # common in dialogue and no blanket normalization is safe.
        flags.append("japanese_style_punctuation_observed_not_auto_rewritten")

    if frozen_entry is not None:
        state = overlay_state(frozen_entry, current_ko)
        if state == "baseline_drift_requires_rebase":
            return (
                "hold_frozen_pc_only_correction_baseline_drift",
                "frozen coordinate no longer matches either guarded current or guarded proposal hash",
                "manual_rebase_required",
                sorted(set(flags)),
                risk_categories,
            )
        return (
            "frozen_pc_only_correction_status_recorded",
            state,
            "previous_pc_only_correction_exists_not_rejudged_here",
            sorted(set(flags)),
            risk_categories,
        )

    fatal_format_flags = {
        "runtime_token_mismatch_against_pristine_jp",
        "printf_token_mismatch_against_pristine_jp",
        "escape_tag_mismatch_against_pristine_jp",
        "empty_target_for_nonempty_jp",
    }
    residual_flags = {"target_kana_residual", "target_han_residual"}
    placeholder_flags = {
        "target_dummy_placeholder_for_nonempty_jp",
        "target_localization_identifier_for_nonempty_jp",
    }
    if fatal_format_flags.intersection(flags):
        return (
            "hold_format_or_empty_target_integrity",
            "runtime/printf/escape/empty target condition requires manual runtime-aware review",
            "manual_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    if residual_flags.intersection(flags):
        return (
            "hold_non_korean_script_residual",
            "residual kana/han needs contextual confirmation before any rewrite",
            "manual_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    if placeholder_flags.intersection(flags):
        return (
            "hold_internal_placeholder_or_identifier",
            "possible non-display/internal slot; do not translate automatically",
            "manual_display_and_semantic_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    if {
        "linebreak_count_mismatch_against_pristine_jp",
        "external_whitespace_mismatch_against_pristine_jp",
    }.intersection(flags):
        return (
            "hold_layout_or_boundary_difference",
            "layout/boundary difference requires rendered UI review, not automatic normalization",
            "runtime_or_layout_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    if duplicate_source_coordinate:
        return (
            "review_same_pristine_jp_multiple_current_ko_renderings",
            "same source has multiple current Korean renderings; context may justify it",
            "terminology_consistency_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    if missing_contexts:
        return (
            "review_partial_pc_context_coverage",
            "one or more expected PC EN/SC/TC coordinate contexts are absent",
            "manual_semantic_review_with_pristine_jp_required",
            sorted(set(flags)),
            risk_categories,
        )
    if risk_categories:
        return (
            "review_source_semantic_risk_marker",
            "source contains a domain term whose Korean rendering needs direct semantic review",
            "manual_semantic_review_required",
            sorted(set(flags)),
            risk_categories,
        )
    return (
        "pc_paired_mechanical_clear_no_semantic_verdict",
        "pristine PC JP and available PC references are paired; no automatic semantic conclusion is drawn",
        "not_automatically_semantically_adjudicated",
        sorted(set(flags)),
        risk_categories,
    )


def build_rows(steam_root: Path, original_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    steam_root = steam_root.resolve()
    original_root = original_root.resolve()
    overlays, overlay_metadata = overlay_entries()

    all_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    resource_summaries: dict[str, Any] = {}

    for spec in SPECS:
        live_path = steam_root / spec.relative_path
        pristine_path = source_path_for(spec, original_root)
        if not live_path.is_file() or not pristine_path.is_file():
            raise ClosureError(f"missing PC target/source pair for {spec.name}")
        current_file_sha256 = sha256_file(live_path)
        pristine_file_sha256 = sha256_file(pristine_path)
        expected_pristine = INVENTORY.PRISTINE_JP_SHA256[spec.relative_path]
        if pristine_file_sha256 != expected_pristine:
            raise ClosureError(
                f"pristine PC Japanese hash differs for {spec.name}: expected {expected_pristine}, got {pristine_file_sha256}"
            )
        frozen_resource = overlays[spec.relative_path]
        if current_file_sha256 != frozen_resource["baseline_packed_sha256"]:
            raise ClosureError(f"current Steam target baseline drifted for {spec.name}; rebase before audit")

        jp_rows = parse_msggame(pristine_path)
        ko_rows = parse_msggame(live_path)
        if set(jp_rows) != set(ko_rows):
            raise ClosureError(f"coordinate mismatch between pristine JP and current PC Korean: {spec.name}")

        context_tables: dict[str, dict[str, str]] = {}
        context_file_hashes: dict[str, str] = {}
        for language in spec.pc_context_languages:
            context_path = steam_root / language_path(spec.relative_path, language)
            if not context_path.is_file():
                raise ClosureError(f"missing required PC {language} context file for {spec.name}: {context_path}")
            context_tables[language] = parse_msggame(context_path)
            context_file_hashes[language] = sha256_file(context_path)

        duplicate_coordinates = inconsistent_source_coordinates(jp_rows, ko_rows)
        frozen_entries = frozen_resource["entries"]
        unknown_frozen = set(frozen_entries).difference(ko_rows)
        if unknown_frozen:
            raise ClosureError(f"frozen correction coordinates absent from current {spec.name}: {sorted(unknown_frozen, key=coordinate_key)}")

        resource_rows: list[dict[str, Any]] = []
        for coordinate in sorted(ko_rows, key=coordinate_key):
            source_jp = jp_rows[coordinate]
            current_ko = ko_rows[coordinate]
            contexts = {
                language: rows[coordinate]
                for language, rows in context_tables.items()
                if coordinate in rows
            }
            frozen_entry = frozen_entries.get(coordinate)
            disposition, detail, semantic_status, flags, risks = classify(
                source_jp=source_jp,
                current_ko=current_ko,
                contexts=contexts,
                expected_context_languages=spec.pc_context_languages,
                duplicate_source_coordinate=coordinate in duplicate_coordinates,
                frozen_entry=frozen_entry,
            )
            row = {
                "schema": "nobu16.kr.core-msggame-pc-only-closure.v1",
                "resource": spec.name,
                "coordinate": coordinate,
                "disposition": disposition,
                "disposition_detail": detail,
                "semantic_status": semantic_status,
                "mechanical_review_flags": flags,
                "source_risk_categories": risks,
                "source_jp": source_jp,
                "source_jp_utf16le_sha256": INVENTORY.sha256_text(source_jp),
                "current_ko": current_ko,
                "current_ko_utf16le_sha256": INVENTORY.sha256_text(current_ko),
                "pc_reference_contexts": contexts,
                "pc_reference_coverage": {
                    "expected_languages": list(spec.pc_context_languages),
                    "available_languages": sorted(contexts),
                    "missing_languages": [language for language in spec.pc_context_languages if language not in contexts],
                },
                "pristine_jp_file_sha256": pristine_file_sha256,
                "current_pc_ko_file_sha256": current_file_sha256,
                "pc_reference_file_sha256": context_file_hashes,
                "frozen_pc_only_overlay_status": (
                    overlay_state(frozen_entry, current_ko) if frozen_entry is not None else "not_a_frozen_overlay_coordinate"
                ),
                "audit_scope": {
                    "pristine_pc_japanese": True,
                    "current_pc_korean": True,
                    "pc_en_sc_tc_context_only": True,
                    "switch_korean_read": False,
                    "historic_korean_read": False,
                    "frozen_overlay_read_for_status_only": True,
                    "steam_game_resource_written": False,
                },
            }
            resource_rows.append(row)
            if disposition.startswith("hold_") or disposition.startswith("review_"):
                hold_rows.append(row)
        all_rows.extend(resource_rows)
        resource_summaries[spec.name] = {
            "relative_path": spec.relative_path,
            "coordinate_count": len(resource_rows),
            "pristine_pc_jp_file_sha256": pristine_file_sha256,
            "current_pc_ko_file_sha256": current_file_sha256,
            "pc_reference_file_sha256": context_file_hashes,
            "frozen_pc_only_correction_coordinate_count": len(frozen_entries),
            "duplicate_source_coordinate_count": len(duplicate_coordinates),
            "disposition_counts": dict(sorted(Counter(row["disposition"] for row in resource_rows).items())),
        }

    summary = {
        "schema": "nobu16.kr.core-msggame-pc-only-closure-summary.v1",
        "scope": "base_msggame and pk_msggame only; every current PC Korean coordinate paired with pinned pristine PC Japanese and available PC EN/SC/TC context",
        "resource_count": len(SPECS),
        "coordinate_count": len(all_rows),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in all_rows).items())),
        "semantic_status_counts": dict(sorted(Counter(row["semantic_status"] for row in all_rows).items())),
        "hold_or_review_count": len(hold_rows),
        "new_high_confidence_candidate_count": len(candidate_rows),
        "automatic_semantic_completion_claim": False,
        "reason_automatic_semantic_completion_claim_is_false": "mechanical/coverage dispositions do not replace human semantic adjudication",
        "frozen_overlay": overlay_metadata,
        "resources": resource_summaries,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_installation_written": False,
    }
    return all_rows, candidate_rows, hold_rows, summary


def validate_rows(
    rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    holds: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    expected_by_resource = {"base_msggame": 24262, "pk_msggame": 29524}
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_resource[row["resource"]].append(row)
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ClosureError("closure ledger scope is no longer PC-only/read-only")
        if row["semantic_status"] == "not_automatically_semantically_adjudicated" and row["disposition"] != "pc_paired_mechanical_clear_no_semantic_verdict":
            raise ClosureError("automatic-semantic status must be limited to the explicit non-verdict disposition")
    if set(by_resource) != set(expected_by_resource):
        raise ClosureError(f"closure resource set differs: {sorted(by_resource)}")
    for resource, expected_count in expected_by_resource.items():
        resource_rows = by_resource[resource]
        if len(resource_rows) != expected_count:
            raise ClosureError(f"{resource}: expected {expected_count} rows, got {len(resource_rows)}")
        coordinates = [row["coordinate"] for row in resource_rows]
        if len(coordinates) != len(set(coordinates)):
            raise ClosureError(f"{resource}: coordinate appears more than once")
    if len(rows) != sum(expected_by_resource.values()):
        raise ClosureError("core msggame full-audit coordinate sum differs")
    expected_holds = [row for row in rows if row["disposition"].startswith("hold_") or row["disposition"].startswith("review_")]
    if [row["resource"] + ":" + row["coordinate"] for row in holds] != [
        row["resource"] + ":" + row["coordinate"] for row in expected_holds
    ]:
        raise ClosureError("hold/review projection differs from full closure ledger")
    if candidates:
        raise ClosureError("this coverage-only pass must not emit an unvalidated automatic candidate")
    if summary.get("coordinate_count") != len(rows) or summary.get("hold_or_review_count") != len(holds):
        raise ClosureError("summary count differs from closure ledger")
    if summary.get("automatic_semantic_completion_claim") is not False:
        raise ClosureError("closure ledger must not claim automatic semantic completion")


def output_paths(output_root: Path) -> dict[str, Path]:
    root = safe_under_tmp(output_root)
    return {
        "audit": root / "private_core_msggame_pc_only_closure.v1.jsonl",
        "candidates": root / "private_core_msggame_pc_only_new_high_confidence_candidates.v1.jsonl",
        "holds": root / "private_core_msggame_pc_only_holds.v1.jsonl",
        "summary": root / "summary.source_free.v1.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true", help="write deterministic private evidence below tmp")
    parser.add_argument("--validate", action="store_true", help="validate generated data and any existing deterministic outputs")
    args = parser.parse_args()

    rows, candidates, holds, summary = build_rows(args.steam_root, args.original_root)
    validate_rows(rows, candidates, holds, summary)
    paths = output_paths(args.output_root)
    payloads = {
        "audit": deterministic_jsonl(rows),
        "candidates": deterministic_jsonl(candidates),
        "holds": deterministic_jsonl(holds),
        "summary": deterministic_json(summary),
    }
    if args.write:
        for key, path in paths.items():
            atomic_write(path, payloads[key])
    if args.validate:
        for key, path in paths.items():
            if not path.is_file():
                raise ClosureError(f"expected deterministic {key} output is absent: {path}")
            if path.read_text(encoding="utf-8") != payloads[key]:
                raise ClosureError(f"existing deterministic {key} output differs: {path}")
    public_result = {
        "coordinate_count": summary["coordinate_count"],
        "disposition_counts": summary["disposition_counts"],
        "hold_or_review_count": summary["hold_or_review_count"],
        "new_high_confidence_candidate_count": summary["new_high_confidence_candidate_count"],
        "automatic_semantic_completion_claim": summary["automatic_semantic_completion_claim"],
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_installation_written": False,
    }
    print(json.dumps(public_result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
