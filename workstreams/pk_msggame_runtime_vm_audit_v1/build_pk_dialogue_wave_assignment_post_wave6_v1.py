#!/usr/bin/env python3
"""Build a maximum-width wave-7 assignment after consolidated wave 6."""

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
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (
        parent
        / "workstreams"
        / "pk_msggame_runtime_vm_audit_v1"
    ).is_dir()
)
WORKSTREAM = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

PREDECESSOR_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave5_v1.py"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "8373B34147AC889C17A4574C5B5CC328EC7C87BDB18CE1DEE7DA3A61E38F54D0"
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
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave6.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292_wave7.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.post_wave6.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v7"
AGENT_BUNDLE_COUNT = 3
MAX_SELECTORS = 38

METHOD = (
    "post_selector292_wave6_rank_order_greedy_maximum_width_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave7"
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "B4FE4B994729E97F515C8F2DE71D0AEA19369339CCCD0334FDBA918EF3A4B356",
    "ranking_private":
        "FED6181AE978C3A476F6DEDEDC80BF995B3B79A740662BFCFBAA6D96E962169A",
    "ranking_public":
        "4C573A461A9E0FF3C1D0056982375434D4C1453E32D3A22B649C79A2D7DB42AA",
    "ledger":
        "7016A0AB5EFD5B0FD223818F860B5757A914188A8EE58C2AD3BE6D14BC393F61",
    "checkpoint_public":
        "987E9644DD5DC235C74E52858546C9196BA15203871A7FE9DDEBF121697435F3",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (
    700, 184, 598, 490, 544, 784, 340, 442, 712, 910,
    1138, 556, 808, 976, 988, 1102, 244, 574, 652, 892,
    1210, 88, 526, 820, 838, 886, 1234, 250, 328, 388,
    856, 958, 1120, 94, 124, 472, 982, 1240,
)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (
    1, 2, 5, 7, 8, 9, 10, 11, 13, 15,
    17, 19, 20, 21, 22, 23, 25, 26, 27, 28,
    29, 30, 34, 35, 36, 37, 38, 39, 40, 41,
    43, 44, 46, 47, 48, 52, 54, 55,
)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "E46A86030E37A7330350EF9D30B405239CB7DFC7CFC8286FEA0262B2616D6F33"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "65374B09FECA671F84BFD42D37ADD5DC2069FA1569D9FC9BFDC2242DA1CE6531",
    "45D2CEFD55F9D22C1418DF8CE63872095D3425F7D16FE430E5D51CDC6495D062",
    "5FFFDE2459C3A1B5BB9D78A1DE6D4956275642716AB8445D80B94BB68A2E5284",
    "D0D864175DE8D85E370F30B5D8FC2AB008A0129388F8AB0B25CCB6AEE6C54DFE",
    "4BA2D75C09880A248FA129F2554EE31251C3DB5665BEA175446DDA59F87E5207",
    "9813F47921E15D60ECBC699264BF23A4A1B4DF915446FAAF143FEA5EA0186455",
    "1613942B630A80CC52355BA946CC03E2A7A210A06D5268B4787F27352AA68596",
    "EFA801625E08D4ED99602212680232DDB4A3F7C346D2699274666E42766BD44B",
    "D4EBC94B63D15C426D107D0518C7D98CA86DF7A67B941BC026E44175E9594AD7",
    "AA0A102E6A3681A461EBE6458A0ABCE7EA00CD0BD46F14747901675E555BA1A6",
    "DF20C849C44BDA730B8B167CE97200FEA0872C1D934AE95F4C52394A3BB6E8D8",
    "A7B5F55BEC4677220344D90DA1A0DC0C8D47563B6A5935E10A072062E7C223DC",
    "67A212002D9C9D6D744EA063966AE3F717E19D8A4EB6A653F4F8DAB4DF416676",
    "D9906F7B14ADE773FE901F54912CBE9F402DB953DB8310C9F5E7EFAF06FEA300",
    "7ED25D41D844346D7113CE294240A6030FC53622888C3AF0B3F26F2A3F94E537",
    "DE5412AA8169F4BB846EAA2A9C4D35F1C2E400335B70F9ACFF05004034C35854",
    "796EC34FDB5A32E80D66F4E118DEA864658A4EA034E218802BAA189E2332E68F",
    "2D0ACED78BEB29FC3B158853BFB92F2B7E4E0D6322F9B5769885AC5F0ABE6ADE",
    "A01E9EA8595D18A30126654C089B80D777CA761666A95B4AF87EF2BB58F97B56",
    "18332F850049EFF94C1397A9C8DBCE1504C372D4861A2C3C30BB3FEFE44A82E8",
    "E95D5A69CCA1B4C750A97BC0AD1011BE4A096FFFADF0D4EBE8F7B8E6C21F2A6F",
    "486BA7A86073531D3E91426F5D8610AD8B2A698701556717CF1CC13F43CE0D34",
    "1E7E9B4013426B98129756C0B8FE46E153ED47757885EF677B674CC2443DD14C",
    "6E5250A89DCDFA5F32C6FC3071BB297D1976DA103E8191241D191ED0B9F1326E",
    "5BBCB36F36FB8B22AC517858FC643E53C619E0C6029D884C26328D100C6B38FD",
    "D756B0CF135AFC2317DE7F45952537FEAFCAF67C8D696E9202494250770AC221",
    "D6469BA0D619B6A81FF3BBCF3EBBA79DD88C2140AF1D1C252388C77A71ED2AB1",
    "3A605B160BBD3CEAE790E6FE35D2C17556743AC9D1E39FC36397734068A38AD8",
    "69D351B43AEECBDCDB41D029CD97AC11C5167C04388389DD941412D45A4E8A24",
    "C666045ED676900A79F3ED40E4F82113AB97494882440AF0F429B063566D56FE",
    "FF43E41B9D95A6F13496C7DF6ADAD560F675EE9B40D15772B6584F3FE743DBD3",
    "2A62E9696A649E01D97B85611463E12C1F7FE7256AE776600F8A6CEF1A66827B",
    "E52B6E6AC8BF123661F602AFF0E321F7AEBEAB9B89E4FB8C761E956FD7858AEC",
    "F5466CDA800ADA499319DE338ABBD4C8EA07988DD265D76F3CDF27D6AC123A9F",
    "555DC1C328083C8D9422A99EF9D69874164175ECFB3A74FBB76BB861918D777F",
    "8FFB43BCD88017C32BA3B122D9FDF540BD6BD264D45CA6E492253B65E3A7B206",
    "13E3B4ECEE487DFFC9C251935524D654A6438666EBFF43E32317E92A5335DC8E",
    "F37F3F6F72042636875D82720D73F77732C6417066AB32FC7E8428AF95B281EB",
)
EXPECTED_BUNDLE_MANIFEST_SHA256: str | None = (
    "13C3ACED1A00BAFB781A9D0C0728C572673DEE0F415C066FBAC5BBA36205A79B"
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "B45AD7AFCF18CADD8D7574DB59EAE7DD23809D01DF11181A2AD16D33BD869825"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "EB3CC3EC82C28B348E306793A3A02E985DCDB8A8DEAE24EAA89C086F78574708"
)

# This fallback is deliberately read-only.  It exists only so the wide
# selector/bundle mechanics can be exercised before the wave-6 closure and
# ranking are frozen.  It must never be used by --bootstrap, --write, or
# --check.
PROTOTYPE_RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave5_v1.py"
)
PROTOTYPE_RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.private.v1.json"
)
PROTOTYPE_RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.source_free.v1.json"
)
PROTOTYPE_VIRTUAL_OUTPUT_ROOT = TMP / "_wave7_read_only_prototype"
PROTOTYPE_EXPECTED_INPUT_SHA256 = {
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
PROTOTYPE_EXPECTED_CANDIDATE_SHA256 = (
    "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F"
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


class Wave7AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave7AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(PREDECESSOR_PATH, "pk_dialogue_wave7_assignment_base")
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
    "MAX_SELECTORS": MAX_SELECTORS,
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
        AGENT_BUNDLE_COUNT <= len(packets) <= MAX_SELECTORS,
        "wide wave packet count is outside the configured bounds",
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
        "post-wave5 assignment predecessor drifted",
    )
    require(
        not (prototype and allow_unfrozen),
        "prototype and final bootstrap modes cannot be combined",
    )
    if not prototype and not allow_unfrozen:
        missing = unresolved_final_pins()
        require(
            not missing,
            "wave7 assignment pins unresolved: " + ", ".join(missing),
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
                f"wave7 output drifted: {path}",
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
        "bundle_manifest_sha256":
            public["guards"]["agent_bundle_manifest_sha256"],
        "prototype_read_only": bool(args.prototype),
        "status": public["status"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
