#!/usr/bin/env python3
"""Build a root-disjoint three-chunk assignment for PK selector 748.

Candidate call sites are assigned exactly once. Source-only call sites remain
in a separate repair queue, and records sharing an identical template
signature are treated as indivisible assignment atoms.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_"
    "post_selector550_consolidated_v1.py"
)
LEGACY_ASSIGNMENT_PATH = WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
RANKING_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector550_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector550_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector748_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector748_assignment_coverage.v1.json"
)

SELECTOR = 748
TERMINALS = tuple(range(2161, 2168))
CHUNK_COUNT = 3
PRIVATE_SCHEMA = "nobu16.kr.pk-selector748-assignment.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector748-assignment-coverage.v1"
METHOD = (
    "selector550_checkpoint_selector748_root_disjoint_three_chunk_"
    "template_atom_assignment"
)

EXPECTED_INPUT_SHA256 = {
    "ledger": "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E",
    "checkpoint_public": "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC",
    "ranking_builder": "17CB2BA1B4229BAAD8B33DC68ABC5A50BAFA0EEE0C9D9BC7259540734B8EFD12",
    "ranking_private": "6DBF0FF82745F8C229656BBDE4F2E94312DE0C2796F3BA080648AAF5F6E984ED",
    "ranking_public": "1F8377BF3FE8296FEFBA563A1555E524C340E155BC1DB50C0C1A92AAF72BEF38",
    "legacy_assignment": "FFAB60E333B547158CBE349D60708BB8D26B1EBF2DE0F56AC7EF512EDD6EEC9E",
}
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
EXPECTED_CONTEXT_SHA256 = {
    "en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}
EXPECTED_SITE_ROW_SHA256 = (
    "A95B469FD22F8C08556D88893D6FDDFF95BCF0DC65F9205A1F066FE90D73C597"
)
EXPECTED_CHUNK_METRICS = (
    (34, 33, 25, 68, 2, 814),
    (34, 33, 16, 47, 1, 815),
    (34, 34, 19, 47, 1, 826),
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "CE5FBC60D33426695E86FBC8E76205E99917956EE55DBF10375B8933CE91B17E"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "68615492AC049EF3B87D5840ACDB67A8E05D6E8F2EED63CBC89905A8DF5515B2"
)


class AssignmentError(ValueError):
    """Raised when immutable assignment evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RANKING_WRAPPER = load_module(RANKING_BUILDER_PATH, "pk_selector748_ranking_v1")
RANKING = RANKING_WRAPPER.RANKING
RANKING.CONTROL_RE = RANKING.LEGACY.CONTROL_RE
LEGACY = load_module(LEGACY_ASSIGNMENT_PATH, "pk_selector748_site_helpers_v1")
LEGACY.RANKING = RANKING
LEGACY.ENGINE = RANKING.ENGINE
LEGACY.SELECTOR = SELECTOR
LEGACY.TERMINALS = TERMINALS
ENGINE = RANKING.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
    )


def serialized_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    )


def coordinate_digest(values: Iterable[str]) -> str:
    return RANKING.coordinate_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return RANKING.root_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return RANKING.site_digest(values)


def load_records() -> tuple[
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[tuple[int, int], Any],
    dict[str, dict[tuple[int, int], Any]],
    dict[tuple[int, int], set[str]],
]:
    steam_root = RANKING_WRAPPER.DEFAULT_STEAM_ROOT
    current_path = steam_root / "MSG_PK" / "JP" / "msggame.bin"
    pristine_path = (
        steam_root / "KR_PATCH_BACKUP" / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0" / "originals" / "MSG_PK" / "JP"
        / "msggame.bin"
    )
    context_paths = {
        language: steam_root / "MSG_PK" / language.upper() / "msggame.bin"
        for language in ("en", "sc", "tc")
    }
    require(
        sha256_file(current_path) == EXPECTED_PK_CURRENT_SHA256,
        "PK current drifted",
    )
    require(
        sha256_file(pristine_path) == EXPECTED_PK_PRISTINE_SHA256,
        "PK pristine drifted",
    )
    require(
        {key: sha256_file(path) for key, path in context_paths.items()}
        == EXPECTED_CONTEXT_SHA256,
        "multilingual context drifted",
    )
    replacements, pending = RANKING.load_official_ledger(
        RANKING_WRAPPER.DEFAULT_LEDGER
    )
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        "candidate reconstruction drifted",
    )

    def records(blob: bytes) -> dict[tuple[int, int], Any]:
        return ENGINE.archive_records(ENGINE.parse_packed_msggame(blob).archive)

    candidate = records(candidate_blob)
    current = records(current_path.read_bytes())
    source = records(pristine_path.read_bytes())
    contexts = {
        key: records(path.read_bytes()) for key, path in context_paths.items()
    }
    return candidate, current, source, contexts, pending


def template_atoms(
    sites: Sequence[str],
    record_sets: Sequence[Mapping[tuple[int, int], Any]],
) -> list[set[tuple[int, int]]]:
    """Return connected components of every repeated exact site template."""
    signatures: defaultdict[str, set[tuple[int, int]]] = defaultdict(set)
    roots = {RANKING.site_key(site)[:2] for site in sites}
    for site in sites:
        block_id, record_id, gap_id, offset = RANKING.site_key(site)
        root = (block_id, record_id)
        signature = {
            "gap": gap_id,
            "offset": offset,
            "records": [
                sha256_bytes(records[root].data) for records in record_sets
            ],
        }
        signatures[canonical_sha256(signature)].add(root)

    parent = {root: root for root in roots}

    def find(root: tuple[int, int]) -> tuple[int, int]:
        while parent[root] != root:
            parent[root] = parent[parent[root]]
            root = parent[root]
        return root

    def union(left: tuple[int, int], right: tuple[int, int]) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for group in signatures.values():
        if len(group) < 2:
            continue
        ordered = sorted(group)
        for root in ordered[1:]:
            union(ordered[0], root)
    components: defaultdict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for root in roots:
        components[find(root)].add(root)
    result = [group for group in components.values() if len(group) >= 2]
    result.sort(key=lambda group: (-len(group), root_digest(group)))
    return result


def balanced_chunks(
    rows: Sequence[Mapping[str, Any]],
    templates: Sequence[set[tuple[int, int]]],
) -> tuple[list[dict[str, Any]], ...]:
    by_root: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_root[RANKING.parse_root(str(row["root"]))].append(dict(row))
    units: list[list[dict[str, Any]]] = []
    used: set[tuple[int, int]] = set()
    for roots in templates:
        units.append([row for root in sorted(roots) for row in by_root[root]])
        used.update(roots)
    units.extend(by_root[root] for root in sorted(set(by_root) - used))
    units.sort(
        key=lambda unit: (
            -sum(int(row["workload_weight"]) for row in unit),
            -len(unit),
            RANKING.site_key(str(unit[0]["site"])),
        )
    )
    chunks: list[list[dict[str, Any]]] = [[] for _ in range(CHUNK_COUNT)]
    weights = [0] * CHUNK_COUNT
    for unit in units:
        chunk_id = min(
            range(CHUNK_COUNT),
            key=lambda index: (weights[index], len(chunks[index]), index),
        )
        chunks[chunk_id].extend(unit)
        weights[chunk_id] += sum(int(row["workload_weight"]) for row in unit)
    return tuple(
        sorted(chunk, key=lambda row: RANKING.site_key(str(row["site"])))
        for chunk in chunks
    )


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        ) is None,
        "public assignment contains CJK text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public assignment contains an exact coordinate",
    )
    require('"translation"' not in content, "public contains translation")


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    immutable = {
        RANKING_WRAPPER.DEFAULT_LEDGER: EXPECTED_INPUT_SHA256["ledger"],
        RANKING_WRAPPER.CHECKPOINT_PUBLIC:
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        RANKING_BUILDER_PATH: EXPECTED_INPUT_SHA256["ranking_builder"],
        RANKING_PRIVATE_PATH: EXPECTED_INPUT_SHA256["ranking_private"],
        RANKING_PUBLIC_PATH: EXPECTED_INPUT_SHA256["ranking_public"],
        LEGACY_ASSIGNMENT_PATH: EXPECTED_INPUT_SHA256["legacy_assignment"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"input drifted: {path}",
        )
    ranking_private = json.loads(RANKING_PRIVATE_PATH.read_text(encoding="utf-8"))
    ranking_public = json.loads(RANKING_PUBLIC_PATH.read_text(encoding="ascii"))
    require(
        ranking_public["recommendation"]["selector_coordinate"] == "0:748",
        "ranking handoff drifted",
    )
    target = next(
        row for row in ranking_private["direct_targets"]
        if row["target_coordinate"] == "0:748"
    )
    candidate, current, source, contexts, pending = load_records()
    candidate_edges = RANKING.graph_edges(candidate)
    source_edges = RANKING.graph_edges(source)
    candidate_sites = RANKING.candidate_call_sites(candidate_edges)[(0, SELECTOR)]
    source_sites = RANKING.candidate_call_sites(source_edges)[(0, SELECTOR)]
    candidate_roots = {RANKING.site_key(site)[:2] for site in candidate_sites}
    source_only = set(source_sites) - set(candidate_sites)
    candidate_only = set(candidate_sites) - set(source_sites)
    direct_pending_sites = [
        site for site in candidate_sites
        if RANKING.site_key(site)[:2] in pending
    ]
    reachable_roots = {
        RANKING.parse_root(root) for root in target["reachable_pending_roots"]
    }
    potential = {
        coordinate for root in reachable_roots for coordinate in pending[root]
    }
    owned_by_selector = {
        selector: set() for selector in RANKING_WRAPPER.OWNED_SELECTORS
    }
    for root in reachable_roots:
        calls = RANKING.reachable_call_targets(candidate_edges, root)
        for selector in owned_by_selector:
            if (0, selector) in calls:
                owned_by_selector[selector].add(root)
    owned_roots = set().union(*owned_by_selector.values())
    owned_coordinates = {
        coordinate for root in owned_roots for coordinate in pending[root]
    }
    shape = RANKING.family_shape(candidate_edges, source_edges, (0, SELECTOR))
    require(
        len(candidate_sites) == 102
        and len(candidate_roots) == 100
        and len(source_sites) == 114
        and len(source_only) == 12
        and not candidate_only
        and len(direct_pending_sites) == 62
        and len(reachable_roots) == 60
        and len(potential) == 162
        and len(owned_roots) == 4
        and len(owned_coordinates) == 10
        and shape["seven_way"]
        and shape["source_candidate_identical"],
        "selector748 coverage drifted",
    )
    site_rows = LEGACY.build_site_rows(
        sites=candidate_sites,
        candidate=candidate,
        current=current,
        source=source,
        contexts=contexts,
    )
    require(
        canonical_sha256(site_rows) == EXPECTED_SITE_ROW_SHA256,
        "site risk matrix drifted",
    )
    templates = template_atoms(
        candidate_sites,
        [candidate, current, source, contexts["en"], contexts["sc"], contexts["tc"]],
    )
    require(not templates, "selector748 template atom topology drifted")
    template_union: set[tuple[int, int]] = set()
    chunk_rows = balanced_chunks(site_rows, templates)
    chunks: list[dict[str, Any]] = []
    for chunk_id, members in enumerate(chunk_rows):
        roots = {RANKING.parse_root(str(row["root"])) for row in members}
        chunk_pending = {
            coordinate for root in roots for coordinate in pending.get(root, set())
        }
        flags: Counter[str] = Counter()
        languages: Counter[str] = Counter()
        for row in members:
            flags.update(key for key, value in row["flags"].items() if value)
            languages.update(
                key for key, value in row["language_available"].items() if value
            )
        chunks.append({
            "chunk_id": chunk_id,
            "flag_counts": dict(sorted(flags.items())),
            "language_available_counts": dict(sorted(languages.items())),
            "pending_coordinates": sorted(chunk_pending, key=RANKING.parse_coordinate),
            "pending_row_upper_bound": len(chunk_pending),
            "pending_sha256": coordinate_digest(chunk_pending),
            "owned_overlap_root_count": len(roots & owned_roots),
            "owned_overlap_root_sha256": root_digest(roots & owned_roots),
            "pending_root_count": len(roots & reachable_roots),
            "pending_root_sha256": root_digest(roots & reachable_roots),
            "root_count": len(roots),
            "root_sha256": root_digest(roots),
            "roots": [RANKING.root_string(root) for root in sorted(roots)],
            "site_count": len(members),
            "site_sha256": site_digest(str(row["site"]) for row in members),
            "sites": [str(row["site"]) for row in members],
            "template_root_count": len(roots & template_union),
            "template_root_sha256": root_digest(roots & template_union),
            "workload_weight": sum(int(row["workload_weight"]) for row in members),
        })
    observed = tuple(
        (
            row["site_count"], row["root_count"], row["pending_root_count"],
            row["pending_row_upper_bound"], row["owned_overlap_root_count"],
            row["workload_weight"],
        )
        for row in chunks
    )
    require(observed == EXPECTED_CHUNK_METRICS, f"chunk drifted: {observed}")
    require(
        not any(
            set(chunks[left]["roots"]) & set(chunks[right]["roots"])
            for left in range(CHUNK_COUNT) for right in range(left + 1, CHUNK_COUNT)
        )
        and set().union(*(set(row["sites"]) for row in chunks))
        == set(candidate_sites)
        and not (set(source_only) & set(candidate_sites)),
        "candidate/source-only partition drifted",
    )
    root_to_chunk = {
        RANKING.parse_root(root): row["chunk_id"]
        for row in chunks for root in row["roots"]
    }
    require(
        all(len({root_to_chunk[root] for root in group}) == 1 for group in templates),
        "identical template atom split",
    )
    inputs = {
        "official_integrated_ledger_sha256": EXPECTED_INPUT_SHA256["ledger"],
        "official_public_checkpoint_sha256":
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        "ranking_builder_sha256": EXPECTED_INPUT_SHA256["ranking_builder"],
        "ranking_private_sha256": EXPECTED_INPUT_SHA256["ranking_private"],
        "ranking_public_sha256": EXPECTED_INPUT_SHA256["ranking_public"],
        "pk_current_sha256": EXPECTED_PK_CURRENT_SHA256,
        "pk_pristine_sha256": EXPECTED_PK_PRISTINE_SHA256,
        "pk_context_sha256": EXPECTED_CONTEXT_SHA256,
        "pk_rebuilt_candidate_sha256": EXPECTED_PK_CANDIDATE_SHA256,
    }
    private = {
        "schema": PRIVATE_SCHEMA,
        "method": METHOD,
        "inputs": inputs,
        "scope": {
            "selector_coordinate": "0:748:0",
            "terminal_coordinates": [f"0:{value}:0" for value in TERMINALS],
            "candidate_call_sites": candidate_sites,
            "source_only_repair_sites": sorted(source_only, key=RANKING.site_key),
            "direct_pending_call_sites": direct_pending_sites,
            "potential_current_pending_coordinates": sorted(
                potential, key=RANKING.parse_coordinate
            ),
        },
        "identical_template_atoms": [
            [RANKING.root_string(root) for root in sorted(group)]
            for group in templates
        ],
        "site_assignments": site_rows,
        "chunks": chunks,
        "privacy": {
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "steam_write_performed": False,
        },
    }
    private["guards"] = {
        "chunks_canonical_sha256": canonical_sha256(chunks),
        "site_assignments_canonical_sha256": canonical_sha256(site_rows),
        "template_atoms_canonical_sha256":
            canonical_sha256(private["identical_template_atoms"]),
        "payload_without_guards_canonical_sha256": canonical_sha256(private),
    }
    private_content = serialized_json(private)
    public_chunks = [
        {key: row[key] for key in (
            "chunk_id", "flag_counts", "language_available_counts",
            "pending_row_upper_bound", "pending_sha256",
            "owned_overlap_root_count", "owned_overlap_root_sha256",
            "pending_root_count", "pending_root_sha256", "root_count",
            "root_sha256", "site_count", "site_sha256",
            "template_root_count", "template_root_sha256", "workload_weight",
        )}
        for row in chunks
    ]
    public = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": inputs,
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "selector": SELECTOR,
            "terminal_count": 7,
            "terminal_coordinate_sha256": root_digest(shape["candidate_leaves"]),
            "official_pending_rows": 6980,
        },
        "coverage": {
            "candidate_call_site_count": len(candidate_sites),
            "candidate_call_site_sha256": site_digest(candidate_sites),
            "candidate_call_root_count": len(candidate_roots),
            "candidate_call_root_sha256": root_digest(candidate_roots),
            "source_call_site_count": len(source_sites),
            "source_call_site_sha256": site_digest(source_sites),
            "source_only_repair_site_count": len(source_only),
            "source_only_repair_site_sha256": site_digest(source_only),
            "direct_pending_call_site_count": len(direct_pending_sites),
            "direct_pending_call_site_sha256": site_digest(direct_pending_sites),
            "potential_current_pending_rows": len(potential),
            "potential_current_pending_sha256": coordinate_digest(potential),
            "owned_overlap_root_count": len(owned_roots),
            "owned_overlap_pending_rows": len(owned_coordinates),
            "owned_overlap_selector_counts": {
                str(selector): {
                    "pending_root_count": len(roots),
                    "pending_row_count": sum(len(pending[root]) for root in roots),
                }
                for selector, roots in sorted(owned_by_selector.items())
            },
        },
        "assignment": {
            "chunk_count": CHUNK_COUNT,
            "root_split_permitted": False,
            "identical_template_atom_count": len(templates),
            "identical_template_root_count": len(template_union),
            "identical_template_atoms_split": False,
            "source_only_calls_separate_from_candidate_chunks": True,
            "site_risk_matrix_sha256": canonical_sha256(site_rows),
            "chunks": public_chunks,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_assignment_stays_below_tmp": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    public["guards"] = {
        "private_assignment_sha256": sha256_bytes(private_content.encode("utf-8")),
        "payload_without_guards_canonical_sha256": canonical_sha256(public),
    }
    assert_source_free(public)
    return private_content, serialized_json(public), private, public


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-output", type=Path, default=DEFAULT_PRIVATE_OUTPUT)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.private_output.resolve() == DEFAULT_PRIVATE_OUTPUT.resolve(),
        "private path drifted",
    )
    require(
        args.public_output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public path drifted",
    )
    private_content, public_content, _private, public = build_outputs()
    private_sha = sha256_bytes(private_content.encode("utf-8"))
    public_sha = sha256_bytes(public_content.encode("utf-8"))
    if EXPECTED_PRIVATE_FILE_SHA256 is not None:
        require(private_sha == EXPECTED_PRIVATE_FILE_SHA256, "private output drifted")
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(public_sha == EXPECTED_PUBLIC_FILE_SHA256, "public output drifted")
    if args.check:
        require(
            args.private_output.read_text(encoding="utf-8") == private_content,
            "private artifact drifted",
        )
        require(
            args.public_output.read_text(encoding="ascii") == public_content,
            "public artifact drifted",
        )
    else:
        args.private_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_output.write_text(private_content, encoding="utf-8", newline="")
        args.public_output.write_text(public_content, encoding="ascii", newline="")
    print(json.dumps({
        "chunks": [
            {
                "chunk": row["chunk_id"],
                "sites": row["site_count"],
                "pending": row["pending_row_upper_bound"],
                "weight": row["workload_weight"],
            }
            for row in public["assignment"]["chunks"]
        ],
        "private_sha256": private_sha,
        "public_sha256": public_sha,
        "source_only_repair_sites":
            public["coverage"]["source_only_repair_site_count"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
