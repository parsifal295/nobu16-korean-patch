#!/usr/bin/env python3
"""Build a source-private, root-sharded maximum-width PK dialogue wave 7.

Every still-pending root reachable from the 55 eligible selector families is
owned by the highest-ranked eligible selector that reaches it.  The resulting
owner packets are globally disjoint by root, pending coordinate, candidate
site, and source site, then balanced across three agent bundles.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pk_msggame_runtime_vm_audit_v1").is_dir()
)
WORKSTREAM = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

BASE_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave5_v1.py"
)
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave6_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave6.private.v1.json"
)
DEFAULT_OUTPUT = (
    TMP / "pk_dialogue_wave7_root_sharded_assignment.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave7_root_sharded_assignment.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v7_root_sharded"

METHOD = (
    "post292_wave6_rank_order_highest_rank_per_pending_root_"
    "global_disjoint_owner_shards_three_bundle_balance_v1"
)
WAVE_ID = "post_selector292_wave7_root_sharded"
SCHEMA = "nobu16.kr.pk-dialogue-wave7-root-sharded-assignment.private.v1"
AGENT_BUNDLE_COUNT = 3
EXPECTED_ELIGIBLE_FAMILIES = 55
EXPECTED_PENDING_COORDINATES = 216
EXPECTED_PENDING_ROOTS = 113
EXPECTED_OWNER_SELECTORS = 48
EXPECTED_BASE_BUILDER_SHA256 = (
    "8373B34147AC889C17A4574C5B5CC328EC7C87BDB18CE1DEE7DA3A61E38F54D0"
)
EXPECTED_RANKING_BUILDER_SHA256 = (
    "B4FE4B994729E97F515C8F2DE71D0AEA19369339CCCD0334FDBA918EF3A4B356"
)
EXPECTED_RANKING_PRIVATE_SHA256 = (
    "FED6181AE978C3A476F6DEDEDC80BF995B3B79A740662BFCFBAA6D96E962169A"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)
EXPECTED_PRIVATE_SHA256 = (
    "95806AE1BD79742473E8C503E1F8DA48C13EC3408CDCFF705E4AB418734E7D3B"
)
EXPECTED_PUBLIC_SHA256 = (
    "6D6601B9BC91456EBD65ECA86D479592BCF998584A9F5E2E336A438C5BCC7E5E"
)


class RootShardedAssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RootShardedAssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_PATH, "pk_dialogue_wave7_root_shard_base")
ENGINE = BASE.ENGINE
RANKING = load_module(
    RANKING_BUILDER_PATH, "pk_dialogue_wave7_root_shard_ranking"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_root(value: str) -> tuple[int, int]:
    parts = value.split(":")
    require(len(parts) >= 2, f"invalid root coordinate: {value}")
    return int(parts[0]), int(parts[1])


def site_root(value: str) -> tuple[int, int]:
    return ENGINE.parse_coordinate(value)[:2]


def owner_profiles(
    ranking_private: Mapping[str, Any],
    world: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    direct = {
        str(row["target_coordinate"]): row
        for row in ranking_private["direct_targets"]
    }
    eligible = list(ranking_private["eligible_family_ranking"])
    require(
        len(eligible) == EXPECTED_ELIGIBLE_FAMILIES,
        "eligible family count drifted",
    )
    owner_by_root: dict[tuple[int, int], tuple[int, int]] = {}
    skipped_selectors: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    record_sets = (
        world["candidate"],
        world["current"],
        world["source"],
        world["contexts"]["en"],
        world["contexts"]["sc"],
        world["contexts"]["tc"],
    )
    for rank, summary in enumerate(eligible, start=1):
        coordinate = str(summary["selector_coordinate"])
        row = direct[coordinate]
        full = ENGINE.target_profile(row, rank=rank, world=world)
        owned_roots = {
            root
            for root in full["reachable_roots"]
            if root not in owner_by_root
        }
        if not owned_roots:
            skipped_selectors.append({
                "rank": rank,
                "selector": int(full["selector"]),
                "reason": "all_reachable_pending_roots_owned_by_higher_rank",
            })
            continue
        for root in owned_roots:
            owner_by_root[root] = (rank, int(full["selector"]))
        # Keep every runtime branch for the owning selector.  Non-owner roots
        # are branch-validation context only; actionable coordinates are
        # restricted below to owned_roots/pending_coordinates.
        candidate_sites = tuple(full["candidate_sites"])
        source_sites = tuple(full["source_sites"])
        candidate_roots = {site_root(site) for site in candidate_sites}
        source_roots = {site_root(site) for site in source_sites}
        require(
            owned_roots <= candidate_roots,
            f"selector {full['selector']} owns root without candidate branch",
        )
        pending_coordinates = {
            coordinate
            for root in owned_roots
            for coordinate in world["pending"].get(root, ())
        }
        require(
            pending_coordinates,
            f"selector {full['selector']} owns no pending coordinates",
        )
        signatures = {
            ENGINE.site_signature(site, record_sets)
            for site in candidate_sites
        }
        profile = {
            **full,
            "candidate_roots": candidate_roots,
            "candidate_sites": candidate_sites,
            "pending_coordinates": pending_coordinates,
            "reachable_roots": owned_roots,
            "site_roots": candidate_roots | source_roots,
            "source_only_sites": set(source_sites) - set(candidate_sites),
            "source_sites": source_sites,
            "template_signatures": signatures,
        }
        profiles.append(profile)

    require(
        len(owner_by_root) == EXPECTED_PENDING_ROOTS,
        "owned pending root count drifted",
    )
    require(
        len(profiles) == EXPECTED_OWNER_SELECTORS,
        "owner selector count drifted",
    )
    all_coordinates = {
        coordinate
        for profile in profiles
        for coordinate in profile["pending_coordinates"]
    }
    require(
        len(all_coordinates) == EXPECTED_PENDING_COORDINATES,
        "owned pending coordinate union drifted",
    )
    require(
        len(all_coordinates)
        == sum(len(profile["pending_coordinates"]) for profile in profiles),
        "pending coordinate ownership overlap",
    )
    return profiles, skipped_selectors


def packet_weight(packet: Mapping[str, Any]) -> tuple[int, int]:
    scope = packet["scope"]
    return (
        int(scope["pending_coordinate_count"]),
        int(scope["candidate_site_count"]),
    )


def imbalance(values: Sequence[int]) -> int:
    return sum(
        abs(values[left] - values[right])
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )


def bundle_objective(
    bundles: Sequence[Mapping[str, Any]],
    *,
    pending_scale: int,
    site_scale: int,
) -> tuple[int, int, int, int, int]:
    pending = [int(row["pending_coordinate_count"]) for row in bundles]
    sites = [int(row["candidate_site_count"]) for row in bundles]
    pending_imbalance = imbalance(pending)
    site_imbalance = imbalance(sites)
    return (
        pending_imbalance * site_scale + site_imbalance * pending_scale,
        pending_imbalance,
        site_imbalance,
        max(pending) - min(pending),
        max(sites) - min(sites),
    )


def balance_bundles(
    packets: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[int, int]]:
    require(
        len(packets) >= AGENT_BUNDLE_COUNT,
        "not enough owner packets for agent bundles",
    )
    total_pending = sum(packet_weight(packet)[0] for packet in packets)
    total_sites = sum(packet_weight(packet)[1] for packet in packets)
    pending_scale = max(total_pending, 1)
    site_scale = max(total_sites, 1)
    packets_by_id = {
        int(packet["packet_id"]): packet for packet in packets
    }
    ordered = sorted(
        packets,
        key=lambda packet: (
            -(
                packet_weight(packet)[0] * site_scale
                + packet_weight(packet)[1] * pending_scale
            ),
            -packet_weight(packet)[0],
            -packet_weight(packet)[1],
            int(packet["rank"]),
            int(packet["packet_id"]),
        ),
    )
    bundles = [
        {
            "bundle_id": index,
            "candidate_site_count": 0,
            "packet_ids": [],
            "pending_coordinate_count": 0,
        }
        for index in range(AGENT_BUNDLE_COUNT)
    ]
    for packet in ordered:
        packet_id = int(packet["packet_id"])
        pending, sites = packet_weight(packet)
        choices = []
        for index in range(AGENT_BUNDLE_COUNT):
            projected = [
                {
                    **bundle,
                    "packet_ids": list(bundle["packet_ids"]),
                }
                for bundle in bundles
            ]
            projected[index]["pending_coordinate_count"] += pending
            projected[index]["candidate_site_count"] += sites
            projected[index]["packet_ids"].append(packet_id)
            choices.append((
                bundle_objective(
                    projected,
                    pending_scale=pending_scale,
                    site_scale=site_scale,
                ),
                len(projected[index]["packet_ids"]),
                index,
            ))
        index = min(choices)[-1]
        bundles[index]["pending_coordinate_count"] += pending
        bundles[index]["candidate_site_count"] += sites
        bundles[index]["packet_ids"].append(packet_id)

    while True:
        current = bundle_objective(
            bundles, pending_scale=pending_scale, site_scale=site_scale
        )
        choices = []
        for left in range(AGENT_BUNDLE_COUNT):
            for right in range(left + 1, AGENT_BUNDLE_COUNT):
                for left_id in sorted(bundles[left]["packet_ids"]):
                    for right_id in sorted(bundles[right]["packet_ids"]):
                        lp, ls = packet_weight(packets_by_id[left_id])
                        rp, rs = packet_weight(packets_by_id[right_id])
                        projected = [
                            {
                                **bundle,
                                "packet_ids": list(bundle["packet_ids"]),
                            }
                            for bundle in bundles
                        ]
                        projected[left]["pending_coordinate_count"] += rp - lp
                        projected[left]["candidate_site_count"] += rs - ls
                        projected[right]["pending_coordinate_count"] += lp - rp
                        projected[right]["candidate_site_count"] += ls - rs
                        choices.append((
                            bundle_objective(
                                projected,
                                pending_scale=pending_scale,
                                site_scale=site_scale,
                            ),
                            left,
                            right,
                            left_id,
                            right_id,
                        ))
        best = min(choices)
        if best[0] >= current:
            break
        _objective, left, right, left_id, right_id = best
        lp, ls = packet_weight(packets_by_id[left_id])
        rp, rs = packet_weight(packets_by_id[right_id])
        bundles[left]["packet_ids"].remove(left_id)
        bundles[left]["packet_ids"].append(right_id)
        bundles[right]["packet_ids"].remove(right_id)
        bundles[right]["packet_ids"].append(left_id)
        bundles[left]["pending_coordinate_count"] += rp - lp
        bundles[left]["candidate_site_count"] += rs - ls
        bundles[right]["pending_coordinate_count"] += lp - rp
        bundles[right]["candidate_site_count"] += ls - rs

    packet_to_bundle: dict[int, int] = {}
    rows = []
    for bundle in bundles:
        packet_ids = sorted(
            map(int, bundle["packet_ids"]),
            key=lambda packet_id: (
                int(packets_by_id[packet_id]["rank"]),
                packet_id,
            ),
        )
        for packet_id in packet_ids:
            require(
                packet_id not in packet_to_bundle,
                "packet assigned to multiple bundles",
            )
            packet_to_bundle[packet_id] = int(bundle["bundle_id"])
        bundle_packets = [packets_by_id[packet_id] for packet_id in packet_ids]
        rows.append({
            "bundle_id": int(bundle["bundle_id"]),
            "candidate_site_count":
                sum(packet_weight(packet)[1] for packet in bundle_packets),
            "packet_count": len(packet_ids),
            "packet_ids": packet_ids,
            "pending_coordinate_count":
                sum(packet_weight(packet)[0] for packet in bundle_packets),
            "selectors": [
                int(packet["scope"]["selector_coordinate"].split(":")[1])
                for packet in bundle_packets
            ],
            "selection_ranks": [
                int(packet["rank"]) for packet in bundle_packets
            ],
            "reachable_pending_root_count": sum(
                int(packet["scope"]["reachable_pending_root_count"])
                for packet in bundle_packets
            ),
            "source_only_site_count": sum(
                int(packet["scope"]["source_only_site_count"])
                for packet in bundle_packets
            ),
            "terminal_row_count": sum(
                len(packet["terminal_manifest"]) for packet in bundle_packets
            ),
        })
    require(
        len(packet_to_bundle) == len(packets),
        "agent bundles do not cover every owner packet",
    )
    return rows, packet_to_bundle


def validate_global_disjointness(
    packets: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    owners: dict[str, dict[str, int]] = {
        "roots": {},
        "pending_coordinates": {},
        "candidate_sites": {},
        "source_sites": {},
    }
    pairwise = []
    for packet in packets:
        packet_id = int(packet["packet_id"])
        sets = {
            "roots": {
                str(row["root"]) for row in packet["root_contexts"]
            },
            "pending_coordinates": {
                str(value)
                for row in packet["root_contexts"]
                for value in row["pending_coordinates"]
            },
            "candidate_sites": {
                str(row["site"]) for row in packet["site_contexts"]
            },
            "source_sites": (
                {
                    str(row["site"]) for row in packet["site_contexts"]
                }
                | {
                    site
                    for site in (
                        str(value)
                        for value in packet.get("_source_sites", ())
                    )
                }
            ),
        }
        for dimension, values in sets.items():
            if dimension in {"candidate_sites", "source_sites"}:
                for value in values:
                    owners[dimension].setdefault(value, packet_id)
                continue
            overlap = set(owners[dimension]) & values
            require(
                not overlap,
                f"global {dimension} ownership overlap: {sorted(overlap)[:3]}",
            )
            for value in values:
                owners[dimension][value] = packet_id
    for left in range(len(packets)):
        left_roots = {
            str(row["root"]) for row in packets[left]["root_contexts"]
        }
        left_coordinates = {
            str(value)
            for row in packets[left]["root_contexts"]
            for value in row["pending_coordinates"]
        }
        for right in range(left + 1, len(packets)):
            right_roots = {
                str(row["root"]) for row in packets[right]["root_contexts"]
            }
            right_coordinates = {
                str(value)
                for row in packets[right]["root_contexts"]
                for value in row["pending_coordinates"]
            }
            pairwise.append({
                "left_packet_id": int(packets[left]["packet_id"]),
                "owned_pending_coordinate_overlap":
                    len(left_coordinates & right_coordinates),
                "owned_root_overlap": len(left_roots & right_roots),
                "right_packet_id": int(packets[right]["packet_id"]),
            })
    require(
        all(
            row["owned_pending_coordinate_overlap"] == 0
            and row["owned_root_overlap"] == 0
            for row in pairwise
        ),
        "pairwise owner overlap",
    )
    return {
        "candidate_site_count": len(owners["candidate_sites"]),
        "candidate_site_sha256":
            ENGINE.site_digest(set(owners["candidate_sites"])),
        "owned_pending_coordinate_count":
            len(owners["pending_coordinates"]),
        "owned_pending_coordinate_sha256":
            ENGINE.coordinate_digest(set(owners["pending_coordinates"])),
        "owned_root_count": len(owners["roots"]),
        "owned_root_sha256": ENGINE.root_digest({
            parse_root(root) for root in owners["roots"]
        }),
        "pair_count": len(pairwise),
        "pairwise": pairwise,
        "source_site_count": len(owners["source_sites"]),
        "source_site_sha256": ENGINE.site_digest(set(owners["source_sites"])),
    }


def build_outputs() -> tuple[
    bytes,
    bytes,
    dict[Path, bytes],
    dict[str, Any],
]:
    require(RANKING_PRIVATE_PATH.is_file(), "wave6 ranking private absent")
    require(
        sha256_file(BASE_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "base assignment builder drifted",
    )
    require(
        sha256_file(RANKING_BUILDER_PATH)
        == EXPECTED_RANKING_BUILDER_SHA256,
        "wave6 ranking builder drifted",
    )
    require(
        sha256_file(RANKING_PRIVATE_PATH)
        == EXPECTED_RANKING_PRIVATE_SHA256,
        "wave6 ranking private drifted",
    )
    RANKING.configure_ranking()
    ranking_private, _ranking_public, _inputs = RANKING.build_outputs()
    require(
        json.loads(RANKING_PRIVATE_PATH.read_text(encoding="utf-8"))
        == ranking_private,
        "wave6 ranking private object drifted",
    )
    RANKING.configure_ranking()
    world = ENGINE.load_world(RANKING)
    profiles, skipped_selectors = owner_profiles(ranking_private, world)

    original_method = ENGINE.METHOD
    original_wave_id = ENGINE.WAVE_ID
    try:
        ENGINE.METHOD = METHOD
        ENGINE.WAVE_ID = WAVE_ID
        packets = [
            ENGINE.build_packet(
                profile, packet_id=index, world=world
            )
            for index, profile in enumerate(profiles)
        ]
    finally:
        ENGINE.METHOD = original_method
        ENGINE.WAVE_ID = original_wave_id

    # Keep source-site ownership available for validation only; strip it from
    # each packet before serialization because the standard packet contract
    # already commits source/source-only counts and digests.
    for packet, profile in zip(packets, profiles):
        packet["_source_sites"] = list(profile["source_sites"])
        owned_coordinates = set(profile["pending_coordinates"])
        for site_row in packet["site_contexts"]:
            site_row["pending_coordinates"] = [
                coordinate
                for coordinate in site_row["pending_coordinates"]
                if coordinate in owned_coordinates
            ]
            site_row["branch_validation_only"] = (
                site_root(str(site_row["site"]))
                not in profile["reachable_roots"]
            )
        packet["agent_contract"]["global_root_shard_assignment"] = True
        packet["agent_contract"]["nonowner_site_context_read_only"] = True
        packet["agent_contract"]["owner_selector_rank"] = int(profile["rank"])
        packet["agent_contract"]["source_only_action_count"] = 0
        packet["agent_contract"]["steam_write_authorized"] = False
        packet["scope"]["ownership_policy"] = (
            "highest_ranked_eligible_selector_per_pending_root"
        )

    disjointness = validate_global_disjointness(packets)
    require(
        world["candidate_sha256"] == EXPECTED_CANDIDATE_SHA256,
        "candidate changed before root-sharded assignment freeze",
    )
    require(
        disjointness["owned_pending_coordinate_count"]
        == EXPECTED_PENDING_COORDINATES,
        "global owned coordinate count drifted",
    )
    require(
        disjointness["owned_root_count"] == EXPECTED_PENDING_ROOTS,
        "global owned root count drifted",
    )
    bundles, packet_to_bundle = balance_bundles(packets)
    packet_outputs: dict[Path, bytes] = {}
    for packet in packets:
        packet_id = int(packet["packet_id"])
        packet["bundle_id"] = packet_to_bundle[packet_id]
        packet.pop("_source_sites")
        selector = packet["scope"]["selector_coordinate"].split(":")[1]
        packet_outputs[
            PACKET_DIR / f"selector{selector}.private.v1.json"
        ] = ENGINE.serialized_private(packet)

    assignment = {
        "agent_bundle_manifest": {
            "balance_dimensions": [
                "pending_coordinate_count",
                "candidate_site_count",
            ],
            "bundle_count": AGENT_BUNDLE_COUNT,
            "bundles": bundles,
            "exact_disjoint_packet_assignment": True,
        },
        "constraints": {
            "changed_branches_only": True,
            "full_integration_rebuild_authorized": False,
            "jp_authoritative": True,
            "nonpending_root_actions_authorized": False,
            "source_only_action_count": 0,
            "steam_write_authorized": False,
            "terminal_rows_read_only": True,
        },
        "global_disjointness": disjointness,
        "inputs": {
            "base_builder_sha256": sha256_file(BASE_PATH),
            "candidate_sha256": world["candidate_sha256"],
            "ranking_builder_sha256": sha256_file(RANKING_BUILDER_PATH),
            "ranking_private_sha256": sha256_file(RANKING_PRIVATE_PATH),
        },
        "method": METHOD,
        "owner_assignment": [
            {
                "bundle_id": packet_to_bundle[int(packet["packet_id"])],
                "candidate_site_count":
                    int(packet["scope"]["candidate_site_count"]),
                "owner_rank": int(packet["rank"]),
                "packet_id": int(packet["packet_id"]),
                "pending_coordinate_count":
                    int(packet["scope"]["pending_coordinate_count"]),
                "reachable_pending_root_count":
                    int(packet["scope"]["reachable_pending_root_count"]),
                "selector":
                    int(
                        packet["scope"]["selector_coordinate"].split(":")[1]
                    ),
                "source_only_site_count":
                    int(packet["scope"]["source_only_site_count"]),
            }
            for packet in packets
        ],
        "packet_artifacts": [
            {
                "basename": path.name,
                "packet_id": packet_id,
                "sha256": sha256_bytes(content),
            }
            for packet_id, (path, content) in enumerate(packet_outputs.items())
        ],
        "result": {
            "eligible_family_count": EXPECTED_ELIGIBLE_FAMILIES,
            "owner_packet_count": len(packets),
            "owned_pending_coordinate_count":
                disjointness["owned_pending_coordinate_count"],
            "owned_pending_root_count": disjointness["owned_root_count"],
            "skipped_fully_shadowed_selector_count": len(skipped_selectors),
            "total_candidate_sites":
                sum(
                    int(packet["scope"]["candidate_site_count"])
                    for packet in packets
                ),
            "total_source_only_sites":
                sum(
                    int(packet["scope"]["source_only_site_count"])
                    for packet in packets
                ),
        },
        "schema": SCHEMA,
        "skipped_fully_shadowed_selectors": skipped_selectors,
        "status": "READY",
        "steam_write_performed": False,
        "wave_id": WAVE_ID,
    }
    private_bytes = ENGINE.serialized_private(assignment)
    private_sha256 = sha256_bytes(private_bytes)
    require(
        private_sha256 == EXPECTED_PRIVATE_SHA256,
        "private root-sharded assignment drifted",
    )
    public = {
        "agent_bundle_manifest": assignment["agent_bundle_manifest"],
        "constraints": assignment["constraints"],
        "global_disjointness": {
            key: value
            for key, value in disjointness.items()
            if key != "pairwise"
        },
        "guards": {
            **assignment["inputs"],
            "private_assignment_sha256": private_sha256,
        },
        "method": METHOD,
        "owner_assignment": assignment["owner_assignment"],
        "packet_artifacts": assignment["packet_artifacts"],
        "privacy": {
            "contains_candidate_text": False,
            "contains_context_text": False,
            "contains_source_text": False,
            "contains_terminal_text": False,
            "source_private_packet_count": len(packet_outputs),
        },
        "result": assignment["result"],
        "schema": (
            "nobu16.kr.pk-dialogue-wave7-root-sharded-"
            "assignment.source-free.v1"
        ),
        "skipped_fully_shadowed_selectors":
            assignment["skipped_fully_shadowed_selectors"],
        "status": assignment["status"],
        "steam_write_performed": False,
        "wave_id": WAVE_ID,
    }
    ENGINE.assert_source_free(public)
    public_bytes = ENGINE.serialized_public(public)
    require(
        EXPECTED_PUBLIC_SHA256 is None
        or sha256_bytes(public_bytes) == EXPECTED_PUBLIC_SHA256,
        "public root-sharded assignment drifted",
    )
    return private_bytes, public_bytes, packet_outputs, assignment


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    private_bytes, public_bytes, packet_outputs, assignment = build_outputs()
    output_map = {
        DEFAULT_OUTPUT: private_bytes,
        DEFAULT_PUBLIC_OUTPUT: public_bytes,
        **packet_outputs,
    }
    if args.bootstrap:
        for path, content in output_map.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in output_map.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"root-sharded wave7 output drifted: {path}",
            )
    print(json.dumps({
        "agent_bundles":
            assignment["agent_bundle_manifest"]["bundles"],
        "candidate_sha256": assignment["inputs"]["candidate_sha256"],
        "owner_packet_count": assignment["result"]["owner_packet_count"],
        "owned_pending_coordinates":
            assignment["result"]["owned_pending_coordinate_count"],
        "owned_pending_roots":
            assignment["result"]["owned_pending_root_count"],
        "private_sha256": sha256_bytes(private_bytes),
        "public_sha256": sha256_bytes(public_bytes),
        "skipped_fully_shadowed_selectors":
            assignment["result"]["skipped_fully_shadowed_selector_count"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
