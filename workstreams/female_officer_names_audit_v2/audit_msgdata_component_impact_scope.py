#!/usr/bin/env python3
"""Audit the full *possible* name-sharing scope of a msgdata component overlay.

This is a read-only, conservative impact audit.  For every ``msgev`` string it
finds all exact, non-empty, two-component decompositions of the SC text, then
selects the pairs containing each proposed JP ``msgdata`` component.  A match
means that the component *could* produce that text if a runtime record uses
that pair.  It is deliberately an upper bound: the static executable analysis
does not recover the per-officer runtime component map.

The report keeps source text out of the JSON.  ``--details`` emits the small
human review table (IDs and Korean direct names) only to the explicitly chosen
working file; it must remain outside the game installation and is not a
distribution artefact.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent


class AuditError(RuntimeError):
    """Raised when a supplied input cannot satisfy the audit contract."""


def load_component_audit() -> Any:
    module_path = HERE / "audit_female_officer_component_combinations.py"
    spec = importlib.util.spec_from_file_location("female_component_audit", module_path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load component audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPONENT_AUDIT = load_component_audit()
SCHEMA = "nobu16.kr.msgdata-component-impact-scope-audit.v1"
HISTORICAL_OFFICER_MAX_ID = COMPONENT_AUDIT.HISTORICAL_OFFICER_MAX_ID

# The evidence labels are intentionally narrower than the planned overlay.
# A lexical decomposition can establish only a possible scope, never a record
# assignment.  2083 is the user's directly observed Oichi regression; 2082
# is an explicit requested global spelling policy.  The other entries remain
# pending until a record anchor or an equally strong authorization is found.
EVIDENCE_BY_COMPONENT: dict[int, dict[str, str]] = {
    2083: {
        "level": "RUNTIME_OBSERVED_SINGLE_ANCHOR",
        "note": "Observed Oichi output; known component pair is 62+2083.",
    },
    2082: {
        "level": "USER_POLICY_APPROVED_GLOBAL_COMPONENT",
        "note": "User directed every Hime component to render as 히메.",
    },
}

# Decision is deliberately made at the historical-officer-name level.  A
# component-table entry can also occur as a normal word in dialogue; that does
# not prove a name-record use.  A *historical name* whose direct Korean form
# does not contain the proposed replacement normally blocks an unrestricted
# component change, unless every apparent conflict has a complete alternate
# exact component decomposition that excludes the proposed ID.
DECISION_BY_COMPONENT: dict[int, dict[str, str]] = {
    386: {
        "status": "TARGET_PAIR_ALTERNATE_COMPONENTS_VALIDATED",
        "reason": "Megohime exact pair is 386+2082; the six other historical 爱-token names have complete exact component pairs excluding 386 and at least one pair renders each direct Korean name exactly.",
    },
    2083: {
        "status": "OBSERVED_ANCHOR_ALTERNATE_COMPONENTS_VALIDATED",
        "reason": "Observed Oichi anchor is 62+2083; the four other historical 市-token names have complete exact component pairs 573+1661/7764, 572+2371, 596+2016 and 596+2447, none of which contains 2083.",
    },
}


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(payload, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_outside_game_root(path: Path, game_root: Path) -> None:
    try:
        path.resolve().relative_to(game_root.resolve())
    except ValueError:
        return
    raise AuditError("output must be outside the supplied game root")


def pair_comparison(
    pair: tuple[int, int], candidate_components: list[str], direct_ko: str
) -> str:
    left, right = pair
    return COMPONENT_AUDIT.compare(candidate_components[left] + candidate_components[right], direct_ko)


def empty_scope() -> dict[str, Any]:
    return {
        "msgev_ids": [],
        "exact_pair_occurrence_count": 0,
        "comparison_counts": Counter(),
        "rows": [],
    }


def empty_token_scope() -> dict[str, Any]:
    return {"msgev_ids": [], "replacement_containment_counts": Counter(), "rows": []}


def add_row(
    scope: dict[str, Any],
    msgev_id: int,
    pairs: list[tuple[int, int]],
    source_text: str,
    direct_ko: str,
    candidate_components: list[str],
) -> None:
    comparisons = [pair_comparison(pair, candidate_components, direct_ko) for pair in pairs]
    scope["msgev_ids"].append(msgev_id)
    scope["exact_pair_occurrence_count"] += len(pairs)
    scope["comparison_counts"].update(comparisons)
    scope["rows"].append(
        {
            "msgev_id": msgev_id,
            "source_utf16le_sha256": COMPONENT_AUDIT.text_hash(source_text),
            "direct_ko_utf16le_sha256": COMPONENT_AUDIT.text_hash(direct_ko),
            "pairs": [[left, right] for left, right in pairs],
            "comparisons": comparisons,
        }
    )


def serialise_scope(scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "msgev_ids": scope["msgev_ids"],
        "msgev_row_count": len(scope["msgev_ids"]),
        "exact_pair_occurrence_count": scope["exact_pair_occurrence_count"],
        "comparison_counts": dict(sorted(scope["comparison_counts"].items())),
        "rows": scope["rows"],
    }


def add_token_row(
    scope: dict[str, Any], msgev_id: int, source_text: str, direct_ko: str, replacement_ko: str
) -> None:
    contains_replacement = replacement_ko in direct_ko
    scope["msgev_ids"].append(msgev_id)
    scope["replacement_containment_counts"].update(
        ["DIRECT_CONTAINS_REPLACEMENT" if contains_replacement else "DIRECT_DOES_NOT_CONTAIN_REPLACEMENT"]
    )
    scope["rows"].append(
        {
            "msgev_id": msgev_id,
            "source_utf16le_sha256": COMPONENT_AUDIT.text_hash(source_text),
            "direct_ko_utf16le_sha256": COMPONENT_AUDIT.text_hash(direct_ko),
            "direct_ko_contains_replacement": contains_replacement,
        }
    )


def serialise_token_scope(scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "msgev_ids": scope["msgev_ids"],
        "msgev_row_count": len(scope["msgev_ids"]),
        "replacement_containment_counts": dict(sorted(scope["replacement_containment_counts"].items())),
        "rows": scope["rows"],
    }


def audit(game_root: Path) -> tuple[dict[str, Any], dict[int, list[dict[str, Any]]]]:
    entries, overlay = COMPONENT_AUDIT.load_overlay()
    tables: dict[str, tuple[str, ...]] = {}
    input_tables: dict[str, dict[str, Any]] = {}
    for resource_name, relative in (
        ("SC_msgev", COMPONENT_AUDIT.MSGEV_RELATIVE),
        ("JP_msgev", COMPONENT_AUDIT.MSGEV_RELATIVE),
        ("SC_msgdata", COMPONENT_AUDIT.MSGDATA_RELATIVE),
        ("JP_msgdata", COMPONENT_AUDIT.MSGDATA_RELATIVE),
    ):
        language = resource_name[:2]
        texts, metadata = COMPONENT_AUDIT.read_table(
            game_root / Path(str(relative).format(language=language))
        )
        expected = (
            COMPONENT_AUDIT.EXPECTED_MSGEV_COUNT
            if resource_name.endswith("msgev")
            else COMPONENT_AUDIT.EXPECTED_MSGDATA_COUNT
        )
        if len(texts) != expected:
            raise AuditError(f"{resource_name} string count differs")
        tables[resource_name] = texts
        input_tables[resource_name] = metadata

    candidate_components = COMPONENT_AUDIT.apply_overlay_in_memory(tables["JP_msgdata"], entries)
    source_index = COMPONENT_AUDIT.component_index(tables["SC_msgdata"])
    component_ids = tuple(entry["id"] for entry in entries)
    scopes: dict[int, dict[str, dict[str, Any]]] = {
        component_id: {
            "all_msgev": empty_scope(),
            "historical_officers": empty_scope(),
            "historical_female_officers": empty_scope(),
        }
        for component_id in component_ids
    }
    # A component token occurrence is an even more conservative lexical upper
    # bound than a completed two-part decomposition.  It is necessary for
    # one-character components such as 2083, for which no non-empty split of
    # the source display string can expose the runtime pair.
    token_scopes: dict[int, dict[str, dict[str, Any]]] = {
        component_id: {
            "all_msgev": empty_token_scope(),
            "historical_officers": empty_token_scope(),
            "historical_female_officers": empty_token_scope(),
        }
        for component_id in component_ids
    }
    # Retained separately for the review-only local detail file.
    detail_rows: dict[int, list[dict[str, Any]]] = {component_id: [] for component_id in component_ids}

    # This is intentionally the whole 17,916-row table, not merely 0..2206.
    # That avoids incorrectly claiming that a component has no other possible
    # use merely because it did not occur in the historical-officer range.
    for msgev_id, source_text in enumerate(tables["SC_msgev"]):
        all_pairs = COMPONENT_AUDIT.exact_pairs(source_text, source_index)
        direct_ko = tables["JP_msgev"][msgev_id]
        for component_id in component_ids:
            source_token = tables["SC_msgdata"][component_id]
            replacement_ko = candidate_components[component_id]
            if source_token and source_token in source_text:
                add_token_row(token_scopes[component_id]["all_msgev"], msgev_id, source_text, direct_ko, replacement_ko)
                if msgev_id <= HISTORICAL_OFFICER_MAX_ID:
                    add_token_row(token_scopes[component_id]["historical_officers"], msgev_id, source_text, direct_ko, replacement_ko)
                    if msgev_id in COMPONENT_AUDIT.OFFICIAL_ROSTER_IDS or msgev_id in COMPONENT_AUDIT.HIME_COMPONENT_EXTENSION_IDS:
                        add_token_row(token_scopes[component_id]["historical_female_officers"], msgev_id, source_text, direct_ko, replacement_ko)
            if not all_pairs:
                continue
            matched = [
                pair for pair in all_pairs if component_id == pair[0] or component_id == pair[1]
            ]
            if not matched:
                continue
            add_row(scopes[component_id]["all_msgev"], msgev_id, matched, source_text, direct_ko, candidate_components)
            if msgev_id <= HISTORICAL_OFFICER_MAX_ID:
                add_row(scopes[component_id]["historical_officers"], msgev_id, matched, source_text, direct_ko, candidate_components)
                if msgev_id in COMPONENT_AUDIT.OFFICIAL_ROSTER_IDS or msgev_id in COMPONENT_AUDIT.HIME_COMPONENT_EXTENSION_IDS:
                    add_row(scopes[component_id]["historical_female_officers"], msgev_id, matched, source_text, direct_ko, candidate_components)
            detail_rows[component_id].append(
                {
                    "msgev_id": msgev_id,
                    "direct_ko": direct_ko,
                    "pairs": matched,
                    "comparisons": [pair_comparison(pair, candidate_components, direct_ko) for pair in matched],
                    "historical_officer": msgev_id <= HISTORICAL_OFFICER_MAX_ID,
                    "reviewed_female_officer": msgev_id in COMPONENT_AUDIT.OFFICIAL_ROSTER_IDS or msgev_id in COMPONENT_AUDIT.HIME_COMPONENT_EXTENSION_IDS,
                }
            )

    components: list[dict[str, Any]] = []
    for entry in entries:
        component_id = entry["id"]
        evidence = EVIDENCE_BY_COMPONENT.get(
            component_id,
            {
                "level": "STATIC_LEXICAL_SCOPE_ONLY",
                "note": "No runtime record anchor recovered; do not deploy from this evidence alone.",
            },
        )
        declared = list(entry["affected_msgev_ids"])
        full_historical = scopes[component_id]["historical_officers"]["msgev_ids"]
        token_historical = token_scopes[component_id]["historical_officers"]
        decision = DECISION_BY_COMPONENT.get(
            component_id,
            {
                "status": "HISTORICAL_NAME_SCOPE_VALIDATED",
                "reason": "Every historical source-token occurrence contains the proposed Korean replacement in the direct Korean officer name.",
            },
        )
        components.append(
            {
                "component_id": component_id,
                "replacement_ko_utf16le_sha256": entry["ko_utf16le_sha256"],
                "overlay_declared_msgev_ids": declared,
                "static_evidence": evidence,
                "scope_is_possible_upper_bound_not_runtime_mapping": True,
                "declared_ids_outside_historical_possible_scope": sorted(set(declared) - set(full_historical)),
                "historical_possible_ids_not_in_declared_overlay_scope": sorted(set(full_historical) - set(declared)),
                "historical_name_scope_decision": decision,
                "all_msgev": serialise_scope(scopes[component_id]["all_msgev"]),
                "historical_officers": serialise_scope(scopes[component_id]["historical_officers"]),
                "historical_female_officers": serialise_scope(scopes[component_id]["historical_female_officers"]),
                "source_component_token_occurrence_upper_bound": {
                    "definition": "Rows whose SC msgev source text contains the SC msgdata text at this component ID. This is intentionally broader than an exact pair and does not establish record use.",
                    "all_msgev": serialise_token_scope(token_scopes[component_id]["all_msgev"]),
                    "historical_officers": serialise_token_scope(token_scopes[component_id]["historical_officers"]),
                    "historical_female_officers": serialise_token_scope(token_scopes[component_id]["historical_female_officers"]),
                },
            }
        )

    document = {
        "schema": SCHEMA,
        "method": {
            "analysis": "static_only",
            "all_msgev_rows_examined": len(tables["SC_msgev"]),
            "historical_officer_id_range": [0, HISTORICAL_OFFICER_MAX_ID],
            "pair_rule": "all exact non-empty two-component decompositions of SC msgev text in SC msgdata ID range",
            "scope_interpretation": "A matched row is a possible use, not proof that its runtime record contains that component pair.",
            "runtime_record_mapping_recovered": False,
            "installed_game_files_modified": False,
        },
        "source_text_policy": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "row_texts_stored_as_hash_only": True,
        },
        "input_tables": input_tables,
        "in_memory_overlay": {
            "overlay_id": overlay["overlay_id"],
            "component_ids": list(component_ids),
            "installed_game_files_modified": False,
        },
        "components": components,
    }
    return document, detail_rows


def render_details(
    document: dict[str, Any], detail_rows: dict[int, list[dict[str, Any]]]
) -> str:
    lines = [
        "# Private component impact review", "",
        "This is a static possible-scope review, not a runtime-record map.",
        "A listed name is an upper-bound candidate only.", "",
    ]
    for component in document["components"]:
        component_id = component["component_id"]
        evidence = component["static_evidence"]["level"]
        rows = detail_rows[component_id]
        lines += [
            f"## component {component_id} — {evidence}", "",
            f"all={component['all_msgev']['msgev_row_count']}; "
            f"historical={component['historical_officers']['msgev_row_count']}; "
            f"reviewed-female={component['historical_female_officers']['msgev_row_count']}",
            "",
            "| msgev ID | Korean direct text | possible component pair(s) | comparison | historical | reviewed female |",
            "| ---: | --- | --- | --- | :---: | :---: |",
        ]
        for row in rows:
            pairs = ", ".join(f"{left}+{right}" for left, right in row["pairs"])
            comparisons = ", ".join(row["comparisons"])
            # A vertical bar is structural Markdown, so escape it should one
            # occur in a text entry.
            direct_ko = row["direct_ko"].replace("|", "\\|").replace("\n", "<br>")
            lines.append(
                f"| {row['msgev_id']} | {direct_ko} | {pairs} | {comparisons} | "
                f"{'Y' if row['historical_officer'] else ''} | {'Y' if row['reviewed_female_officer'] else ''} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--details", type=Path)
    args = parser.parse_args(argv)
    try:
        game_root = args.game_root.resolve()
        report = args.report.resolve()
        ensure_outside_game_root(report, game_root)
        if args.details is not None:
            ensure_outside_game_root(args.details.resolve(), game_root)
        document, details = audit(game_root)
        atomic_write(report, json.dumps(document, ensure_ascii=False, indent=2) + "\n")
        if args.details is not None:
            atomic_write(args.details.resolve(), render_details(document, details))
    except (OSError, ValueError, AuditError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"report={report}")
    if args.details is not None:
        print(f"details={args.details.resolve()}")
    for component in document["components"]:
        print(
            "component=" + str(component["component_id"])
            + " all=" + str(component["all_msgev"]["msgev_row_count"])
            + " historical=" + str(component["historical_officers"]["msgev_row_count"])
            + " female=" + str(component["historical_female_officers"]["msgev_row_count"])
            + " token_historical=" + str(component["source_component_token_occurrence_upper_bound"]["historical_officers"]["msgev_row_count"])
            + " evidence=" + str(component["static_evidence"]["level"])
            + " decision=" + str(component["historical_name_scope_decision"]["status"])
        )
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
