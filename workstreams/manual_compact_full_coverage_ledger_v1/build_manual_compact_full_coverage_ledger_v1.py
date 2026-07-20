#!/usr/bin/env python3
"""Build a read-only coverage ledger for manual_compact_korean_layout rows.

This is an audit index, not an event-message builder.  It reads the historical
1,553-row inventory plus existing review artifacts/private-candidate audits and
writes a compact ledger under this workstream only.  It never reads or writes
the Steam installation and it has no Git, release, or network code path.

The Static Patch 007 contract recorded here is deliberately the 30px runtime
contract: raw G1N <= 1440, ceil(raw * 30 / 48) <= 912, at most four lines.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"
OUTPUT = PUBLIC / "manual_compact_full_coverage_ledger.v1.json"

SCHEMA = "nobu16.kr.manual-compact-full-coverage-ledger.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
EXPECTED_INVENTORY_COUNT = 1_553

INVENTORY_PATH = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_korean_layout_inventory_v1"
    / "public"
    / "msgev_manual_compact_korean_layout_inventory.v1.json"
)

# These are explicit quality holds, not layout holds.  A layout-only candidate
# must not silently turn such a row into a completed translation review.
QUALITY_HOLD_OVERRIDES: Mapping[int, str] = {
    3820: (
        "The batch07 layout audit explicitly retained this row and states that "
        "a separate source-semantic Korean quality review is required."
    ),
}

CANDIDATE_WORKSTREAMS: tuple[str, ...] = (
    "pc_event_manual_compact_static007_batch01_v1",
    "pc_event_manual_compact_static007_batch02_v1",
    "pc_event_manual_compact_static007_batch03_v1",
    "pc_event_manual_compact_static007_batch04_v1",
    "pc_event_manual_compact_static007_batch05_v1",
    "pc_event_manual_compact_static007_batch06_v1",
    "pc_event_manual_compact_static007_batch07_v1",
    "pc_event_manual_compact_4000_5000_restore_v1",
    "pc_event_manual_compact_static007_6000_7999_restore_v1",
    "pc_event_manual_compact_static007_3900_11008_restore_v1",
)

REVIEW_SPECS: tuple[Mapping[str, str], ...] = (
    {
        "name": "manual_compact_4000_review_v1",
        "relative": "workstreams/manual_compact_4000_review_v1/public/manual_compact_4000_review.v1.json",
    },
    {
        "name": "manual_compact_5000_review_v1",
        "relative": "workstreams/manual_compact_5000_review_v1/public/manual_compact_5000_review.v1.json",
    },
    {
        "name": "manual_compact_6000_review_v1",
        "relative": "workstreams/manual_compact_6000_review_v1/public/manual_compact_6000_review.v1.json",
    },
    {
        "name": "manual_compact_7000_review_v1",
        "relative": "workstreams/manual_compact_7000_review_v1/public/manual_compact_7000_review.v1.json",
    },
    {
        "name": "manual_compact_8000_review_v1",
        "relative": "workstreams/manual_compact_8000_review_v1/public/manual_compact_8000_review.v1.json",
    },
    {
        "name": "manual_compact_9000_review_v1",
        "relative": "workstreams/manual_compact_9000_review_v1/public/manual_compact_9000_review.v1.json",
    },
    {
        "name": "manual_compact_10000_review_v1",
        "relative": "workstreams/manual_compact_10000_review_v1/public/manual_compact_10000_11008_review.v1.json",
    },
    # The 3900 reviewer owns this path.  It is intentionally optional while
    # that focused review is in progress; absence is reported as a real gap.
    {
        "name": "manual_compact_3900_review_v1",
        "relative": "workstreams/manual_compact_3900_review_v1/public/manual_compact_3900_review.v1.json",
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def ids(value: Any) -> set[int]:
    """Return the integer IDs in an artifact field without coercing text IDs."""
    if value is None:
        return set()
    require(isinstance(value, (list, tuple, set)), f"ID field must be a list, got {type(value).__name__}")
    result: set[int] = set()
    for item in value:
        require(isinstance(item, int), f"non-integer entry ID: {item!r}")
        result.add(item)
    return result


def range_bucket(entry_id: int) -> str:
    if 3000 <= entry_id <= 3999:
        return "3000-3999"
    if 4000 <= entry_id <= 4999:
        return "4000-4999"
    if 5000 <= entry_id <= 5999:
        return "5000-5999"
    if 6000 <= entry_id <= 6999:
        return "6000-6999"
    if 7000 <= entry_id <= 7999:
        return "7000-7999"
    if 8000 <= entry_id <= 8999:
        return "8000-8999"
    if 9000 <= entry_id <= 9999:
        return "9000-9999"
    if 10000 <= entry_id <= 11008:
        return "10000-11008"
    raise RuntimeError(f"inventory ID outside requested coverage range: {entry_id}")


def get_first(mapping: Mapping[str, Any], names: Iterable[str], default: Any = None) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    return default


def parse_literal_assignments(path: Path) -> dict[str, set[int]]:
    """Read the declared batch lists without importing a candidate builder."""
    if not path.is_file():
        return {}
    wanted = {
        "CHANGED_IDS",
        "RUNTIME_HOLD_IDS",
        "STATIC_RETAINED_MANUAL_IDS",
        "QUALITY_HOLD_IDS",
    }
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: dict[str, set[int]] = {}
    for node in tree.body:
        targets: list[str] = []
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
            value = node.value
        if value is None:
            continue
        for target in targets:
            if target not in wanted:
                continue
            try:
                literal = ast.literal_eval(value)
            except (ValueError, TypeError):
                continue
            if isinstance(literal, (tuple, list, set)) and all(isinstance(item, int) for item in literal):
                found[target] = set(literal)
    return found


def candidate_audit_layout(audit: Mapping[str, Any], changed: set[int]) -> Mapping[str, Any]:
    """Verify the emitted private-candidate audit uses the Static Patch 007 gate."""
    policy = audit.get("layout_policy", audit.get("static_patch_007_layout"))
    require(isinstance(policy, Mapping), "candidate audit lacks layout_policy")
    raw_full = get_first(policy, ("raw_full_width_px", "raw_g1n_full_width_px"))
    raw_half = get_first(policy, ("raw_half_width_px", "raw_g1n_half_width_px"))
    raw_limit = get_first(policy, ("raw_hard_limit_px", "raw_g1n_hard_limit_px", "raw_g1n_pass_limit_px"))
    effective_limit = get_first(policy, ("effective_width_hard_limit_px", "runtime_usable_line_width_px"))
    max_lines = get_first(policy, ("max_lines",))
    formula = policy.get("effective_width_formula")
    explicit_advance_contract = raw_full is not None or raw_half is not None
    contract_ok = (
        raw_limit == 1440
        and effective_limit == 912
        and max_lines == 4
        and formula == "ceil(raw_g1n_width_px * 30 / 48)"
        and (not explicit_advance_contract or (raw_full == 48 and raw_half == 24))
    )

    rows = audit.get("rows")
    require(isinstance(rows, list), "candidate audit lacks rows")
    observed_changed = {
        row.get("entry_id")
        for row in rows
        if isinstance(row, Mapping) and row.get("entry_id") in changed
    }
    missing_rows = sorted(changed - observed_changed)
    over_rows: list[int] = []
    max_raw = 0
    max_effective = 0
    max_target_lines = 0
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        entry_id = row.get("entry_id")
        if entry_id not in changed:
            continue
        target_lines = row.get("target_lines")
        nested_layout = row.get("layout")
        if target_lines is None and isinstance(nested_layout, Mapping):
            target_lines = nested_layout.get("lines")
        require(isinstance(target_lines, list), f"changed candidate row {entry_id} lacks target_lines")
        line_count = get_first(
            row,
            ("target_manual_line_count", "target_line_count"),
            nested_layout.get("line_count", len(target_lines)) if isinstance(nested_layout, Mapping) else len(target_lines),
        )
        require(isinstance(line_count, int), f"invalid target line count: {entry_id}")
        max_target_lines = max(max_target_lines, line_count)
        row_bad = line_count > 4
        for line in target_lines:
            require(isinstance(line, Mapping), f"invalid target line payload: {entry_id}")
            raw = line.get("raw_g1n_width_px")
            effective = line.get("effective_width_px")
            require(isinstance(raw, int), f"missing raw width: {entry_id}")
            require(isinstance(effective, int), f"missing effective width: {entry_id}")
            max_raw = max(max_raw, raw)
            max_effective = max(max_effective, effective)
            if raw > 1440 or effective > 912:
                row_bad = True
        if row.get("any_line_exceeds_912px") is True:
            row_bad = True
        if row.get("target_static_patch_007_passes") is False:
            row_bad = True
        if row.get("max_four_lines_pass") is False:
            row_bad = True
        if isinstance(nested_layout, Mapping):
            if nested_layout.get("any_line_exceeds_912px") is True:
                row_bad = True
            if nested_layout.get("all_lines_pass_static_patch_007") is False:
                row_bad = True
        if row_bad:
            over_rows.append(entry_id)
    return {
        "contract_ok": contract_ok,
        "formula": formula,
        "max_raw_g1n_width_px": max_raw,
        "max_effective_width_px": max_effective,
        "max_target_line_count": max_target_lines,
        "changed_rows_missing_from_audit": missing_rows,
        "changed_rows_over_limit_or_over_four_lines": sorted(over_rows),
    }


def collect_candidate(workstream: str, universe: set[int]) -> Mapping[str, Any]:
    root = REPO / "tmp" / workstream / "candidate-final"
    audit_path = root / "audit.v1.json"
    manifest_path = root / "candidate_manifest.v1.json"
    event_path = root / "MSG_PK" / "JP" / "msgev.bin"
    script_matches = list((REPO / "workstreams" / workstream).glob("build*.py"))
    script_path = script_matches[0] if len(script_matches) == 1 else None
    result: dict[str, Any] = {
        "workstream": workstream,
        "candidate_event_present": event_path.is_file(),
        "audit_present": audit_path.is_file(),
        "manifest_present": manifest_path.is_file(),
        "event_relative": repo_relative(event_path) if event_path.is_file() else None,
        "audit_relative": repo_relative(audit_path) if audit_path.is_file() else None,
        "manifest_relative": repo_relative(manifest_path) if manifest_path.is_file() else None,
        "script_relative": repo_relative(script_path) if script_path else None,
        "declared_source_lists": {},
        "audit_changed_ids": [],
        "audit_preserved_ids": [],
        "audit_runtime_hold_ids": [],
        "audit_static_retained_ids": [],
        "audit_quality_hold_ids": [],
        "outside_inventory_ids": [],
        "source_audit_drift": {},
        "layout_validation": None,
        "safety": {},
    }
    if script_path:
        declared = parse_literal_assignments(script_path)
        result["declared_source_lists"] = {key: sorted(value) for key, value in sorted(declared.items())}
    else:
        declared = {}
    if not audit_path.is_file():
        return result

    audit = read_json(audit_path)
    require(isinstance(audit, Mapping), f"invalid candidate audit: {audit_path}")
    coverage = audit.get("coverage", {})
    require(isinstance(coverage, Mapping), f"candidate coverage missing: {audit_path}")
    changed = ids(
        get_first(
            audit,
            ("actual_changed_row_ids",),
            get_first(coverage, ("manual_compact_changed_ids", "planned_changed_row_ids", "changed_row_ids"), []),
        )
    )
    preserved = ids(get_first(coverage, ("preserved_review_row_ids", "preserved_row_ids"), []))
    runtime_hold = ids(get_first(coverage, ("runtime_hold_excluded_ids",), audit.get("runtime_hold_excluded_ids", [])))
    static_retained = ids(get_first(coverage, ("static_retained_manual_ids",), audit.get("static_retained_manual_ids", [])))
    quality_hold = ids(get_first(coverage, ("quality_hold_ids",), []))

    # These IDs are constrained to the historical manual inventory below; a
    # candidate can still list non-manual context rows without affecting it.
    all_artifact_ids = changed | preserved | runtime_hold | static_retained | quality_hold
    outside = sorted(all_artifact_ids - universe)
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    require(isinstance(manifest, Mapping), f"invalid candidate manifest: {manifest_path}")
    result.update(
        {
            "audit_sha256": sha256_file(audit_path),
            "candidate_event_sha256": sha256_file(event_path) if event_path.is_file() else None,
            "output_event_profile": audit.get("output_event_profile"),
            "audit_changed_ids": sorted(changed & universe),
            "audit_preserved_ids": sorted(preserved & universe),
            "audit_runtime_hold_ids": sorted(runtime_hold & universe),
            "audit_static_retained_ids": sorted(static_retained & universe),
            "audit_quality_hold_ids": sorted(quality_hold & universe),
            "outside_inventory_ids": outside,
            "layout_validation": candidate_audit_layout(audit, changed),
            "safety": {
                "candidate_only": audit.get("candidate_only", manifest.get("candidate_only")),
                "steam_game_resource_written": audit.get("steam_game_resource_written", manifest.get("steam_game_resource_written", False)),
                "git_operation_performed": audit.get("git_operation_performed", manifest.get("git_operation_performed", False)),
                "release_published": audit.get("release_published", manifest.get("release_published", False)),
                "network_operation_performed": audit.get("network_operation_performed", manifest.get("network_operation_performed", False)),
            },
        }
    )
    declared_to_audit = {
        "CHANGED_IDS": changed,
        "RUNTIME_HOLD_IDS": runtime_hold,
        "STATIC_RETAINED_MANUAL_IDS": static_retained,
        "QUALITY_HOLD_IDS": quality_hold,
    }
    result["source_audit_drift"] = {
        key: sorted((declared.get(key, set()) & universe) ^ (actual & universe))
        for key, actual in declared_to_audit.items()
        if key in declared
    }
    return result


def review_layout_contract(review: Mapping[str, Any]) -> Mapping[str, Any]:
    baseline = review.get("layout_baseline", {})
    if not isinstance(baseline, Mapping):
        return {"present": False, "contract_ok": False}
    raw_full = get_first(baseline, ("raw_g1n_full_width_advance_px", "raw_full_width_px"))
    raw_half = get_first(baseline, ("raw_g1n_half_width_advance_px", "raw_half_width_px"))
    raw_limit = get_first(baseline, ("raw_g1n_pass_limit_px",))
    effective_limit = get_first(baseline, ("effective_width_pass_limit_px",))
    max_lines = get_first(baseline, ("max_lines", "maximum_lines"))
    formula = baseline.get("effective_width_formula")
    return {
        "present": True,
        "raw_full_width_px": raw_full,
        "raw_half_width_px": raw_half,
        "raw_limit_px": raw_limit,
        "effective_limit_px": effective_limit,
        "max_lines": max_lines,
        "formula": formula,
        "contract_ok": (
            raw_full == 48
            and raw_half == 24
            and raw_limit == 1440
            and effective_limit == 912
            and max_lines == 4
            and formula == "ceil(raw_g1n_width_px * 30 / 48)"
        ),
    }


def collect_review(spec: Mapping[str, str], universe: set[int]) -> Mapping[str, Any]:
    name = spec["name"]
    path = REPO / spec["relative"]
    result: dict[str, Any] = {
        "name": name,
        "relative": spec["relative"],
        "present": path.is_file(),
        "entry_count": 0,
        "entry_ids": [],
        "entries": {},
        "layout_contract": None,
    }
    if not path.is_file():
        return result
    review = read_json(path)
    require(isinstance(review, Mapping), f"invalid review artifact: {path}")
    entries = review.get("entries")
    require(isinstance(entries, list), f"review entries missing: {path}")
    records: dict[int, Mapping[str, Any]] = {}
    for entry in entries:
        require(isinstance(entry, Mapping), f"invalid review entry: {path}")
        entry_id = entry.get("entry_id", entry.get("id"))
        require(isinstance(entry_id, int), f"review entry lacks integer ID: {path}")
        if entry_id not in universe:
            continue
        require(entry_id not in records, f"duplicate review ID {entry_id}: {path}")
        current_values = [
            value
            for key, value in entry.items()
            if key.startswith("current_ko") and isinstance(value, str)
        ]
        proposed = entry.get("proposed_ko")
        records[entry_id] = {
            "review_status": entry.get("review_status"),
            "restoration_strategy": entry.get("restoration_strategy"),
            "semantic_status": entry.get("semantic_status"),
            "review_judgement": entry.get("review_judgement"),
            "proposed_matches_review_current": (
                isinstance(proposed, str)
                and len(current_values) == 1
                and proposed == current_values[0]
            ),
        }
    result.update(
        {
            "sha256": sha256_file(path),
            "schema": review.get("schema"),
            "entry_count": len(records),
            "entry_ids": sorted(records),
            "entries": {str(entry_id): record for entry_id, record in sorted(records.items())},
            "layout_contract": review_layout_contract(review),
            "safety": review.get("safety", {}),
        }
    )
    return result


def initial_row(inventory_row: Mapping[str, Any]) -> dict[str, Any]:
    entry_id = inventory_row["entry_id"]
    historical_layout = inventory_row.get("source_manual_compact_layout", {})
    require(isinstance(historical_layout, Mapping), f"invalid historical manual layout: {entry_id}")
    return {
        "entry_id": entry_id,
        "range": range_bucket(entry_id),
        "historical_manual_operation": historical_layout.get("operation"),
        "historical_manual_newline_operations": historical_layout.get("newline_operations"),
        "historical_source_utf16le_sha256": inventory_row.get("source_manual_compact_ko_utf16le_sha256"),
        "current_strict_utf16le_sha256": inventory_row.get("current_ko_utf16le_sha256"),
        "candidate_actions": [],
        "review_artifacts": [],
        "status": None,
        "resolution_status": None,
        "follow_up": None,
    }


def classify_rows(
    inventory_rows: list[Mapping[str, Any]],
    candidates: list[Mapping[str, Any]],
    reviews: list[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    universe = {row["entry_id"] for row in inventory_rows}
    rows = {row["entry_id"]: initial_row(row) for row in inventory_rows}
    conflicts: list[Mapping[str, Any]] = []

    action_map = (
        ("audit_changed_ids", "private_candidate_built_text_change"),
        ("audit_preserved_ids", "private_candidate_built_reviewed_preserve"),
        ("audit_runtime_hold_ids", "runtime_token_hold_context_reviewed"),
        ("audit_static_retained_ids", "reviewed_layout_retained"),
        ("audit_quality_hold_ids", "translation_quality_hold"),
    )
    for candidate in candidates:
        for key, action in action_map:
            for entry_id in candidate.get(key, []):
                if entry_id not in universe:
                    continue
                rows[entry_id]["candidate_actions"].append(
                    {"action": action, "workstream": candidate["workstream"]}
                )
    for review in reviews:
        for entry_id in review.get("entry_ids", []):
            if entry_id not in universe:
                continue
            record = review["entries"][str(entry_id)]
            rows[entry_id]["review_artifacts"].append(
                {
                    "artifact": review["name"],
                    "review_status": record.get("review_status"),
                    "restoration_strategy": record.get("restoration_strategy"),
                    "semantic_status": record.get("semantic_status"),
                    "proposed_matches_review_current": record.get("proposed_matches_review_current"),
                }
            )

    priority = {
        "translation_quality_hold": 70,
        "runtime_token_hold_context_reviewed": 60,
        "private_candidate_built_text_change": 50,
        "private_candidate_built_reviewed_preserve": 40,
        "reviewed_layout_retained": 30,
    }

    def review_current_is_final_preserve_or_reflow(row: Mapping[str, Any]) -> tuple[bool, str | None]:
        """A review can resolve a no-byte-change row only when it proves the
        proposed text is already the strict current text.  A review proposal
        that differs still needs its chained private candidate and is pending.
        """
        records = row["review_artifacts"]
        if not records or not all(record["proposed_matches_review_current"] for record in records):
            return False, None
        strategies = " ".join(str(record.get("restoration_strategy") or "").lower() for record in records)
        if "reflow" in strategies:
            return True, "resolved_semantic_reflow"
        return True, "resolved_preserve"

    for entry_id, row in rows.items():
        actions = row["candidate_actions"]
        action_names = {action["action"] for action in actions}
        # Explicit quality work takes priority over a layout-only retention.
        # If a later candidate has an audited text change for this exact row,
        # the old hold is resolved by that source-semantic candidate instead.
        if (
            entry_id in QUALITY_HOLD_OVERRIDES
            and "private_candidate_built_text_change" not in action_names
        ):
            row["status"] = "translation_quality_hold"
            row["follow_up"] = QUALITY_HOLD_OVERRIDES[entry_id]
        elif actions:
            chosen = max(actions, key=lambda action: priority[action["action"]])["action"]
            row["status"] = chosen
            if chosen == "runtime_token_hold_context_reviewed":
                row["follow_up"] = (
                    "Establish the runtime name-token rendering route and a token-specific "
                    "30/48-scaled reservation before semantic reflow; do not use a global estimate."
                )
        elif row["review_artifacts"]:
            row["status"] = "review_complete_private_candidate_pending"
            already_current, resolution = review_current_is_final_preserve_or_reflow(row)
            if already_current:
                row["resolution_status"] = resolution
                row["follow_up"] = None
            else:
                row["follow_up"] = (
                    "Apply only this review artifact's proposed_ko in a chained private candidate, "
                    "then validate its per-line Static Patch 007 audit."
                )
        else:
            row["status"] = "unreviewed_pending"
            row["follow_up"] = "No completed review artifact or explicit candidate/hold record covers this historical manual-compact row."

        if row["resolution_status"] is None:
            if row["status"] == "private_candidate_built_reviewed_preserve":
                row["resolution_status"] = "resolved_preserve"
            elif row["status"] == "reviewed_layout_retained":
                row["resolution_status"] = "resolved_preserve"
            elif row["status"] == "private_candidate_built_text_change":
                strategy_text = " ".join(
                    str(record.get("restoration_strategy") or "").lower()
                    for record in row["review_artifacts"]
                )
                batch_semantic_reflow = any(
                    action["workstream"].startswith("pc_event_manual_compact_static007_batch")
                    for action in actions
                    if action["action"] == "private_candidate_built_text_change"
                )
                row["resolution_status"] = (
                    "resolved_semantic_reflow"
                    if "reflow" in strategy_text or batch_semantic_reflow
                    else "resolved_restore"
                )
            elif row["status"] == "runtime_token_hold_context_reviewed":
                row["resolution_status"] = "pending_runtime_token_evidence"
            elif row["status"] == "translation_quality_hold":
                row["resolution_status"] = "pending_translation_quality"
            elif row["status"] == "review_complete_private_candidate_pending":
                row["resolution_status"] = "pending_private_candidate"
            elif row["status"] == "unreviewed_pending":
                row["resolution_status"] = "pending_review"
            else:
                raise RuntimeError(f"unclassified resolution state: {entry_id} {row['status']}")

        # Two different non-hold candidate outcomes for the same ID would make
        # the ledger ambiguous.  The expected chaining has no such conflicts.
        built_actions = {
            name
            for name in action_names
            if name in {"private_candidate_built_text_change", "private_candidate_built_reviewed_preserve", "reviewed_layout_retained"}
        }
        if len(built_actions) > 1:
            conflicts.append({"entry_id": entry_id, "candidate_actions": actions})
    return [rows[entry_id] for entry_id in sorted(rows)], conflicts


def summarize_ranges(rows: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["range"]].append(row)
    ordered = (
        "3000-3999",
        "4000-4999",
        "5000-5999",
        "6000-6999",
        "7000-7999",
        "8000-8999",
        "9000-9999",
        "10000-11008",
    )
    result: list[Mapping[str, Any]] = []
    for name in ordered:
        selected = groups[name]
        counts = Counter(row["status"] for row in selected)
        resolution_counts = Counter(row["resolution_status"] for row in selected)
        unresolved = [
            row["entry_id"]
            for row in selected
            if not str(row["resolution_status"]).startswith("resolved_")
        ]
        result.append(
            {
                "range": name,
                "target_count": len(selected),
                "status_counts": dict(sorted(counts.items())),
                "resolution_status_counts": dict(sorted(resolution_counts.items())),
                "candidate_or_review_assignment_complete": all(row["status"] != "unreviewed_pending" for row in selected),
                "all_rows_resolved": not unresolved,
                "private_candidate_ready_without_follow_up": not unresolved,
                "unresolved_or_pending_ids": unresolved,
            }
        )
    return result


def build_ledger() -> Mapping[str, Any]:
    inventory = read_json(INVENTORY_PATH)
    require(isinstance(inventory, Mapping), "inventory root must be an object")
    inventory_rows = inventory.get("rows")
    require(isinstance(inventory_rows, list), "inventory rows missing")
    require(len(inventory_rows) == EXPECTED_INVENTORY_COUNT, "historical inventory is not 1,553 rows")
    require(all(isinstance(row, Mapping) for row in inventory_rows), "inventory contains invalid row")
    universe = {row["entry_id"] for row in inventory_rows}
    require(len(universe) == EXPECTED_INVENTORY_COUNT, "historical inventory has duplicate IDs")

    layout = inventory.get("layout_policy", {})
    require(isinstance(layout, Mapping), "inventory layout policy missing")
    inventory_layout_ok = (
        layout.get("raw_full_width_px") == 48
        and layout.get("raw_half_width_px") == 24
        and layout.get("static_patch_007_raw_equivalent_limit_px") == 1440
        and layout.get("static_patch_007_runtime_effective_limit_px") == 912
        and layout.get("max_lines") == 4
        and layout.get("effective_width_formula") == "ceil(raw_g1n_width_px * 30 / 48)"
    )
    candidates = [collect_candidate(workstream, universe) for workstream in CANDIDATE_WORKSTREAMS]
    reviews = [collect_review(spec, universe) for spec in REVIEW_SPECS]
    rows, conflicts = classify_rows(inventory_rows, candidates, reviews)
    ranges = summarize_ranges(rows)
    status_counts = Counter(row["status"] for row in rows)
    resolution_status_counts = Counter(row["resolution_status"] for row in rows)
    unresolved_rows = [
        {
            "entry_id": row["entry_id"],
            "range": row["range"],
            "status": row["status"],
            "resolution_status": row["resolution_status"],
            "follow_up": row["follow_up"],
        }
        for row in rows
        if not str(row["resolution_status"]).startswith("resolved_")
    ]
    candidate_drift = [
        {
            "workstream": candidate["workstream"],
            "drift": {key: value for key, value in candidate["source_audit_drift"].items() if value},
        }
        for candidate in candidates
        if any(candidate["source_audit_drift"].values())
    ]
    candidate_layout_failures = [
        {
            "workstream": candidate["workstream"],
            "layout_validation": candidate["layout_validation"],
        }
        for candidate in candidates
        if candidate["layout_validation"] is not None
        and (
            not candidate["layout_validation"]["contract_ok"]
            or candidate["layout_validation"]["changed_rows_missing_from_audit"]
            or candidate["layout_validation"]["changed_rows_over_limit_or_over_four_lines"]
        )
    ]
    review_layout_failures = [
        {"artifact": review["name"], "layout_contract": review["layout_contract"]}
        for review in reviews
        if review["present"] and not review["layout_contract"]["contract_ok"]
    ]
    missing_reviews = [review["name"] for review in reviews if not review["present"]]
    three_xxx = next(item for item in ranges if item["range"] == "3000-3999")
    ledger: dict[str, Any] = {
        "schema": SCHEMA,
        "resource": RESOURCE,
        "read_only_audit": True,
        "candidate_binary_created_by_this_workstream": False,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
        "scope": {
            "historical_manual_compact_operation": "manual_compact_korean_layout",
            "historical_target_count": EXPECTED_INVENTORY_COUNT,
            "id_min": min(universe),
            "id_max": max(universe),
            "inventory_relative": repo_relative(INVENTORY_PATH),
            "inventory_sha256": sha256_file(INVENTORY_PATH),
        },
        "static_patch_007_layout_contract": {
            "runtime_font_px": 30,
            "line_spacing_setting": 8,
            "usable_line_width_px": 912,
            "max_lines": 4,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "raw_g1n_limit_px": 1440,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_limit_px": 912,
            "inventory_contract_matches": inventory_layout_ok,
        },
        "candidate_artifacts": candidates,
        "review_artifacts": reviews,
        "summary": {
            "target_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "resolution_status_counts": dict(sorted(resolution_status_counts.items())),
            "candidate_or_review_assignment_complete": not any(row["status"] == "unreviewed_pending" for row in rows),
            "all_1553_resolved": all(
                str(row["resolution_status"]).startswith("resolved_") for row in rows
            ),
            "all_review_artifacts_present": not missing_reviews,
            "all_private_candidate_audits_layout_safe": not candidate_layout_failures,
            "all_review_layout_contracts_match_static007": not review_layout_failures,
            "candidate_source_audit_drift_count": len(candidate_drift),
            "candidate_action_conflict_count": len(conflicts),
            "unresolved_or_pending_count": len(unresolved_rows),
            "private_candidate_ready_without_follow_up": len(unresolved_rows) == 0,
            "steam_deployment_ready": False,
        },
        "range_coverage": ranges,
        "three_xxx_coverage_check": {
            "historical_target_count": three_xxx["target_count"],
            "expected_historical_target_count": 191,
            "candidate_or_review_assignment_complete": three_xxx["candidate_or_review_assignment_complete"],
            "all_rows_resolved": three_xxx["all_rows_resolved"],
            "private_candidate_ready_without_follow_up": three_xxx["private_candidate_ready_without_follow_up"],
            "unresolved_or_pending_ids": three_xxx["unresolved_or_pending_ids"],
            "note": (
                "A true result means every 3xxx historical manual-compact ID has either "
                "a private-candidate action, a completed review record, or an explicit hold. "
                "Final completion is instead all_rows_resolved=true; any runtime-token hold "
                "keeps that result false. It never means a Steam install occurred."
            ),
        },
        "candidate_source_audit_drift": candidate_drift,
        "candidate_layout_failures": candidate_layout_failures,
        "review_layout_contract_failures": review_layout_failures,
        "missing_review_artifacts": missing_reviews,
        "candidate_action_conflicts": conflicts,
        "unresolved_or_pending": unresolved_rows,
        "rows": rows,
    }
    return ledger


def print_summary(ledger: Mapping[str, Any]) -> None:
    summary = ledger["summary"]
    print(f"historical target rows: {summary['target_count']}")
    print("status counts:")
    for status, count in summary["status_counts"].items():
        print(f"  {status}: {count}")
    print("resolution status counts:")
    for status, count in summary["resolution_status_counts"].items():
        print(f"  {status}: {count}")
    print(
        "3xxx assignment complete: "
        f"{ledger['three_xxx_coverage_check']['candidate_or_review_assignment_complete']}"
    )
    print(f"unresolved or pending: {summary['unresolved_or_pending_count']}")
    print(f"candidate source/audit drift: {summary['candidate_source_audit_drift_count']}")


def validate(ledger: Mapping[str, Any], *, require_finished_review: bool) -> None:
    summary = ledger["summary"]
    require(summary["target_count"] == EXPECTED_INVENTORY_COUNT, "target count drift")
    require(ledger["static_patch_007_layout_contract"]["inventory_contract_matches"], "inventory layout contract drift")
    require(not ledger["candidate_action_conflicts"], "candidate actions conflict")
    require(not ledger["candidate_layout_failures"], "candidate layout audit failure")
    require(not ledger["review_layout_contract_failures"], "review layout contract failure")
    if require_finished_review:
        if not summary["all_1553_resolved"]:
            pending = summary["resolution_status_counts"]
            if set(pending) <= {"pending_runtime_token_evidence", "resolved_restore", "resolved_preserve", "resolved_semantic_reflow"}:
                raise RuntimeError(
                    f"gate blocked: {pending.get('pending_runtime_token_evidence', 0)} "
                    "runtime-token evidence holds remain"
                )
            raise RuntimeError(
                "all 1,553 rows must be resolved_restore/resolved_preserve/resolved_semantic_reflow"
            )
        require(not ledger["candidate_source_audit_drift"], "candidate source/audit drift remains")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate", "gate", "summary"))
    args = parser.parse_args()
    ledger = build_ledger()
    if args.command == "build":
        PUBLIC.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {repo_relative(OUTPUT)}")
        print_summary(ledger)
        return 0
    if args.command == "summary":
        print_summary(ledger)
        return 0
    validate(ledger, require_finished_review=args.command == "gate")
    print("structural validation passed")
    print_summary(ledger)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
