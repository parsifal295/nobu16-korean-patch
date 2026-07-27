#!/usr/bin/env python3
"""Build the source-free private assignment manifest for PK selector 538."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
INTEGRATED_LEDGER = DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
DEFAULT_OUTPUT = DIALOGUE_TMP / "family538_assignment.private.v1.json"
FINAL_BUILDER = WORKSTREAM / "build_pk_bound_terminal_2546_full_caller_closure_v1.py"

SCHEMA = "nobu16.kr.pk-selector538-assignment.private.v1"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))
CHUNK_COUNT = 4
MIN_CHUNK_SITES = 50
MAX_CHUNK_SITES = 90
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_SITE_COUNT = 277
EXPECTED_SITE_SHA256 = (
    "EF2F1263C50E5C3ED9119DBF81B7BBBFE9761CAD8146C666E7D871F1022DF979"
)
EXPECTED_CUTS = (65, 136, 207, 277)
EXPECTED_FILE_SHA256 = (
    "57FBEE8EEC3551DAD8A7F1BB77CD7B2E2CF08109CB3A912452BE8244BB0FAACF"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_module(path: Path, name: str) -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FINAL = load_module(FINAL_BUILDER, "pk_selector538_assignment_final_v1")
CALLER = FINAL.CALLER


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def coordinate_digest(values: Iterable[str]) -> str:
    return CALLER.coordinate_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return CALLER.record_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "".join(f"{value}\n" for value in values).encode("ascii")
    )


def adjacent_literals(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    block_id, record_id, gap_id, _offset = map(int, site.split(":"))
    value = records.get((block_id, record_id))
    if value is None:
        return "", ""
    literals = CALLER.BASE_AUDIT.parse_record_literals(value)
    return (
        literals[gap_id - 1].text
        if gap_id and gap_id - 1 < len(literals)
        else "",
        literals[gap_id].text if gap_id < len(literals) else "",
    )


def character_width(character: str) -> int:
    if unicodedata.category(character) == "Cc":
        return 0
    return (
        48
        if unicodedata.east_asian_width(character) in {"W", "F", "A"}
        else 24
    )


def line_widths(value: str) -> tuple[int, ...]:
    return tuple(
        sum(character_width(character) for character in line)
        for line in value.split("\n")
    )


def load_ledger() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[int, int], list[str]],
]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    pending: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for line in INTEGRATED_LEDGER.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        key = (str(row["resource"]), str(row["coordinate"]))
        rows[key] = row
        if (
            key[0] == "pk_msggame"
            and row.get("runtime_review") == "pending"
        ):
            pending[CALLER.parse_coordinate(key[1])[:2]].append(key[1])
    for coordinates in pending.values():
        coordinates.sort(key=CALLER.parse_coordinate)
    return rows, dict(pending)


def build_site_rows(
    *,
    candidate_records: Mapping[tuple[int, int], Any],
    current_records: Mapping[tuple[int, int], Any],
    language_records: Mapping[str, Mapping[tuple[int, int], Any]],
) -> list[dict[str, Any]]:
    sites = FINAL.CALLER.call_sites(candidate_records, SELECTOR)
    require(
        len(sites) == EXPECTED_SITE_COUNT
        and site_digest(sites) == EXPECTED_SITE_SHA256,
        "selector 538 site universe drifted",
    )
    terminal_candidate = {
        record_id: CALLER.BASE_AUDIT.parse_record_literals(
            candidate_records[(0, record_id)]
        )[0].text
        for record_id in TERMINALS
    }
    terminal_current = {
        record_id: CALLER.BASE_AUDIT.parse_record_literals(
            current_records[(0, record_id)]
        )[0].text
        for record_id in TERMINALS
    }
    result: list[dict[str, Any]] = []
    for ordinal, site in enumerate(sites):
        block_id, record_id, gap_id, _offset = map(int, site.split(":"))
        left, right = adjacent_literals(candidate_records, site)
        current_left, current_right = adjacent_literals(current_records, site)
        language_available = {
            language: any(
                value != ""
                for value in adjacent_literals(records, site)
            )
            for language, records in language_records.items()
        }
        gap = CALLER.BASE_AUDIT.literal_gaps(
            candidate_records[(block_id, record_id)]
        )[gap_id]
        control_count = sum(
            1 for _match in FINAL.CALLER.CALL_RE.finditer(gap)
        ) + sum(
            1 for _match in CALLER.HONORIFIC.JUMP_RE.finditer(gap)
        )
        layout_risk = False
        maximum_delta = 0
        for terminal in TERMINALS:
            candidate_widths = line_widths(
                left + terminal_candidate[terminal] + right
            )
            current_widths = line_widths(
                current_left
                + terminal_current[terminal]
                + current_right
            )
            nonexpanding = (
                len(candidate_widths) == len(current_widths)
                and all(
                    candidate <= current
                    for candidate, current in zip(
                        candidate_widths,
                        current_widths,
                    )
                )
            )
            layout_risk = layout_risk or not nonexpanding
            maximum_delta = max(
                maximum_delta,
                max(
                    (
                        candidate - current
                        for candidate, current in zip(
                            candidate_widths,
                            current_widths,
                        )
                    ),
                    default=0,
                ),
            )
        flags = {
            "grammar_right_boundary": right != "",
            "layout_relative_expansion": layout_risk,
            "multi_control_gap": control_count > 1,
            "protected_outer_space": (
                (bool(left) and left.endswith(" "))
                or (bool(right) and right.startswith(" "))
            ),
        }
        missing_auxiliary = sum(
            not language_available[language]
            for language in ("sc", "tc", "en")
        )
        workload_weight = (
            10
            + 4 * int(flags["grammar_right_boundary"])
            + 7 * int(flags["layout_relative_expansion"])
            + 6 * int(flags["multi_control_gap"])
            + 8 * int(flags["protected_outer_space"])
            + 3 * missing_auxiliary
        )
        result.append(
            {
                "flags": flags,
                "language_available": language_available,
                "left_coordinate": (
                    f"{block_id}:{record_id}:{gap_id - 1}"
                    if gap_id
                    else None
                ),
                "maximum_positive_raw_g1n_delta_px": maximum_delta,
                "ordinal": ordinal,
                "root": f"{block_id}:{record_id}",
                "site": site,
                "workload_weight": workload_weight,
            }
        )
    return result


def balanced_cuts(rows: Sequence[Mapping[str, Any]]) -> tuple[int, ...]:
    count = len(rows)
    total = sum(int(row["workload_weight"]) for row in rows)
    target_weight = total / CHUNK_COUNT
    target_count = count / CHUNK_COUNT
    prefix = [0]
    for row in rows:
        prefix.append(prefix[-1] + int(row["workload_weight"]))
    dynamic: dict[tuple[int, int], tuple[float, tuple[int, ...]]] = {
        (0, 0): (0.0, ())
    }
    for chunk_id in range(1, CHUNK_COUNT + 1):
        for end in range(
            chunk_id * MIN_CHUNK_SITES,
            min(count, chunk_id * MAX_CHUNK_SITES) + 1,
        ):
            best: tuple[float, tuple[int, ...]] | None = None
            for start in range(
                (chunk_id - 1) * MIN_CHUNK_SITES,
                min(end - MIN_CHUNK_SITES, (chunk_id - 1) * MAX_CHUNK_SITES)
                + 1,
            ):
                previous = dynamic.get((chunk_id - 1, start))
                if previous is None:
                    continue
                workload = prefix[end] - prefix[start]
                site_count = end - start
                cost = (
                    previous[0]
                    + (workload - target_weight) ** 2
                    + 2 * (site_count - target_count) ** 2
                )
                candidate = (cost, previous[1] + (end,))
                if best is None or candidate[0] < best[0]:
                    best = candidate
            if best is not None:
                dynamic[(chunk_id, end)] = best
    cuts = dynamic[(CHUNK_COUNT, count)][1]
    require(cuts == EXPECTED_CUTS, f"assignment cuts drifted: {cuts}")
    return cuts


def build_manifest() -> dict[str, Any]:
    require(
        sha256_file(INTEGRATED_LEDGER) == EXPECTED_LEDGER_SHA256,
        "integrated ledger drifted",
    )
    *_unused, bundle = FINAL.build_outputs()
    analysis = bundle["analysis"]
    candidate_blob = analysis["candidate_blob"]
    require(
        sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "candidate blob drifted",
    )
    prepared = CALLER.ENGINE.prepare_artifacts(
        CALLER.ENGINE.DEFAULT_STEAM_ROOT,
        CALLER.ENGINE.DEFAULT_BASE_PRISTINE,
        CALLER.ENGINE.DEFAULT_PK_PRISTINE,
    )
    pk_resource = prepared.resources["pk_msggame"]
    current_records = CALLER.ENGINE.archive_records(
        pk_resource.current_archive
    )
    language_records = {
        "jp": CALLER.ENGINE.archive_records(pk_resource.pristine_archive),
        "sc": CALLER.ENGINE.archive_records(
            pk_resource.context_archives["SC"]
        ),
        "tc": CALLER.ENGINE.archive_records(
            pk_resource.context_archives["TC"]
        ),
        "en": CALLER.ENGINE.archive_records(
            pk_resource.context_archives["EN"]
        ),
    }
    _ledger_rows, pending_by_root = load_ledger()
    site_rows = build_site_rows(
        candidate_records=analysis["candidate_records"],
        current_records=current_records,
        language_records=language_records,
    )
    cuts = balanced_cuts(site_rows)
    starts = (0,) + cuts[:-1]
    chunks: list[dict[str, Any]] = []
    for chunk_id, (start, end) in enumerate(zip(starts, cuts)):
        members = site_rows[start:end]
        roots = sorted(
            {
                tuple(map(int, str(row["root"]).split(":")))
                for row in members
            }
        )
        root_strings = [f"{root[0]}:{root[1]}" for root in roots]
        pending_coordinates = [
            coordinate
            for root in roots
            for coordinate in pending_by_root.get(root, ())
        ]
        flag_counts: Counter[str] = Counter()
        language_counts: Counter[str] = Counter()
        for row in members:
            flag_counts.update(
                key for key, value in row["flags"].items() if value
            )
            language_counts.update(
                key
                for key, value in row["language_available"].items()
                if value
            )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "flag_counts": dict(sorted(flag_counts.items())),
                "language_available_counts": dict(
                    sorted(language_counts.items())
                ),
                "ordinal_end": end - 1,
                "ordinal_start": start,
                "pending_coordinate_sha256": coordinate_digest(
                    pending_coordinates
                ),
                "pending_coordinates": pending_coordinates,
                "pending_row_upper_bound": len(pending_coordinates),
                "root_count": len(roots),
                "root_sha256": root_digest(roots),
                "roots": root_strings,
                "site_count": len(members),
                "site_sha256": site_digest(
                    str(row["site"]) for row in members
                ),
                "sites": [str(row["site"]) for row in members],
                "workload_weight": sum(
                    int(row["workload_weight"]) for row in members
                ),
            }
        )
    payload: dict[str, Any] = {
        "assignment_method": {
            "chunk_count": CHUNK_COUNT,
            "contiguous_ordinals": True,
            "objective": (
                "minimum squared deviation from one-quarter total workload "
                "plus twice the squared site-count deviation"
            ),
            "site_count_bounds": [
                MIN_CHUNK_SITES,
                MAX_CHUNK_SITES,
            ],
            "weights": {
                "base": 10,
                "grammar_right_boundary": 4,
                "layout_relative_expansion": 7,
                "missing_auxiliary_language_each": 3,
                "multi_control_gap": 6,
                "protected_outer_space": 8,
            },
        },
        "canonicalization": {
            "encoding": "UTF-8",
            "file": (
                "recursive lexicographic keys, compact separators, "
                "ensure_ascii=true, one LF terminator"
            ),
        },
        "chunks": chunks,
        "inputs": {
            "candidate_sha256": sha256_bytes(candidate_blob),
            "integrated_ledger_path": str(
                INTEGRATED_LEDGER.relative_to(REPO)
            ).replace("\\", "/"),
            "integrated_ledger_sha256": sha256_file(INTEGRATED_LEDGER),
            "pending_rows_before": 8213,
        },
        "privacy": {
            "classification": "private",
            "contains_dialogue_bodies": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
        "schema": SCHEMA,
        "scope": {
            "resource": "pk_msggame",
            "selector_coordinate": f"0:{SELECTOR}:0",
            "site_count": len(site_rows),
            "site_sha256": site_digest(
                str(row["site"]) for row in site_rows
            ),
            "terminal_coordinates": [
                f"0:{record_id}:0" for record_id in TERMINALS
            ],
            "terminal_coordinate_sha256": coordinate_digest(
                f"0:{record_id}:0" for record_id in TERMINALS
            ),
        },
        "site_assignments": site_rows,
    }
    payload["guards"] = {
        "chunks_canonical_sha256": canonical_sha256(chunks),
        "payload_canonical_sha256": canonical_sha256(payload),
        "site_assignments_canonical_sha256": canonical_sha256(site_rows),
    }
    return payload


def serialized_manifest() -> bytes:
    return canonical_bytes(build_manifest()) + b"\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    content = serialized_manifest()
    actual_sha256 = sha256_bytes(content)
    if EXPECTED_FILE_SHA256:
        require(
            actual_sha256 == EXPECTED_FILE_SHA256,
            f"assignment file digest drifted: {actual_sha256}",
        )
    if args.check:
        require(args.output.is_file(), f"assignment is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "assignment manifest content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    manifest = json.loads(content)
    print(
        json.dumps(
            {
                "chunks": [
                    {
                        "chunk_id": chunk["chunk_id"],
                        "ordinal_range": [
                            chunk["ordinal_start"],
                            chunk["ordinal_end"],
                        ],
                        "pending_row_upper_bound":
                            chunk["pending_row_upper_bound"],
                        "root_count": chunk["root_count"],
                        "site_count": chunk["site_count"],
                        "workload_weight": chunk["workload_weight"],
                    }
                    for chunk in manifest["chunks"]
                ],
                "file_sha256": actual_sha256,
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
