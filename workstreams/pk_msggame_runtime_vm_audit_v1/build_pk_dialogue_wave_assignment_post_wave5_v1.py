#!/usr/bin/env python3
"""Build the wide wave-6 PK dialogue assignment after consolidated wave 5."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

PREDECESSOR_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave4_v1.py"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "3B30CB7CDF861C42F7DBA5731FE2D1BEB1DBF05057AA86348758ADFFB583A745"
)
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave5_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292_wave6.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.post_wave5.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v6"
AGENT_BUNDLE_COUNT = 3

METHOD = (
    "post_selector292_wave5_rank_order_greedy_wide_eighteen_way_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave6"
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "DE1082D629B91D52EAA946005D7783E31506A963D7D9793E35D4F292CF6C710E",
    "ranking_private":
        "071D7F15C860B8F8D051C89815CFC591BBC65F7B8FE12D1C779796C6F38E21F7",
    "ranking_public":
        "29D3286D710C9B4072ECA71A18C7EC11270163315F7022227D02BAFCF234E46B",
    "ledger":
        "ABC78C74996A5C9467DB92C1EBB55A940A2A39099E9A12A5D565954D4AB68F12",
    "checkpoint_public":
        "D2928654B9CD246366567E5FF996EB0A58F9044962EADBB79F3921BA2ABC680A",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (
    772, 160, 616, 280, 1204, 256, 634, 778, 298,
    898, 1036, 1072, 70, 850, 862, 928, 940, 202,
)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (
    1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 17, 19, 20, 21, 22, 23,
)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "E155972D94C9EA29288175FBE3644EA1B9F7010A96B238A18213F7C6B58CCCE5"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "31BBC15DC747C262F82B1E139C9CB3120BA2942020C6FD95CA83B6349B1ADA8E",
    "A0CC87E8C042BE8664D08B5D5B1E0ECB02ACE583208B2B5C21B1F5ED68AFC1DD",
    "ED89DACE41471D79C01579A8AB2A2D4CCC15D9479C2463F5E1432103D5E4146D",
    "83F2604DE7468AD026500EAFFFB865680D989F12B67810B2706A4E4F62DDC1EB",
    "627B4DA52BC8D4EF4CAB6BAD91D8FE6D4436CA9B53E767E549D16259A2A92221",
    "AC225D05FC9CEE225581271B9B851D64A9569AC526AF88398B221B12136753CC",
    "8FB848C54043E8B5A2F167239271EF401210614FB9EE24DD56A7FFB4D3B34950",
    "F0F9B367D848E061C1207C67050DB301DEDF7B84A2F49D22A242498B44727133",
    "496679FBB154099248B1D9E9FA9622B9C2E5E210F4F6ED804A86DFF0CA05E82A",
    "392AB39CCB87ABED820492897550BF3CE07A44E51E28D33B6D92BFD8EDEFA43C",
    "6EE6B994BBCC20F7ACF35928E5E272C926221CC6D406E21ACC333A53E4F99E07",
    "CBB6154BD81B8F25429AD6F22E242670FDEAA6346F41F2FAC9D2063B1C94BEA1",
    "6A04F6900270F2D35754D70878C664D4977A3689CAFC13B7414BC2722A59F4A4",
    "0A599621BBFA8745ABD2E2F813B0085B7F40FD4933ABAB3C3F5F0F0D1BA00F47",
    "2B80D808023CD1881925ED45F97BE768FBF6C270315CF284D09064FDD07BC705",
    "D4E77CDEC7562AC8B1DB7B5174A0C4CA44D4EB15D3A6F45080AE9BD480DA3992",
    "1133C81193FFDCABE93BF4BA86B0EB6D63EBAA433CC9FA945E2D201850D2DCF4",
    "57836A89B2DA8BA44C78F1116D5E48AE602C3E98AAF1BBE5E81F4765F584B97E",
)
EXPECTED_BUNDLE_MANIFEST_SHA256: str | None = (
    "8E30B2977F32AB46C032D47B7991E8541D009C985F1AE4A28F0AE49623FF9A1D"
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "5FBBD6DCFDF7092EFCE17B74513F004AFA2413C4420E88BFA21A3150D2425610"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "F96FEF252D208E1CF3229A66E07B791540C66108ED5C756AD251873CDEEBFE23"
)

# This fallback is deliberately read-only.  It exists only so the wide
# selector/bundle mechanics can be exercised before the wave-5 closure and
# ranking are frozen.  It must never be used by --bootstrap, --write, or
# --check.
PROTOTYPE_RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave4_v1.py"
)
PROTOTYPE_RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.private.v1.json"
)
PROTOTYPE_RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.source_free.v1.json"
)
PROTOTYPE_VIRTUAL_OUTPUT_ROOT = TMP / "_wave6_read_only_prototype"
PROTOTYPE_EXPECTED_INPUT_SHA256 = {
    "ranking_builder":
        "C9C283FB540888BE8897167B930FEB64552428C4BD0236EA1DE54467E67C76B6",
    "ranking_private":
        "F3F4C736EA138883D9795E6B8AFB5079FF866179AE6026002AFCDFD12B67B7FE",
    "ranking_public":
        "8031A39CC75AE935FCEAD31EBFFF7F9897776AE75A4F560F36599862C3D41797",
    "ledger":
        "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE",
    "checkpoint_public":
        "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB",
}
PROTOTYPE_EXPECTED_CANDIDATE_SHA256 = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)

FINAL_PIN_NAMES = (
    "EXPECTED_CANDIDATE_SHA256",
    "EXPECTED_SELECTED_SELECTORS",
    "EXPECTED_SELECTION_RANKS",
    "EXPECTED_SELECTION_PROFILE_SHA256",
    "EXPECTED_PACKET_SHA256",
    "EXPECTED_BUNDLE_MANIFEST_SHA256",
    "EXPECTED_PRIVATE_SHA256",
    "EXPECTED_PUBLIC_SHA256",
)


class Wave6AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave6AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(PREDECESSOR_PATH, "pk_dialogue_wave6_assignment_base")
ENGINE = BASE.ENGINE
CORE_BUILD_OUTPUTS = BASE.CORE_BUILD_OUTPUTS


FINAL_ENGINE_CONFIG = {
    "RANKING_BUILDER_PATH": RANKING_BUILDER_PATH,
    "RANKING_PRIVATE_PATH": RANKING_PRIVATE_PATH,
    "RANKING_PUBLIC_PATH": RANKING_PUBLIC_PATH,
    "DEFAULT_PRIVATE_OUTPUT": DEFAULT_PRIVATE_OUTPUT,
    "DEFAULT_PUBLIC_OUTPUT": DEFAULT_PUBLIC_OUTPUT,
    "PACKET_DIR": PACKET_DIR,
    "METHOD": METHOD,
    "WAVE_ID": WAVE_ID,
    "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
    "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
    "EXPECTED_SELECTED_SELECTORS": EXPECTED_SELECTED_SELECTORS,
    "EXPECTED_SELECTION_RANKS": EXPECTED_SELECTION_RANKS,
    "EXPECTED_SELECTION_PROFILE_SHA256": EXPECTED_SELECTION_PROFILE_SHA256,
    "EXPECTED_PACKET_SHA256": EXPECTED_PACKET_SHA256,
    "EXPECTED_PRIVATE_SHA256": EXPECTED_PRIVATE_SHA256,
    "EXPECTED_PUBLIC_SHA256": EXPECTED_PUBLIC_SHA256,
    "MAX_SELECTORS": 18,
}
PROTOTYPE_ENGINE_CONFIG = {
    **FINAL_ENGINE_CONFIG,
    "RANKING_BUILDER_PATH": PROTOTYPE_RANKING_BUILDER_PATH,
    "RANKING_PRIVATE_PATH": PROTOTYPE_RANKING_PRIVATE_PATH,
    "RANKING_PUBLIC_PATH": PROTOTYPE_RANKING_PUBLIC_PATH,
    "DEFAULT_PRIVATE_OUTPUT":
        PROTOTYPE_VIRTUAL_OUTPUT_ROOT / "assignment.private.v1.json",
    "DEFAULT_PUBLIC_OUTPUT":
        PROTOTYPE_VIRTUAL_OUTPUT_ROOT / "assignment.source_free.v1.json",
    "PACKET_DIR": PROTOTYPE_VIRTUAL_OUTPUT_ROOT / "packets",
    "EXPECTED_INPUT_SHA256": PROTOTYPE_EXPECTED_INPUT_SHA256,
    "EXPECTED_CANDIDATE_SHA256": PROTOTYPE_EXPECTED_CANDIDATE_SHA256,
    "EXPECTED_SELECTED_SELECTORS": None,
    "EXPECTED_SELECTION_RANKS": None,
    "EXPECTED_SELECTION_PROFILE_SHA256": None,
    "EXPECTED_PACKET_SHA256": None,
    "EXPECTED_PRIVATE_SHA256": None,
    "EXPECTED_PUBLIC_SHA256": None,
}

for _name, _value in FINAL_ENGINE_CONFIG.items():
    setattr(ENGINE, _name, _value)


def unresolved_final_pins() -> list[str]:
    missing = [
        f"EXPECTED_INPUT_SHA256[{name}]"
        for name, value in EXPECTED_INPUT_SHA256.items()
        if value is None
    ]
    missing.extend(
        name for name in FINAL_PIN_NAMES if globals()[name] is None
    )
    return missing


@contextmanager
def engine_configuration(
    values: Mapping[str, Any],
) -> Iterator[None]:
    """Temporarily configure the inherited engine without leaking state."""
    previous = {
        name: getattr(ENGINE, name) for name in values
    }
    try:
        for name, value in values.items():
            setattr(ENGINE, name, value)
        yield
    finally:
        for name, value in previous.items():
            setattr(ENGINE, name, value)


def packet_selector(packet: Mapping[str, Any]) -> int:
    return int(packet["scope"]["selector_coordinate"].split(":")[1])


def packet_load(packet: Mapping[str, Any]) -> tuple[int, int]:
    scope = packet["scope"]
    return (
        int(scope["pending_coordinate_count"]),
        int(scope["candidate_site_count"]),
    )


def pairwise_imbalance(values: Sequence[int]) -> int:
    return sum(
        abs(values[left] - values[right])
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )


def assign_agent_bundles(
    packets: Sequence[Mapping[str, Any]],
    packet_artifacts: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[int, int]]:
    """Balance packets deterministically across three agent bundles.

    Packets are scheduled largest-first using a dimension-normalized combined
    pending-row/candidate-site weight.  For each placement, the same normalized
    pairwise imbalance is minimized across all bundles.  Integer arithmetic and
    explicit tie-breaks make the result reproducible.
    """
    require(
        len(packets) == 18,
        "wide wave must contain exactly eighteen selector packets",
    )
    require(
        len(packet_artifacts) == len(packets),
        "packet artifact manifest length drifted",
    )
    artifacts_by_id = {
        int(row["packet_id"]): row for row in packet_artifacts
    }
    require(
        len(artifacts_by_id) == len(packets),
        "packet artifact ids are not unique",
    )
    total_pending = sum(packet_load(packet)[0] for packet in packets)
    total_sites = sum(packet_load(packet)[1] for packet in packets)
    pending_scale = max(total_pending, 1)
    site_scale = max(total_sites, 1)
    order = sorted(
        packets,
        key=lambda packet: (
            -(
                packet_load(packet)[0] * site_scale
                + packet_load(packet)[1] * pending_scale
            ),
            -packet_load(packet)[0],
            -packet_load(packet)[1],
            int(packet["rank"]),
            packet_selector(packet),
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
    packets_by_id = {
        int(packet["packet_id"]): packet for packet in packets
    }
    packet_to_bundle: dict[int, int] = {}
    for packet in order:
        packet_id = int(packet["packet_id"])
        pending_count, site_count = packet_load(packet)
        choices = []
        for bundle_index in range(AGENT_BUNDLE_COUNT):
            projected_pending = [
                int(bundle["pending_coordinate_count"])
                + (pending_count if index == bundle_index else 0)
                for index, bundle in enumerate(bundles)
            ]
            projected_sites = [
                int(bundle["candidate_site_count"])
                + (site_count if index == bundle_index else 0)
                for index, bundle in enumerate(bundles)
            ]
            pending_imbalance = pairwise_imbalance(projected_pending)
            site_imbalance = pairwise_imbalance(projected_sites)
            normalized_imbalance = (
                pending_imbalance * site_scale
                + site_imbalance * pending_scale
            )
            choices.append((
                normalized_imbalance,
                pending_imbalance,
                site_imbalance,
                projected_pending[bundle_index] * site_scale
                + projected_sites[bundle_index] * pending_scale,
                len(bundles[bundle_index]["packet_ids"]),
                bundle_index,
            ))
        bundle_index = min(choices)[-1]
        bundle = bundles[bundle_index]
        bundle["packet_ids"].append(packet_id)
        bundle["pending_coordinate_count"] += pending_count
        bundle["candidate_site_count"] += site_count
        packet_to_bundle[packet_id] = bundle_index

    def bundle_objective(
        current_bundles: Sequence[Mapping[str, Any]],
    ) -> tuple[int, int, int, int, int]:
        pending_values = [
            int(bundle["pending_coordinate_count"])
            for bundle in current_bundles
        ]
        site_values = [
            int(bundle["candidate_site_count"])
            for bundle in current_bundles
        ]
        pending_imbalance = pairwise_imbalance(pending_values)
        site_imbalance = pairwise_imbalance(site_values)
        return (
            pending_imbalance * site_scale
            + site_imbalance * pending_scale,
            pending_imbalance,
            site_imbalance,
            max(pending_values) - min(pending_values),
            max(site_values) - min(site_values),
        )

    # A deterministic pair-swap descent removes avoidable two-dimensional
    # imbalance left by the fast greedy pass while preserving six packets per
    # agent.  It is bounded by a strictly decreasing integer objective.
    while True:
        current_objective = bundle_objective(bundles)
        swap_candidates = []
        for left_index in range(AGENT_BUNDLE_COUNT):
            for right_index in range(left_index + 1, AGENT_BUNDLE_COUNT):
                for left_id in sorted(bundles[left_index]["packet_ids"]):
                    for right_id in sorted(bundles[right_index]["packet_ids"]):
                        left_pending, left_sites = packet_load(
                            packets_by_id[int(left_id)]
                        )
                        right_pending, right_sites = packet_load(
                            packets_by_id[int(right_id)]
                        )
                        projected = [
                            {
                                **bundle,
                                "packet_ids": list(bundle["packet_ids"]),
                            }
                            for bundle in bundles
                        ]
                        projected[left_index]["pending_coordinate_count"] += (
                            right_pending - left_pending
                        )
                        projected[left_index]["candidate_site_count"] += (
                            right_sites - left_sites
                        )
                        projected[right_index]["pending_coordinate_count"] += (
                            left_pending - right_pending
                        )
                        projected[right_index]["candidate_site_count"] += (
                            left_sites - right_sites
                        )
                        swap_candidates.append((
                            bundle_objective(projected),
                            left_index,
                            right_index,
                            int(left_id),
                            int(right_id),
                        ))
        best = min(swap_candidates)
        if best[0] >= current_objective:
            break
        _objective, left_index, right_index, left_id, right_id = best
        left_pending, left_sites = packet_load(packets_by_id[left_id])
        right_pending, right_sites = packet_load(packets_by_id[right_id])
        bundles[left_index]["packet_ids"].remove(left_id)
        bundles[left_index]["packet_ids"].append(right_id)
        bundles[right_index]["packet_ids"].remove(right_id)
        bundles[right_index]["packet_ids"].append(left_id)
        bundles[left_index]["pending_coordinate_count"] += (
            right_pending - left_pending
        )
        bundles[left_index]["candidate_site_count"] += (
            right_sites - left_sites
        )
        bundles[right_index]["pending_coordinate_count"] += (
            left_pending - right_pending
        )
        bundles[right_index]["candidate_site_count"] += (
            left_sites - right_sites
        )
        packet_to_bundle[left_id] = right_index
        packet_to_bundle[right_id] = left_index

    private_rows = []
    public_rows = []
    seen_packet_ids: set[int] = set()
    for bundle in bundles:
        packet_ids = sorted(
            map(int, bundle["packet_ids"]),
            key=lambda packet_id: (
                int(packets_by_id[packet_id]["rank"]),
                packet_selector(packets_by_id[packet_id]),
                packet_id,
            ),
        )
        require(
            not (seen_packet_ids & set(packet_ids)),
            "agent bundle packet overlap",
        )
        seen_packet_ids.update(packet_ids)
        bundle_packets = [packets_by_id[packet_id] for packet_id in packet_ids]
        selectors = [packet_selector(packet) for packet in bundle_packets]
        ranks = [int(packet["rank"]) for packet in bundle_packets]
        packet_hashes = [
            str(artifacts_by_id[packet_id]["sha256"])
            for packet_id in packet_ids
        ]
        public_row = {
            "bundle_id": int(bundle["bundle_id"]),
            "candidate_site_count":
                sum(packet_load(packet)[1] for packet in bundle_packets),
            "packet_count": len(packet_ids),
            "packet_ids": packet_ids,
            "packet_sha256": packet_hashes,
            "pending_coordinate_count":
                sum(packet_load(packet)[0] for packet in bundle_packets),
            "selection_ranks": ranks,
            "selectors": selectors,
        }
        public_rows.append(public_row)
        private_rows.append({
            **public_row,
            "packet_basenames": [
                str(artifacts_by_id[packet_id]["basename"])
                for packet_id in packet_ids
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
                len(packet["terminal_manifest"])
                for packet in bundle_packets
            ),
        })
    require(
        seen_packet_ids == set(packets_by_id),
        "agent bundles do not exactly cover selector packets",
    )
    require(
        set(packet_to_bundle) == set(packets_by_id),
        "packet-to-bundle mapping is incomplete",
    )
    public_manifest = {
        "balance_totals": {
            "candidate_site_count": total_sites,
            "pending_coordinate_count": total_pending,
        },
        "bundle_count": AGENT_BUNDLE_COUNT,
        "bundles": public_rows,
        "exact_disjoint_packet_assignment": True,
        "policy": (
            "normalized_pending_rows_and_candidate_sites_"
            "largest_first_minimum_pairwise_imbalance_v1"
        ),
    }
    private_manifest = {
        **public_manifest,
        "bundles": private_rows,
    }
    return private_manifest, packet_to_bundle


def attach_bundle_manifests(
    private_bytes: bytes,
    public_bytes: bytes,
    packet_outputs: Mapping[Path, bytes],
    assignment: dict[str, Any],
    public: dict[str, Any],
    *,
    validate_final_pins: bool,
) -> tuple[bytes, bytes, dict[Path, bytes], dict[str, Any], dict[str, Any]]:
    del private_bytes, public_bytes
    manifest, packet_to_bundle = assign_agent_bundles(
        assignment["packets"], assignment["packet_artifacts"]
    )
    public_manifest = {
        key: value
        for key, value in manifest.items()
        if key != "bundles"
    }
    public_manifest["bundles"] = [
        {
            key: value
            for key, value in row.items()
            if key not in {
                "packet_basenames",
                "reachable_pending_root_count",
                "source_only_site_count",
                "terminal_row_count",
            }
        }
        for row in manifest["bundles"]
    ]
    manifest_sha = ENGINE.canonical_sha256(public_manifest)
    require(
        not validate_final_pins
        or EXPECTED_BUNDLE_MANIFEST_SHA256 is None
        or manifest_sha == EXPECTED_BUNDLE_MANIFEST_SHA256,
        "agent bundle manifest drifted",
    )
    assignment["agent_bundle_manifest"] = manifest
    assignment["agent_bundle_manifest_sha256"] = manifest_sha
    private_bytes = ENGINE.serialized_private(assignment)
    private_sha = ENGINE.sha256_bytes(private_bytes)
    public["agent_bundle_manifest"] = public_manifest
    public["guards"]["agent_bundle_manifest_sha256"] = manifest_sha
    public["guards"]["private_assignment_sha256"] = private_sha
    for row in public["packets"]:
        row["bundle_id"] = packet_to_bundle[int(row["packet_id"])]
    public_bytes = ENGINE.serialized_public(public)
    ENGINE.assert_source_free(public)
    require(
        not validate_final_pins
        or EXPECTED_PRIVATE_SHA256 is None
        or private_sha == EXPECTED_PRIVATE_SHA256,
        "private assignment drifted",
    )
    require(
        not validate_final_pins
        or EXPECTED_PUBLIC_SHA256 is None
        or ENGINE.sha256_bytes(public_bytes) == EXPECTED_PUBLIC_SHA256,
        "public assignment drifted",
    )
    return (
        private_bytes,
        public_bytes,
        dict(packet_outputs),
        assignment,
        public,
    )


def build_outputs(
    *,
    allow_unfrozen: bool = False,
    prototype: bool = False,
) -> tuple[bytes, bytes, dict[Path, bytes], dict[str, Any], dict[str, Any]]:
    require(
        hashlib.sha256(PREDECESSOR_PATH.read_bytes()).hexdigest().upper()
        == EXPECTED_PREDECESSOR_SHA256,
        "post-wave4 assignment predecessor drifted",
    )
    require(
        not (prototype and allow_unfrozen),
        "prototype and final bootstrap modes cannot be combined",
    )
    if not prototype and not allow_unfrozen:
        missing = unresolved_final_pins()
        require(
            not missing,
            "wave6 assignment pins unresolved: " + ", ".join(missing),
        )
    config = (
        PROTOTYPE_ENGINE_CONFIG if prototype else FINAL_ENGINE_CONFIG
    )
    # The inherited engine serializes before bundle metadata exists.  Its
    # private/public output pins are therefore intentionally suppressed here;
    # this wrapper validates the final, bundle-bearing serializations instead.
    core_config = {
        **config,
        "EXPECTED_PRIVATE_SHA256": None,
        "EXPECTED_PUBLIC_SHA256": None,
    }
    with engine_configuration(core_config):
        outputs = CORE_BUILD_OUTPUTS(allow_unfrozen=True)
    return attach_bundle_manifests(
        *outputs,
        validate_final_pins=not prototype,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--prototype", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs(
        allow_unfrozen=args.bootstrap,
        prototype=args.prototype,
    )
    private_bytes, public_bytes, packet_outputs, assignment, public = outputs
    if args.prototype:
        output_map = {
            PROTOTYPE_VIRTUAL_OUTPUT_ROOT / "assignment.private.v1.json":
                private_bytes,
            PROTOTYPE_VIRTUAL_OUTPUT_ROOT
            / "assignment.source_free.v1.json":
                public_bytes,
            **packet_outputs,
        }
        require(
            all(
                str(path).startswith(str(PROTOTYPE_VIRTUAL_OUTPUT_ROOT))
                for path in output_map
            ),
            "prototype output path escaped virtual output root",
        )
    else:
        output_map = {
            DEFAULT_PRIVATE_OUTPUT: private_bytes,
            DEFAULT_PUBLIC_OUTPUT: public_bytes,
            **packet_outputs,
        }
    if args.prototype:
        pass
    elif args.bootstrap or args.write:
        for path, content in output_map.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in output_map.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"wave6 output drifted: {path}",
            )
    print(json.dumps({
        "candidate_sha256": public["guards"]["candidate_sha256"],
        "input_sha256": assignment["inputs"],
        "packet_sha256": [
            row["sha256"] for row in assignment["packet_artifacts"]
        ],
        "private_sha256":
            public["guards"]["private_assignment_sha256"],
        "public_sha256": ENGINE.sha256_bytes(public_bytes),
        "selection_profile_sha256":
            public["guards"]["selection_profile_sha256"],
        "selection_ranks": [
            row["rank"] for row in public["packets"]
        ],
        "selectors": [
            row["selector"] for row in public["packets"]
        ],
        "agent_bundles": public["agent_bundle_manifest"]["bundles"],
        "prototype_read_only": bool(args.prototype),
        "status": public["status"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
