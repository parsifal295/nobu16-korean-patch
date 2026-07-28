#!/usr/bin/env python3
"""Build three independent private PK dialogue review work packets."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector292_consolidated_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_selector292_consolidated.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_selector292_consolidated.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v1"

PRIVATE_SCHEMA = "nobu16.kr.pk-dialogue-wave-assignment.private.v1"
PACKET_SCHEMA = "nobu16.kr.pk-dialogue-wave-work-packet.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-dialogue-wave-assignment.source-free.v1"
METHOD = (
    "post_selector292_rank_order_greedy_three_way_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave1"
MAX_SELECTORS = 3

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "5EECFCF4569D016F0433A81BD6441CA69EAA0FEF8A4A3A59B206F9B4ACBBE7F1",
    "ranking_private":
        "8DA36086B9AD7CE6AAC01F11F873AF87517183977E260DB396816917528E9819",
    "ranking_public":
        "B5CF3A4298190C783B83113FCCC0EDC6BD63C5F0E8A1A5292239E358B5AB3F21",
    "ledger":
        "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725",
    "checkpoint_public":
        "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (286, 190, 736)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (1, 2, 4)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "DD1E1BB72D79AA646CDC6F0FF34F6F5E047FB5355BD107001446C691DBE67F0B"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "DC0B7B85C7215C80886CE2CFBBF0E7DD6FE2189E67BE0967C765E2BCE5AFEE4C",
    "B009219025D5E5BBABCDA59067F0D49539443A9D1A3E811437FC8C011B9A48E5",
    "793C6F5C111D914844859469CEBD61CEBC99E22CBF673BEA04DE61F7318C5DFE",
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "B65F15669454CEC5B25B41E8AF4315704300212504C327BD4B19464EE322A745"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "B6075A025257C007B901FD61B727200E086D3905A98DA3E888AEB5B869F8A591"
)

PIN_NAMES = (
    "EXPECTED_CANDIDATE_SHA256",
    "EXPECTED_SELECTED_SELECTORS",
    "EXPECTED_SELECTION_RANKS",
    "EXPECTED_SELECTION_PROFILE_SHA256",
    "EXPECTED_PACKET_SHA256",
    "EXPECTED_PRIVATE_SHA256",
    "EXPECTED_PUBLIC_SHA256",
)


class WaveAssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WaveAssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def serialized_private(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
        + b"\n"
    )


def serialized_public(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2).encode("ascii")
        + b"\n"
    )


def parse_coordinate(value: str) -> tuple[int, ...]:
    return tuple(map(int, value.split(":")))


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def coordinate_digest(values: Sequence[str] | set[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(values, key=parse_coordinate)).encode("ascii")
    )


def root_digest(values: set[tuple[int, int]]) -> str:
    return sha256_bytes(
        "\n".join(root_string(root) for root in sorted(values)).encode("ascii")
    )


def site_digest(values: Sequence[str] | set[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(values, key=parse_coordinate)).encode("ascii")
    )


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        )
        is None,
        "public summary contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public summary contains exact coordinates",
    )
    require(
        '"translation"' not in content
        and '"reviewed_translation"' not in content,
        "public summary contains dialogue fields",
    )


def unresolved_pins() -> list[str]:
    missing = [
        f"EXPECTED_INPUT_SHA256[{key}]"
        for key, value in EXPECTED_INPUT_SHA256.items()
        if value is None
    ]
    missing.extend(
        name for name in PIN_NAMES if globals()[name] is None
    )
    return missing


def record_literals(engine: Any, record: Any) -> list[str]:
    return [row.text for row in engine.parse_record_literals(record)]


def parse_records(engine: Any, blob: bytes) -> dict[tuple[int, int], Any]:
    return engine.archive_records(engine.parse_packed_msggame(blob).archive)


def load_world(wrapper: Any) -> dict[str, Any]:
    ranking = wrapper.RANKING
    engine = ranking.ENGINE
    steam_root = wrapper.DEFAULT_STEAM_ROOT
    current_path = steam_root / "MSG_PK" / "JP" / "msggame.bin"
    pristine_path = (
        steam_root
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    context_paths = {
        language: steam_root / "MSG_PK" / language.upper() / "msggame.bin"
        for language in ("en", "sc", "tc")
    }
    replacements, pending = ranking.load_official_ledger(
        wrapper.DEFAULT_LEDGER
    )
    candidate_blob = engine.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    candidate_sha = sha256_bytes(candidate_blob)
    expected_candidate = getattr(wrapper, "EXPECTED_PK_CANDIDATE_SHA256")
    require(
        candidate_sha == expected_candidate,
        "post-selector292 candidate reconstruction drifted",
    )
    ledger = {
        str(row["coordinate"]): row
        for row in (
            json.loads(line)
            for line in wrapper.DEFAULT_LEDGER.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        )
        if row.get("resource") == "pk_msggame"
    }
    return {
        "candidate": parse_records(engine, candidate_blob),
        "candidate_blob": candidate_blob,
        "candidate_sha256": candidate_sha,
        "contexts": {
            language: parse_records(engine, path.read_bytes())
            for language, path in context_paths.items()
        },
        "current": parse_records(engine, current_path.read_bytes()),
        "current_path": current_path,
        "engine": engine,
        "ledger": ledger,
        "pending": pending,
        "ranking": ranking,
        "source": parse_records(engine, pristine_path.read_bytes()),
    }


def site_signature(
    site: str,
    record_sets: Sequence[Mapping[tuple[int, int], Any]],
) -> str:
    block_id, record_id, gap_id, offset = parse_coordinate(site)
    root = (block_id, record_id)
    return canonical_sha256({
        "gap": gap_id,
        "offset": offset,
        "records": [
            sha256_bytes(records[root].data) for records in record_sets
        ],
    })


def target_profile(
    row: Mapping[str, Any],
    *,
    rank: int,
    world: Mapping[str, Any],
) -> dict[str, Any]:
    ranking = world["ranking"]
    selector_root = ranking.parse_root(str(row["target_coordinate"]))
    candidate_sites = tuple(map(str, row["candidate_call_sites"]))
    source_sites = tuple(map(str, row["source_call_sites"]))
    candidate_roots = {
        ranking.site_key(site)[:2] for site in candidate_sites
    }
    source_roots = {ranking.site_key(site)[:2] for site in source_sites}
    reachable_roots = {
        ranking.parse_root(str(root))
        for root in row["reachable_pending_roots"]
    }
    closure_nodes = {
        ranking.parse_root(str(root))
        for root in row["jump_closure"]["node_coordinates"]
    }
    terminals = {
        ranking.parse_root(str(root))
        for root in row["jump_closure"]["terminal_coordinates"]
    }
    record_sets = (
        world["candidate"],
        world["current"],
        world["source"],
        world["contexts"]["en"],
        world["contexts"]["sc"],
        world["contexts"]["tc"],
    )
    signatures = {
        site_signature(site, record_sets) for site in candidate_sites
    }
    source_only = set(source_sites) - set(candidate_sites)
    potential = set(map(str, row["current_pending_coordinates"]))
    return {
        "candidate_roots": candidate_roots,
        "candidate_sites": candidate_sites,
        "closure_nodes": closure_nodes,
        "pending_coordinates": potential,
        "rank": rank,
        "reachable_roots": reachable_roots,
        "selector": selector_root[1],
        "selector_root": selector_root,
        "site_roots": candidate_roots | source_roots,
        "source_only_sites": source_only,
        "source_sites": source_sites,
        "template_signatures": signatures,
        "terminals": terminals,
    }


def conflict_counts(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, int]:
    return {
        "atomic_template_signature_overlap":
            len(
                left["template_signatures"]
                & right["template_signatures"]
            ),
        "closure_node_overlap":
            len(left["closure_nodes"] & right["closure_nodes"]),
        "reachable_pending_root_overlap":
            len(left["reachable_roots"] & right["reachable_roots"]),
        "site_root_overlap":
            len(left["site_roots"] & right["site_roots"]),
        "terminal_root_overlap":
            len(left["terminals"] & right["terminals"]),
    }


def profiles_independent(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> bool:
    return not any(conflict_counts(left, right).values())


def choose_profiles(
    ranking_private: Mapping[str, Any],
    world: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    direct = {
        str(row["target_coordinate"]): row
        for row in ranking_private["direct_targets"]
    }
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for rank, summary in enumerate(
        ranking_private["eligible_family_ranking"], start=1
    ):
        coordinate = str(summary["selector_coordinate"])
        profile = target_profile(
            direct[coordinate], rank=rank, world=world
        )
        conflicts = [
            {
                "counts": conflict_counts(profile, accepted),
                "selected_rank": accepted["rank"],
                "selected_selector": accepted["selector"],
            }
            for accepted in selected
            if not profiles_independent(profile, accepted)
        ]
        if conflicts:
            rejected.append({
                "conflicts": conflicts,
                "rank": rank,
                "selector": profile["selector"],
            })
            continue
        selected.append(profile)
        if len(selected) == MAX_SELECTORS:
            break
    require(
        len(selected) == MAX_SELECTORS,
        "fewer than three independent eligible selectors remain",
    )
    return selected, rejected


def neighbor_context(
    records: Mapping[tuple[int, int], Any],
    site: str,
    engine: Any,
) -> dict[str, Any]:
    block_id, record_id, gap_id, _offset = parse_coordinate(site)
    root = (block_id, record_id)
    if root not in records:
        return {"available": False, "left": "", "right": ""}
    values = record_literals(engine, records[root])
    if not 0 <= gap_id <= len(values):
        return {"available": False, "left": "", "right": ""}
    return {
        "available": True,
        "left": "" if gap_id == 0 else values[gap_id - 1],
        "right": "" if gap_id == len(values) else values[gap_id],
    }


def full_record_context(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    engine: Any,
) -> dict[str, Any]:
    if root not in records:
        return {"available": False, "literals": []}
    return {
        "available": True,
        "literals": record_literals(engine, records[root]),
    }


def chunk_roots(
    roots: set[tuple[int, int]],
    pending: Mapping[tuple[int, int], Sequence[str]],
    template_groups: Sequence[set[tuple[int, int]]],
) -> list[list[tuple[int, int]]]:
    count = min(3, max(1, math.ceil(len(roots) / 10)))
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

    for group in template_groups:
        ordered = sorted(group & roots)
        for root in ordered[1:]:
            union(ordered[0], root)
    units: defaultdict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for root in roots:
        units[find(root)].append(root)
    ordered_units = sorted(
        (sorted(unit) for unit in units.values()),
        key=lambda unit: (
            -sum(len(pending.get(root, ())) for root in unit),
            -len(unit),
            tuple(unit),
        ),
    )
    chunks: list[list[tuple[int, int]]] = [[] for _ in range(count)]
    weights = [0] * count
    for unit in ordered_units:
        target = min(
            range(count),
            key=lambda index: (weights[index], len(chunks[index]), index),
        )
        chunks[target].extend(unit)
        weights[target] += sum(len(pending.get(root, ())) for root in unit)
    return [sorted(chunk) for chunk in chunks]


def build_packet(
    profile: Mapping[str, Any],
    *,
    packet_id: int,
    world: Mapping[str, Any],
) -> dict[str, Any]:
    engine = world["engine"]
    ranking = world["ranking"]
    selector = int(profile["selector"])
    candidate_sites = tuple(profile["candidate_sites"])
    source_sites = tuple(profile["source_sites"])
    work_roots = set(profile["reachable_roots"])
    record_sets = (
        world["candidate"],
        world["current"],
        world["source"],
        world["contexts"]["en"],
        world["contexts"]["sc"],
        world["contexts"]["tc"],
    )
    signatures: defaultdict[str, set[tuple[int, int]]] = defaultdict(set)
    for site in candidate_sites:
        signatures[site_signature(site, record_sets)].add(
            ranking.site_key(site)[:2]
        )
    template_groups = [
        roots for roots in signatures.values() if len(roots) > 1
    ]
    template_groups.sort(key=lambda roots: (-len(roots), root_digest(roots)))
    chunks = chunk_roots(work_roots, world["pending"], template_groups)

    site_rows = []
    candidate_edges = ranking.graph_edges(world["candidate"])
    for site in sorted(candidate_sites, key=parse_coordinate):
        block_id, record_id, gap_id, _offset = parse_coordinate(site)
        root = (block_id, record_id)
        same_gap = [
            edge
            for edge in candidate_edges[root]
            if int(edge["gap_id"]) == gap_id
        ]
        site_rows.append({
            "atomic_template_signature":
                site_signature(site, record_sets),
            "context": {
                "candidate":
                    neighbor_context(
                        world["candidate"], site, engine
                    ),
                "current":
                    neighbor_context(world["current"], site, engine),
                "en":
                    neighbor_context(
                        world["contexts"]["en"], site, engine
                    ),
                "jp":
                    neighbor_context(world["source"], site, engine),
                "sc":
                    neighbor_context(
                        world["contexts"]["sc"], site, engine
                    ),
                "tc":
                    neighbor_context(
                        world["contexts"]["tc"], site, engine
                    ),
            },
            "pending_coordinates":
                sorted(
                    world["pending"].get(root, ()),
                    key=parse_coordinate,
                ),
            "root": root_string(root),
            "same_gap_control_count": len(same_gap),
            "same_gap_selectors": [
                int(edge["target"][1])
                for edge in sorted(
                    same_gap, key=lambda row: int(row["offset"])
                )
            ],
            "site": site,
        })

    root_contexts = []
    context_records = {
        "candidate": world["candidate"],
        "current": world["current"],
        "en": world["contexts"]["en"],
        "jp": world["source"],
        "sc": world["contexts"]["sc"],
        "tc": world["contexts"]["tc"],
    }
    for root in sorted(work_roots):
        root_contexts.append({
            "languages": {
                language: full_record_context(records, root, engine)
                for language, records in context_records.items()
            },
            "pending_coordinates":
                sorted(
                    world["pending"].get(root, ()),
                    key=parse_coordinate,
                ),
            "root": root_string(root),
        })

    terminal_rows = []
    for root in sorted(profile["terminals"]):
        coordinate = f"{root[0]}:{root[1]}:0"
        ledger_row = world["ledger"].get(coordinate, {})
        terminal_rows.append({
            "automatic_promotion_authorized": False,
            "languages": {
                language: full_record_context(records, root, engine)
                for language, records in context_records.items()
            },
            "read_only": True,
            "root": root_string(root),
            "runtime_review": ledger_row.get("runtime_review"),
            "scope_classification":
                ledger_row.get("scope_classification"),
        })
    chunk_rows = []
    for chunk_id, roots in enumerate(chunks):
        root_values = set(roots)
        coordinates = {
            coordinate
            for root in roots
            for coordinate in world["pending"].get(root, ())
        }
        sites = {
            site
            for site in candidate_sites
            if ranking.site_key(site)[:2] in root_values
        }
        chunk_rows.append({
            "chunk_id": chunk_id,
            "pending_coordinate_count": len(coordinates),
            "pending_coordinate_sha256": coordinate_digest(coordinates),
            "pending_coordinates":
                sorted(coordinates, key=parse_coordinate),
            "root_count": len(roots),
            "root_sha256": root_digest(root_values),
            "roots": [root_string(root) for root in roots],
            "site_count": len(sites),
            "site_sha256": site_digest(sites),
            "sites": sorted(sites, key=parse_coordinate),
        })

    pending_coordinates = set(profile["pending_coordinates"])
    decisions_name = (
        f"pk_dialogue_wave1_selector{selector}_decisions.private.v1.jsonl"
    )
    evidence_name = (
        f"pk_dialogue_wave1_selector{selector}_evidence.private.v1.json"
    )
    packet = {
        "agent_contract": {
            "accepted_action_values": [
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
                "translation_override_and_verification_renewal",
            ],
            "changed_branches_only": True,
            "en_sc_tc_advisory_only": True,
            "fail_any_branch_or_grammar_blocks_entire_root": True,
            "fresh_semantic_register_and_history_review_required": True,
            "full_integration_rebuild_authorized": False,
            "jp_authoritative": True,
            "maximum_rewrite_attempts_per_root": 1,
            "nonpending_root_actions_authorized": False,
            "output_decisions_basename": decisions_name,
            "output_evidence_basename": evidence_name,
            "prior_evidence_automatic_promotion_authorized": False,
            "source_only_action_count": 0,
            "steam_write_authorized": False,
            "terminal_actions_authorized": False,
        },
        "atomic_template_groups": [
            [root_string(root) for root in sorted(group)]
            for group in template_groups
        ],
        "chunks": chunk_rows,
        "method": METHOD,
        "packet_id": packet_id,
        "rank": int(profile["rank"]),
        "root_contexts": root_contexts,
        "schema": PACKET_SCHEMA,
        "scope": {
            "candidate_site_count": len(candidate_sites),
            "candidate_site_sha256": site_digest(candidate_sites),
            "pending_coordinate_count": len(pending_coordinates),
            "pending_coordinate_sha256":
                coordinate_digest(pending_coordinates),
            "reachable_pending_root_count": len(work_roots),
            "reachable_pending_root_sha256": root_digest(work_roots),
            "selector_coordinate": root_string(
                profile["selector_root"]
            ),
            "source_only_site_count":
                len(profile["source_only_sites"]),
            "source_only_site_sha256":
                site_digest(profile["source_only_sites"]),
            "source_site_count": len(source_sites),
            "source_site_sha256": site_digest(source_sites),
        },
        "site_contexts": site_rows,
        "terminal_manifest": terminal_rows,
        "wave_id": WAVE_ID,
    }
    return packet


def build_outputs(
    *,
    allow_unfrozen: bool = False,
) -> tuple[
    bytes,
    bytes,
    dict[Path, bytes],
    dict[str, Any],
    dict[str, Any],
]:
    require(RANKING_BUILDER_PATH.is_file(), "post-selector292 ranking absent")
    wrapper = load_module(
        RANKING_BUILDER_PATH, "pk_dialogue_wave_ranking"
    )
    observed_inputs = {
        "ranking_builder": sha256_file(RANKING_BUILDER_PATH),
        "ranking_private": sha256_file(RANKING_PRIVATE_PATH),
        "ranking_public": sha256_file(RANKING_PUBLIC_PATH),
        "ledger": sha256_file(wrapper.DEFAULT_LEDGER),
        "checkpoint_public": sha256_file(wrapper.CHECKPOINT_PUBLIC),
    }
    if not allow_unfrozen:
        require(not unresolved_pins(), "wave assignment pins unresolved")
    for key, observed in observed_inputs.items():
        expected = EXPECTED_INPUT_SHA256[key]
        if expected is not None:
            require(observed == expected, f"wave input drifted: {key}")
    ranking_private, ranking_public = wrapper.build_outputs(
        steam_root=wrapper.DEFAULT_STEAM_ROOT,
        ledger_path=wrapper.DEFAULT_LEDGER,
        checkpoint_public_path=wrapper.CHECKPOINT_PUBLIC,
    )
    require(
        ranking_private["schema"].startswith(
            "nobu16.kr.pk-next-selector-family-ranking-"
        )
        and ranking_public["schema"].endswith("-source-free.v1"),
        "ranking handoff drifted",
    )
    world = load_world(wrapper)
    if EXPECTED_CANDIDATE_SHA256 is not None:
        require(
            world["candidate_sha256"] == EXPECTED_CANDIDATE_SHA256,
            "wave candidate drifted",
        )
    selected, rejected = choose_profiles(ranking_private, world)
    selectors = tuple(int(row["selector"]) for row in selected)
    ranks = tuple(int(row["rank"]) for row in selected)
    packets = [
        build_packet(row, packet_id=index, world=world)
        for index, row in enumerate(selected)
    ]
    packet_outputs = {
        PACKET_DIR / f"selector{packet['scope']['selector_coordinate'].split(':')[1]}.private.v1.json":
            serialized_private(packet)
        for packet in packets
    }
    packet_hashes = tuple(
        sha256_bytes(content)
        for _path, content in packet_outputs.items()
    )
    pairwise = []
    for left_index in range(len(selected)):
        for right_index in range(left_index + 1, len(selected)):
            counts = conflict_counts(
                selected[left_index], selected[right_index]
            )
            require(not any(counts.values()), "selected wave conflict")
            pairwise.append({
                "counts": counts,
                "left_packet_id": left_index,
                "right_packet_id": right_index,
            })
    profile_rows = [
        {
            "candidate_root_sha256":
                root_digest(set(row["candidate_roots"])),
            "closure_node_sha256":
                root_digest(set(row["closure_nodes"])),
            "packet_id": index,
            "rank": int(row["rank"]),
            "reachable_root_sha256":
                root_digest(set(row["reachable_roots"])),
            "selector": int(row["selector"]),
            "site_root_sha256": root_digest(set(row["site_roots"])),
            "template_signature_sha256":
                canonical_sha256(sorted(row["template_signatures"])),
            "terminal_root_sha256":
                root_digest(set(row["terminals"])),
        }
        for index, row in enumerate(selected)
    ]
    profile_sha = canonical_sha256(profile_rows)
    if EXPECTED_SELECTED_SELECTORS is not None:
        require(selectors == EXPECTED_SELECTED_SELECTORS, "selection drifted")
    if EXPECTED_SELECTION_RANKS is not None:
        require(ranks == EXPECTED_SELECTION_RANKS, "rank positions drifted")
    if EXPECTED_SELECTION_PROFILE_SHA256 is not None:
        require(
            profile_sha == EXPECTED_SELECTION_PROFILE_SHA256,
            "selection profile drifted",
        )
    if EXPECTED_PACKET_SHA256 is not None:
        require(packet_hashes == EXPECTED_PACKET_SHA256, "packets drifted")

    assignment = {
        "constraints": {
            "changed_branches_only": True,
            "fail_any_branch_or_grammar_blocks_entire_root": True,
            "full_integration_rebuild_authorized": False,
            "maximum_rewrite_attempts_per_root": 1,
            "per_chunk_tracked_review_artifacts": False,
            "per_selector_tracked_review_artifacts": False,
            "source_only_action_count": 0,
            "steam_write_authorized": False,
            "terminal_rows_read_only": True,
        },
        "inputs": {
            **observed_inputs,
            "candidate_sha256": world["candidate_sha256"],
        },
        "method": METHOD,
        "packet_artifacts": [
            {
                "basename": path.name,
                "packet_id": packet_id,
                "sha256": sha256_bytes(packet_outputs[path]),
            }
            for packet_id, path in enumerate(packet_outputs)
        ],
        "packets": packets,
        "pairwise_independence": pairwise,
        "rejected_higher_rank_conflicts": rejected,
        "schema": PRIVATE_SCHEMA,
        "selection_profile": profile_rows,
        "selection_profile_sha256": profile_sha,
        "wave_id": WAVE_ID,
    }
    private_bytes = serialized_private(assignment)
    private_sha = sha256_bytes(private_bytes)
    public_rows = [
        {
            "candidate_site_count":
                packet["scope"]["candidate_site_count"],
            "chunk_count": len(packet["chunks"]),
            "packet_id": packet["packet_id"],
            "packet_sha256": packet_hashes[index],
            "pending_coordinate_count":
                packet["scope"]["pending_coordinate_count"],
            "rank": packet["rank"],
            "reachable_pending_root_count":
                packet["scope"]["reachable_pending_root_count"],
            "selector":
                int(packet["scope"]["selector_coordinate"].split(":")[1]),
            "source_only_site_count":
                packet["scope"]["source_only_site_count"],
            "terminal_count": len(packet["terminal_manifest"]),
        }
        for index, packet in enumerate(packets)
    ]
    public = {
        "distribution_policy": {
            "private_assignment_stays_below_tmp": True,
            "private_decisions_and_evidence_stay_below_tmp": True,
            "tracked_wave_artifact_counts": {
                "assignment_summary": 1,
                "checkpoint": 1,
                "closure": 1,
                "progress": 1,
            },
            "tracked_wave_intermediate_reviews": 0,
        },
        "guards": {
            "candidate_sha256": world["candidate_sha256"],
            "private_assignment_sha256": private_sha,
            "ranking_builder_sha256":
                observed_inputs["ranking_builder"],
            "ranking_private_sha256":
                observed_inputs["ranking_private"],
            "ranking_public_sha256":
                observed_inputs["ranking_public"],
            "selection_profile_sha256": profile_sha,
        },
        "independence": {
            "atomic_template_signature_overlap": 0,
            "closure_node_overlap": 0,
            "pair_count": len(pairwise),
            "reachable_pending_root_overlap": 0,
            "site_root_overlap": 0,
            "terminal_root_overlap": 0,
        },
        "method": METHOD,
        "packets": public_rows,
        "release_target": "0.15.0",
        "result": {
            "packet_count": len(packets),
            "selected_selector_count": len(selectors),
            "total_candidate_sites":
                sum(row["candidate_site_count"] for row in public_rows),
            "total_chunks": sum(row["chunk_count"] for row in public_rows),
            "total_pending_coordinates":
                sum(row["pending_coordinate_count"] for row in public_rows),
            "total_reachable_pending_roots":
                sum(
                    row["reachable_pending_root_count"]
                    for row in public_rows
                ),
            "total_source_only_sites":
                sum(row["source_only_site_count"] for row in public_rows),
            "total_terminal_rows":
                sum(row["terminal_count"] for row in public_rows),
        },
        "schema": PUBLIC_SCHEMA,
        "status": "READY",
        "steam_write_performed": False,
        "wave_id": WAVE_ID,
    }
    assert_source_free(public)
    public_bytes = serialized_public(public)
    if EXPECTED_PRIVATE_SHA256 is not None:
        require(private_sha == EXPECTED_PRIVATE_SHA256, "private drifted")
    if EXPECTED_PUBLIC_SHA256 is not None:
        require(
            sha256_bytes(public_bytes) == EXPECTED_PUBLIC_SHA256,
            "public drifted",
        )
    return private_bytes, public_bytes, packet_outputs, assignment, public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs(allow_unfrozen=args.bootstrap)
    private_bytes, public_bytes, packet_outputs, assignment, public = outputs
    output_map = {
        DEFAULT_PRIVATE_OUTPUT: private_bytes,
        DEFAULT_PUBLIC_OUTPUT: public_bytes,
        **packet_outputs,
    }
    if args.bootstrap or args.write:
        for path, content in output_map.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in output_map.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"wave output drifted: {path}",
            )
    print(json.dumps({
        "candidate_sha256": public["guards"]["candidate_sha256"],
        "input_sha256": assignment["inputs"],
        "packet_sha256": [
            row["sha256"] for row in assignment["packet_artifacts"]
        ],
        "private_sha256":
            public["guards"]["private_assignment_sha256"],
        "public_sha256": sha256_bytes(public_bytes),
        "selection_profile_sha256":
            public["guards"]["selection_profile_sha256"],
        "selection_ranks": [
            row["rank"] for row in public["packets"]
        ],
        "selectors": [
            row["selector"] for row in public["packets"]
        ],
        "status": public["status"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
