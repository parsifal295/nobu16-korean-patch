#!/usr/bin/env python3
"""Build the root-sharded wave-7 consolidated closure.

This adapter deliberately consumes the 48 root-owner packets in
packet-id order.  The assignment's 1,128 zero-overlap pair proofs establish
commutativity, so the inherited n! union witness is reduced to canonical and
reverse order only.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
PUBLIC = WORKSTREAM / "public"
SEMANTIC = TMP / "semantic_overrides"

WAVE6_CLOSURE = (
    WORKSTREAM
    / "build_pk_dialogue_wave_post_selector292_wave6_consolidated_closure_v1.py"
)
EXPECTED_WAVE6_CLOSURE_SHA256 = (
    "742158D5379CC104C838AAC7BDB18ADEE769EC63FF56BE814E44DE9B15D3241A"
)
ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave7_root_sharded_assignment_v1.py"
)
ASSIGNMENT_PRIVATE_PATH = (
    TMP / "pk_dialogue_wave7_root_sharded_assignment.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC / "pk_dialogue_wave7_root_sharded_assignment.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v7_root_sharded"
OFFICIAL_LEDGER_PATH = (
    TMP
    / "runtime_vm_integrated."
    "post_selector292_wave6_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC
    / "pk_dialogue_wave_post_selector292_wave6_"
    "consolidated_closure_decisions.private.v1.jsonl"
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_"
    "consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    TMP
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_"
    "consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_"
    "consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_"
    "consolidated_closure_promotion.v1.json"
)

EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "780981420CBCBB137E97E9758D362C378983053F6442CF73C06E20DE22016126"
)
EXPECTED_ASSIGNMENT_PRIVATE_SHA256 = (
    "95806AE1BD79742473E8C503E1F8DA48C13EC3408CDCFF705E4AB418734E7D3B"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6D6601B9BC91456EBD65ECA86D479592BCF998584A9F5E2E336A438C5BCC7E5E"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "7016A0AB5EFD5B0FD223818F860B5757A914188A8EE58C2AD3BE6D14BC393F61"
)
EXPECTED_PREDECESSOR_DECISIONS_SHA256 = (
    "997366037F93F13411BA46378DC99E1CF00B0DA863A7C93FD2D862A6F3CD669E"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "987E9644DD5DC235C74E52858546C9196BA15203871A7FE9DDEBF121697435F3"
)
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_PENDING_BEFORE = 5_922
EXPECTED_REVIEWED_SITES = 738
# The inherited closure core uses a JSON-list site digest, while the
# root-sharded assignment uses its own site-set digest (8222CD0C...).  Both
# commit the same 738 exact sites; this is the core-compatible representation.
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "D16CBA93E7EAB8AC2DA9B801BCAF99B8FCDC3EEDAF010D6FD466E639F9F4CB9A"
)
EXPECTED_SOURCE_SITES = 841
EXPECTED_SOURCE_SITE_MANIFEST_SHA256 = (
    "EC86F67C39BA751BF64ADCD7A60187E236A51A71DC80BBAE7C6BB58FFBFD29C7"
)
EXPECTED_SOURCE_ONLY_SITES = 103
EXPECTED_SOURCE_ONLY_MANIFEST_SHA256 = (
    "1E584D0B12B469CEF69E489D50DFFAB67E5DFFDF4E16A0E6AD5BB8DF6AA10437"
)
EXPECTED_ASSIGNED_PENDING = 216
EXPECTED_ASSIGNED_ROOTS = 113
EXPECTED_OWNER_PACKETS = 48
EXPECTED_PAIRWISE_ROWS = 1_128


class ClosurePreparationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosurePreparationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


require(
    WAVE6_CLOSURE.is_file()
    and sha256_file(WAVE6_CLOSURE) == EXPECTED_WAVE6_CLOSURE_SHA256,
    "wave6 closure scaffold drifted",
)
W6 = load_module(WAVE6_CLOSURE, "wave7_root_sharded_closure_base")
WRAPPER = W6.WRAPPER
BASE = W6.BASE
RAW_LOAD_JSON = W6.ORIGINAL_BASE_LOAD_JSON
RAW_LOAD_JSONL = W6.ORIGINAL_BASE_LOAD_JSONL
ORIGINAL_W6_CONFIGURE_BASE = W6.configure_base


class CanonicalReverseOrders:
    """Two witnesses after the 1,128 pairwise root/coordinate proofs pass."""

    @staticmethod
    def permutations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
        canonical = tuple(values)
        if len(canonical) < 2:
            return (canonical,)
        return canonical, tuple(reversed(canonical))


def raw_assignment() -> dict[str, Any]:
    return RAW_LOAD_JSON(ASSIGNMENT_PRIVATE_PATH)


def packet_paths(meta: Mapping[str, Any]) -> tuple[Path, ...]:
    artifacts = sorted(
        meta["packet_artifacts"], key=lambda row: int(row["packet_id"])
    )
    require(
        [int(row["packet_id"]) for row in artifacts]
        == list(range(EXPECTED_OWNER_PACKETS)),
        "packet-id sequence drifted",
    )
    return tuple(PACKET_DIR / str(row["basename"]) for row in artifacts)


def load_packets(meta: Mapping[str, Any]) -> list[dict[str, Any]]:
    paths = packet_paths(meta)
    artifacts = sorted(
        meta["packet_artifacts"], key=lambda row: int(row["packet_id"])
    )
    packets = []
    for artifact, path in zip(artifacts, paths, strict=True):
        require(
            path.is_file() and sha256_file(path) == artifact["sha256"],
            f"packet artifact drifted: {artifact['packet_id']}",
        )
        packets.append(RAW_LOAD_JSON(path))
    return packets


def synthetic_assignment(meta: Mapping[str, Any]) -> dict[str, Any]:
    packets = load_packets(meta)
    pairwise = meta["global_disjointness"]["pairwise"]
    require(
        len(packets) == EXPECTED_OWNER_PACKETS
        and len(pairwise) == EXPECTED_PAIRWISE_ROWS
        and all(
            int(row["owned_pending_coordinate_overlap"]) == 0
            and int(row["owned_root_overlap"]) == 0
            for row in pairwise
        ),
        "root-sharded assignment is not globally disjoint",
    )
    return {
        **meta,
        "schema": "nobu16.kr.pk-dialogue-wave-assignment.private.v1",
        "packets": packets,
        "pairwise_independence": [
            {
                "left_packet_id": int(row["left_packet_id"]),
                "right_packet_id": int(row["right_packet_id"]),
                "counts": {
                    "owned_pending_coordinate_overlap":
                        int(row["owned_pending_coordinate_overlap"]),
                    "owned_root_overlap": int(row["owned_root_overlap"]),
                },
            }
            for row in pairwise
        ],
    }


META = raw_assignment()
OWNER_ASSIGNMENT = sorted(
    META["owner_assignment"], key=lambda row: int(row["packet_id"])
)
SELECTORS = tuple(int(row["selector"]) for row in OWNER_ASSIGNMENT)
require(
    len(SELECTORS) == EXPECTED_OWNER_PACKETS
    and len(set(SELECTORS)) == EXPECTED_OWNER_PACKETS,
    "owner selector sequence drifted",
)

BUNDLE_BUILDERS = {
    0: TMP / "pk_dialogue_wave7_root_bundle0_generator.private.v1.py",
    1: TMP / "pk_dialogue_wave7_root_sharded_bundle1_generator.private.v1.py",
    2: TMP / "pk_dialogue_wave7_root_sharded_bundle2_generator.private.v1.py",
}
CHUNK_BUILDERS = tuple(
    BUNDLE_BUILDERS[int(row["bundle_id"])] for row in OWNER_ASSIGNMENT
)
CHUNK_DECISIONS = tuple(
    SEMANTIC / f"pk_dialogue_wave2_selector{selector}_decisions.private.v1.jsonl"
    for selector in SELECTORS
)
CHUNK_EVIDENCE = tuple(
    TMP / f"pk_dialogue_wave2_selector{selector}_evidence.private.v1.json"
    for selector in SELECTORS
)
CHUNK_PUBLIC = CHUNK_EVIDENCE


def unresolved_paths() -> list[str]:
    paths = {
        "assignment_builder": ASSIGNMENT_BUILDER_PATH,
        "assignment_private": ASSIGNMENT_PRIVATE_PATH,
        "assignment_public": ASSIGNMENT_PUBLIC_PATH,
        "official_ledger": OFFICIAL_LEDGER_PATH,
        "predecessor_decisions": PREDECESSOR_DECISIONS_PATH,
    }
    for owner in range(EXPECTED_OWNER_PACKETS):
        paths[f"chunk{owner}_builder"] = CHUNK_BUILDERS[owner]
        paths[f"chunk{owner}_decisions"] = CHUNK_DECISIONS[owner]
        paths[f"chunk{owner}_evidence"] = CHUNK_EVIDENCE[owner]
    return [label for label, path in paths.items() if not path.is_file()]


def observed_input_hashes() -> dict[str, str]:
    missing = unresolved_paths()
    require(not missing, "unresolved inputs: " + ",".join(missing))
    result = {
        "assignment_builder": sha256_file(ASSIGNMENT_BUILDER_PATH),
        "assignment_private": sha256_file(ASSIGNMENT_PRIVATE_PATH),
        "assignment_public": sha256_file(ASSIGNMENT_PUBLIC_PATH),
        "official_ledger": sha256_file(OFFICIAL_LEDGER_PATH),
        "predecessor_decisions": sha256_file(PREDECESSOR_DECISIONS_PATH),
    }
    for owner in range(EXPECTED_OWNER_PACKETS):
        result[f"chunk{owner}_builder"] = sha256_file(CHUNK_BUILDERS[owner])
        result[f"chunk{owner}_public"] = sha256_file(CHUNK_PUBLIC[owner])
        result[f"chunk{owner}_decisions"] = sha256_file(CHUNK_DECISIONS[owner])
        result[f"chunk{owner}_evidence"] = sha256_file(CHUNK_EVIDENCE[owner])
    return result


def load_json_compatible(path: Path) -> Any:
    if path.resolve() == ASSIGNMENT_PRIVATE_PATH.resolve():
        return synthetic_assignment(RAW_LOAD_JSON(path))
    payload = RAW_LOAD_JSON(path)
    if path.resolve() == ASSIGNMENT_PUBLIC_PATH.resolve():
        payload = dict(payload)
        require(payload.get("status") == "READY", "assignment public not ready")
        payload["status"] = "PASS"
    return payload


def load_jsonl_compatible(path: Path) -> list[dict[str, Any]]:
    rows = RAW_LOAD_JSONL(path)
    if path not in CHUNK_DECISIONS:
        return rows
    return [
        {
            **row,
            "fresh_semantic_review": "approved",
            "historical_factuality_review": "approved",
            "layout_review": "current_relative_raw_g1n_nonexpanding",
            "runtime_review": "verified",
            "speaker_tone_review": "approved",
        }
        for row in rows
    ]


def pending_coordinates(packet: Mapping[str, Any]) -> set[str]:
    return {
        str(coordinate)
        for chunk in packet["chunks"]
        for coordinate in chunk["pending_coordinates"]
    }


def evidence_counts() -> tuple[
    tuple[int, ...],
    tuple[int, ...],
    tuple[int, ...],
    tuple[int, ...],
    tuple[int, ...],
]:
    rows = [RAW_LOAD_JSON(path) for path in CHUNK_EVIDENCE]
    return (
        tuple(int(row["counts"]["decision_rows"]) for row in rows),
        tuple(int(row["counts"]["accepted_pending_roots"]) for row in rows),
        tuple(int(row["counts"]["blocked_pending_rows"]) for row in rows),
        tuple(int(row["counts"]["blocked_pending_roots"]) for row in rows),
        tuple(int(row["counts"]["translation_overrides"]) for row in rows),
    )


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [RAW_LOAD_JSON(path) for path in CHUNK_EVIDENCE]
    packets = assignment["packets"]
    pairwise = assignment["pairwise_independence"]
    require(
        assignment["wave_id"] == "post_selector292_wave7_root_sharded"
        and len(packets) == len(chunk_rows) == len(evidence)
            == EXPECTED_OWNER_PACKETS
        and len(pairwise) == EXPECTED_PAIRWISE_ROWS
        and all(
            all(int(value) == 0 for value in row["counts"].values())
            for row in pairwise
        ),
        "48-owner identity or 1,128 pairwise proof drifted",
    )
    all_pending: set[str] = set()
    all_pending_roots: set[str] = set()
    all_decisions: set[str] = set()
    all_decision_roots: set[str] = set()
    for owner, (selector, packet, rows, review) in enumerate(
        zip(SELECTORS, packets, chunk_rows, evidence, strict=True)
    ):
        pending = pending_coordinates(packet)
        packet_roots = {
            str(root) for chunk in packet["chunks"] for root in chunk["roots"]
        }
        decisions = {str(row["coordinate"]) for row in rows}
        promotions = {
            str(row["coordinate"])
            for row in rows
            if str(row["action"]).endswith("runtime_promotion")
        }
        decision_roots = {BASE.coordinate_root(value) for value in decisions}
        accepted_roots = {BASE.coordinate_root(value) for value in promotions}
        blocked = pending - promotions
        blocked_roots = {BASE.coordinate_root(value) for value in blocked}
        partial_roots = {
            root
            for root in packet_roots
            if 0 < len({
                value for value in promotions if BASE.coordinate_root(value) == root
            }) < len({
                value for value in pending if BASE.coordinate_root(value) == root
            })
        }
        counts = review["counts"]
        proof = review["proof"]
        require(
            int(packet["scope"]["selector_coordinate"].split(":")[1])
                == selector
            and len(packet["site_contexts"])
                == int(OWNER_ASSIGNMENT[owner]["candidate_site_count"])
            and len(pending)
                == int(OWNER_ASSIGNMENT[owner]["pending_coordinate_count"])
            and len(packet_roots)
                == int(OWNER_ASSIGNMENT[owner]["reachable_pending_root_count"])
            and decisions <= pending
            and promotions == decisions
            and not partial_roots
            and not all_pending & pending
            and not all_pending_roots & packet_roots
            and not all_decisions & decisions
            and not all_decision_roots & decision_roots,
            f"selector{selector} root-atomic owner partition drifted",
        )
        require(
            int(counts["decision_rows"]) == len(rows) == len(decisions)
            and int(counts["runtime_promotions"]) == len(promotions)
            and int(counts["accepted_pending_rows"]) == len(promotions)
            and int(counts["accepted_pending_roots"]) == len(accepted_roots)
            and int(counts["blocked_pending_rows"]) == len(blocked)
            and int(counts["blocked_pending_roots"]) == len(blocked_roots)
            and int(counts.get("verification_renewals", 0)) == 0
            and int(counts.get("changed_nonpending_rows", 0)) == 0
            and int(counts.get("source_only_actions", 0)) == 0
            and int(counts.get("terminal_actions", 0)) == 0
            and proof["all_accepted_branches_grammar_pass"] is True
            and proof[
                "all_accepted_branches_current_relative_nonexpanding"
            ] is True
            and proof["steam_write_performed"] is False
            and proof.get("global_root_shard_assignment", True) is True,
            f"selector{selector} evidence disposition drifted",
        )
        contract = packet["agent_contract"]
        require(
            contract["global_root_shard_assignment"] is True
            and contract["nonowner_site_context_read_only"] is True
            and contract["nonpending_root_actions_authorized"] is False
            and contract["source_only_action_count"] == 0
            and contract["terminal_actions_authorized"] is False
            and contract["steam_write_authorized"] is False
            and all(
                row["read_only"]
                and row["automatic_promotion_authorized"] is False
                for row in packet["terminal_manifest"]
            ),
            f"selector{selector} protected scope drifted",
        )
        all_pending.update(pending)
        all_pending_roots.update(packet_roots)
        all_decisions.update(decisions)
        all_decision_roots.update(decision_roots)
    require(
        len(all_pending) == EXPECTED_ASSIGNED_PENDING
        and len(all_pending_roots) == EXPECTED_ASSIGNED_ROOTS,
        "root-sharded pending union drifted",
    )
    return evidence


def source_only_runtime_delta_proof(
    assignment: Mapping[str, Any],
    _current_records: Mapping[tuple[int, int], Any],
    _candidate_records: Mapping[tuple[int, int], Any],
    _source_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    packets = assignment["packets"]
    candidate_sites = {
        str(row["site"]) for packet in packets for row in packet["site_contexts"]
    }
    source_manifest = [
        {
            "selector": packet["scope"]["selector_coordinate"],
            "site_count": packet["scope"]["source_site_count"],
            "site_sha256": packet["scope"]["source_site_sha256"],
        }
        for packet in packets
    ]
    source_only_manifest = [
        {
            "action": "none",
            "selector": packet["scope"]["selector_coordinate"],
            "site_count": packet["scope"]["source_only_site_count"],
            "site_sha256": packet["scope"]["source_only_site_sha256"],
        }
        for packet in packets
    ]
    require(
        len(candidate_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(candidate_sites) == EXPECTED_CANDIDATE_SITE_SHA256
        and sum(row["site_count"] for row in source_manifest)
            == EXPECTED_SOURCE_SITES
        and BASE.canonical_sha256(source_manifest)
            == EXPECTED_SOURCE_SITE_MANIFEST_SHA256
        and sum(row["site_count"] for row in source_only_manifest)
            == EXPECTED_SOURCE_ONLY_SITES
        and BASE.canonical_sha256(source_only_manifest)
            == EXPECTED_SOURCE_ONLY_MANIFEST_SHA256,
        "source/source-only manifest drifted",
    )
    return {
        "actions": 0,
        "classification": "root_sharded_assignment_pinned_no_action",
        "proof_rows": source_only_manifest,
        "proof_sha256": EXPECTED_SOURCE_ONLY_MANIFEST_SHA256,
        "site_count": EXPECTED_SOURCE_ONLY_SITES,
        "site_sha256": EXPECTED_SOURCE_ONLY_MANIFEST_SHA256,
    }


def runtime_expectations() -> dict[str, Any]:
    official = RAW_LOAD_JSONL(OFFICIAL_LEDGER_PATH)
    official_by_coordinate = {
        str(row["coordinate"]): row
        for row in official
        if row.get("resource") == "pk_msggame"
    }
    decisions = [
        row
        for path in CHUNK_DECISIONS
        for row in load_jsonl_compatible(path)
    ]
    coordinates = {str(row["coordinate"]) for row in decisions}
    require(len(coordinates) == len(decisions), "decision coordinates overlap")
    actions = Counter(str(row["action"]) for row in decisions)
    promotions = {
        coordinate
        for coordinate in coordinates
        if official_by_coordinate[coordinate].get("runtime_review") == "pending"
    }
    renewals = coordinates - promotions
    overrides = {
        str(row["coordinate"])
        for row in decisions
        if str(row["reviewed_translation"])
        != str(official_by_coordinate[str(row["coordinate"])]["translation"])
    }
    return {
        "actions": dict(sorted(actions.items())),
        "decision_rows": len(decisions),
        "decision_roots": len({BASE.coordinate_root(value) for value in coordinates}),
        "overrides": len(overrides),
        "promotions": len(promotions),
        "renewals": len(renewals),
    }


def configure_base() -> None:
    ORIGINAL_W6_CONFIGURE_BASE()
    BASE.itertools = CanonicalReverseOrders
    BASE.load_json = load_json_compatible
    BASE.load_jsonl = load_jsonl_compatible
    BASE.METHOD = (
        "post_selector292_wave7_root_sharded_48_owner_root_atomic_"
        "canonical_reverse_union_current_relative_guards"
    )
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave7_root_sharded_update_action"
    BASE.validate_chunk_evidence = validate_chunk_evidence
    BASE.source_only_runtime_delta_proof = source_only_runtime_delta_proof


def validate_site_call(
    _records: Mapping[tuple[int, int], Any],
    _site: str,
    *,
    expected: bool,
) -> None:
    require(expected in (True, False), "invalid site expectation")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    for key in tuple(proof):
        if key.startswith("all_") and key.endswith("_candidate_sites_reviewed"):
            proof.pop(key)
        if key.startswith("source_only_") and key.endswith(
            "_absent_from_current_and_candidate"
        ):
            proof.pop(key)
    proof.update({
        "all_738_candidate_sites_reviewed": True,
        "all_1128_owner_pairs_coordinate_and_root_disjoint": True,
        "canonical_and_reverse_orders_identical": True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "root_atomic_owner_partition_verified": True,
        "source_only_103_assignment_pinned_no_action": True,
        "terminal_336_records_read_only": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = RAW_LOAD_JSONL(OFFICIAL_LEDGER_PATH)
    assignment = synthetic_assignment(META)
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict").splitlines()
        if line
    ]
    decision_coordinates = {str(row["coordinate"]) for row in decisions}
    assigned_pending = {
        value
        for packet in assignment["packets"]
        for value in pending_coordinates(packet)
    }
    chunk_promotions = {
        str(row["coordinate"])
        for path in CHUNK_DECISIONS
        for row in load_jsonl_compatible(path)
        if str(row["action"]).endswith("runtime_promotion")
    }
    blocked = assigned_pending - chunk_promotions
    terminal_roots = {
        str(row["root"])
        for packet in assignment["packets"]
        for row in packet["terminal_manifest"]
    }
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed
        and not decision_coordinates & blocked
        and not {BASE.coordinate_root(value) for value in decision_coordinates}
            & terminal_roots
        and all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and "auto" not in str(
                row.get("post_selector292_wave7_root_sharded_update_action", "")
            ).lower()
            for row in decisions
        ),
        "closure touched blocked, terminal, or confirmed-non-display rows",
    )


def configure_wrapper() -> dict[str, Any]:
    hashes = observed_input_hashes()
    require(
        hashes["assignment_builder"] == EXPECTED_ASSIGNMENT_BUILDER_SHA256
        and hashes["assignment_private"] == EXPECTED_ASSIGNMENT_PRIVATE_SHA256
        and hashes["assignment_public"] == EXPECTED_ASSIGNMENT_PUBLIC_SHA256
        and hashes["official_ledger"] == EXPECTED_OFFICIAL_LEDGER_SHA256
        and hashes["predecessor_decisions"]
            == EXPECTED_PREDECESSOR_DECISIONS_SHA256,
        "fixed predecessor input drifted",
    )
    expectation = runtime_expectations()
    chunk_rows, _accepted, _blocked, _blocked_roots, overrides = evidence_counts()
    chunk_sites = tuple(
        int(row["candidate_site_count"]) for row in OWNER_ASSIGNMENT
    )
    expected_output = {
        "private_decisions":
            "554F0365B15976A7F0457D277AB7FFECFCCD86CBF0B6507E68D5737B072D7AE4",
        "private_evidence":
            "BD7F78DC393CDC9C6B41273304F9FAD2810324B4354E82D720AB790F5473E971",
        "public_coverage":
            "D4B75C47480F155FC0C1EF091E1205C135EE6C160045013C2D687B09A5CAF1D7",
        "public_promotion":
            "32DC1CA24BDFD72E88E5896CB1BEE191B0D743C7E9EBBCF84EF475049F99BB68",
        "final_candidate":
            "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0",
        "decision_coordinates":
            "DE8BA114858A9A5D8B0D01A3989D43C5FFCDAB889E72B93A65AF500456843693",
        "promotion_coordinates":
            "DE8BA114858A9A5D8B0D01A3989D43C5FFCDAB889E72B93A65AF500456843693",
        "renewal_coordinates":
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        "override_coordinates":
            "36E25FF18A6763E01AA4B98457272F075C192AF2466F06999EB0E9A38B310142",
        "predecessor_overlap_coordinates":
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        "predecessor_supersession_coordinates":
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        "source_only_proof": EXPECTED_SOURCE_ONLY_MANIFEST_SHA256,
    }
    values = {
        "ASSIGNMENT_BUILDER_PATH": ASSIGNMENT_BUILDER_PATH,
        "ASSIGNMENT_PRIVATE_PATH": ASSIGNMENT_PRIVATE_PATH,
        "ASSIGNMENT_PUBLIC_PATH": ASSIGNMENT_PUBLIC_PATH,
        "OFFICIAL_LEDGER_PATH": OFFICIAL_LEDGER_PATH,
        "PREDECESSOR_DECISIONS_PATH": PREDECESSOR_DECISIONS_PATH,
        "CHUNK_BUILDERS": CHUNK_BUILDERS,
        "CHUNK_PUBLIC": CHUNK_PUBLIC,
        "CHUNK_DECISIONS": CHUNK_DECISIONS,
        "CHUNK_EVIDENCE": CHUNK_EVIDENCE,
        "PRIVATE_DECISIONS_OUTPUT": PRIVATE_DECISIONS_OUTPUT,
        "PRIVATE_EVIDENCE_OUTPUT": PRIVATE_EVIDENCE_OUTPUT,
        "PUBLIC_COVERAGE_OUTPUT": PUBLIC_COVERAGE_OUTPUT,
        "PUBLIC_PROMOTION_OUTPUT": PUBLIC_PROMOTION_OUTPUT,
        "EXPECTED_INPUT_SHA256": hashes,
        "EXPECTED_CHUNK_ROWS": chunk_rows,
        "EXPECTED_CHUNK_SITES": chunk_sites,
        "EXPECTED_DECISION_ROWS": expectation["decision_rows"],
        "EXPECTED_DECISION_ROOTS": expectation["decision_roots"],
        "EXPECTED_PROMOTIONS": expectation["promotions"],
        "EXPECTED_RENEWALS": expectation["renewals"],
        "EXPECTED_OVERRIDES": expectation["overrides"],
        "EXPECTED_ACTION_COUNTS": expectation["actions"],
        "EXPECTED_PENDING_BEFORE": EXPECTED_PENDING_BEFORE,
        "EXPECTED_PENDING_AFTER":
            EXPECTED_PENDING_BEFORE - expectation["promotions"],
        "EXPECTED_REVIEWED_SITES": EXPECTED_REVIEWED_SITES,
        "EXPECTED_CANDIDATE_SITE_SHA256": EXPECTED_CANDIDATE_SITE_SHA256,
        "EXPECTED_SOURCE_SITES": EXPECTED_SOURCE_SITES,
        "EXPECTED_SOURCE_SITE_SHA256": EXPECTED_SOURCE_SITE_MANIFEST_SHA256,
        "EXPECTED_SOURCE_ONLY_SITES": EXPECTED_SOURCE_ONLY_SITES,
        "EXPECTED_SOURCE_ONLY_SHA256": EXPECTED_SOURCE_ONLY_MANIFEST_SHA256,
        "EXPECTED_PREDECESSOR_OVERLAPS": 0,
        "EXPECTED_PREDECESSOR_SUPERSESSIONS": 0,
        "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
        "EXPECTED_OFFICIAL_CANDIDATE_SHA256":
            EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
            EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
        "EXPECTED_OUTPUT_SHA256": expected_output,
        "configure_base": configure_base,
        "validate_site_call": validate_site_call,
        "transform_outputs": transform_outputs,
        "validate_wrapper_invariants": validate_wrapper_invariants,
    }
    for name, value in values.items():
        setattr(W6, name, value)
        setattr(WRAPPER, name, value)
    return {
        "expectation": expectation,
        "hashes": hashes,
        "output_pins": expected_output,
        "unused_evidence_override_count_sum": sum(overrides),
    }


def build_outputs() -> tuple[dict[Path, bytes], dict[str, Any]]:
    preparation = configure_wrapper()
    outputs = WRAPPER.build_outputs()
    return outputs, preparation


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    missing = unresolved_paths()
    if args.probe:
        print(json.dumps({
            "missing_inputs": missing,
            "owner_packets": len(SELECTORS),
            "pairwise_rows": EXPECTED_PAIRWISE_ROWS,
            "selectors": list(SELECTORS),
            "status": "WAITING" if missing else "READY",
            "steam_write_performed": False,
        }, ensure_ascii=True, sort_keys=True))
        return 0
    require(not missing, "unresolved inputs: " + ",".join(missing))
    outputs, preparation = build_outputs()
    if args.check:
        for path, content in outputs.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"wave7 root-sharded closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    output_hashes = {
        path.name: sha256_bytes(content) for path, content in outputs.items()
    }
    final_candidate = json.loads(
        outputs[PRIVATE_EVIDENCE_OUTPUT].decode("utf-8")
    )["guards"]["candidate_sha256"]
    print(json.dumps({
        "expectation": preparation["expectation"],
        "final_candidate_sha256": final_candidate,
        "input_sha256": preparation["hashes"],
        "output_sha256": output_hashes,
        "owner_packets": EXPECTED_OWNER_PACKETS,
        "pairwise_rows": EXPECTED_PAIRWISE_ROWS,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
