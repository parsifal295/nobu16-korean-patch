#!/usr/bin/env python3
"""Verify that dialogue remediation changes text, not msggame VM topology.

The runtime-surface remediation is expected to preserve every record, literal
slot, selector, jump, call, operator, and control token.  The reviewed PK
remediation retargets 626 semantic call operations (632 concrete component
mutations) to coherent ending families.  This source-free audit binds every
operation to its exact coordinate, component index, before/after component
hash, and reviewed reason; rejects every other structural mutation; and
rejects newly introduced ``도``/``및`` fallbacks at dynamic boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
sys.path.insert(0, str(WORKSTREAM))

import audit_runtime_surface_v1 as SURFACE  # noqa: E402


SCHEMA = "nobu16.kr.pc-dialogue-candidate-structure-audit.v1"
DEFAULT_PREDECESSOR_ROOT = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
)
DEFAULT_BASE_SOURCE = (
    DEFAULT_PREDECESSOR_ROOT / "MSG" / "JP" / "msggame.bin"
)
DEFAULT_PK_SOURCE = (
    DEFAULT_PREDECESSOR_ROOT / "MSG_PK" / "JP" / "msggame.bin"
)
DEFAULT_REMEDIATION_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_surface_remediation_v1"
)
DEFAULT_BASE_CANDIDATE = (
    DEFAULT_REMEDIATION_ROOT
    / "base"
    / "candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_PK_CANDIDATE = (
    DEFAULT_REMEDIATION_ROOT
    / "pk"
    / "candidate"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
BASE_CALL_ALLOWLIST_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base_call_assembly_structure_allowlist.source_free.v1.json"
)
PK_REMEDIATION_REPORT_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "pk_remediation.source_free.v1.json"
)
EXPECTED_BASE_CALL_ALLOWLIST_COUNT = 1672
EXPECTED_BASE_CALL_ALLOWLIST_SHA256 = (
    "31E851D15751F645187F56C7DD9198D4A8125455968DA0484755C662BA2D73BB"
)
EXPECTED_PK_SOURCE_SHA256 = (
    "0330917524A47974618317A8EC56C4B471672DA5AD07000A8C5D8A7CCFB8A05F"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "1D7F1FB2086419BD1FC928012F3E0E3D0BA2C600809513188A3FFBA455F63EFF"
)
EXPECTED_PK_REVIEWED_OPERATION_COUNT = 626
EXPECTED_PK_REVIEWED_MUTATION_COUNT = 632
EXPECTED_PK_REVIEWED_OPERATION_SHA256 = (
    "3F09DA592C751BD674BBC375DA73F9FA8FA5EC01342AEF7CF37231595086A563"
)
EXPECTED_PK_REVIEWED_COMPONENT_SHA256 = (
    "B01757C09FCC5918FBB17A868CAC72219ECF50472E6FFA5C5B41714410BCD922"
)

def call_component(target: int) -> dict[str, object]:
    return {
        "kind": "call",
        "operand": target,
        "target": [0, target],
        "raw_hex": (b"\x01\x43" + struct.pack("<I", target)).hex().upper(),
    }


CALL_376 = {
    "kind": "call",
    "operand": 376,
    "target": [0, 376],
    "raw_hex": "014378010000",
}
CALL_178 = {
    "kind": "call",
    "operand": 178,
    "target": [0, 178],
    "raw_hex": "0143B2000000",
}
CALL_34 = {
    "kind": "call",
    "operand": 34,
    "target": [0, 34],
    "raw_hex": "014322000000",
}
CALL_8 = {
    "kind": "call",
    "operand": 8,
    "target": [0, 8],
    "raw_hex": "014308000000",
}
CALL_70 = {
    "kind": "call",
    "operand": 70,
    "target": [0, 70],
    "raw_hex": "014346000000",
}
CALL_298 = {
    "kind": "call",
    "operand": 298,
    "target": [0, 298],
    "raw_hex": "01432A010000",
}
CALL_520 = {
    "kind": "call",
    "operand": 520,
    "target": [0, 520],
    "raw_hex": "014308020000",
}
CALL_550 = {
    "kind": "call",
    "operand": 550,
    "target": [0, 550],
    "raw_hex": "014326020000",
}
CALL_556 = {
    "kind": "call",
    "operand": 556,
    "target": [0, 556],
    "raw_hex": "01432C020000",
}
CALL_568 = {
    "kind": "call",
    "operand": 568,
    "target": [0, 568],
    "raw_hex": "014338020000",
}
CALL_718 = {
    "kind": "call",
    "operand": 718,
    "target": [0, 718],
    "raw_hex": "0143CE020000",
}
CALL_1096 = {
    "kind": "call",
    "operand": 1096,
    "target": [0, 1096],
    "raw_hex": "014348040000",
}
CALL_610 = {
    "kind": "call",
    "operand": 610,
    "target": [0, 610],
    "raw_hex": "014362020000",
}
CALL_748 = {
    "kind": "call",
    "operand": 748,
    "target": [0, 748],
    "raw_hex": "0143EC020000",
}
CALL_1247 = {
    "kind": "call",
    "operand": 1247,
    "target": [0, 1247],
    "raw_hex": "0143DF040000",
}
CALL_2633 = {
    "kind": "call",
    "operand": 2633,
    "target": [0, 2633],
    "raw_hex": "0143490A0000",
}
CALL_286 = call_component(286)
CALL_82 = call_component(82)
CALL_88 = call_component(88)
CALL_94 = call_component(94)
CALL_142 = call_component(142)
CALL_160 = call_component(160)
CALL_310 = call_component(310)
CALL_322 = call_component(322)
CALL_394 = call_component(394)
CALL_424 = call_component(424)
CALL_466 = call_component(466)
CALL_508 = call_component(508)
CALL_538 = call_component(538)
CALL_574 = call_component(574)
CALL_616 = call_component(616)
CALL_628 = call_component(628)
CALL_634 = call_component(634)
CALL_700 = call_component(700)
CALL_736 = call_component(736)
CALL_808 = call_component(808)
CALL_880 = call_component(880)
CALL_1048 = call_component(1048)
CALL_1150 = call_component(1150)
CALL_1198 = call_component(1198)
CALL_2634 = call_component(2634)
CALL_136 = call_component(136)
CALL_190 = call_component(190)
CALL_196 = call_component(196)
CALL_256 = call_component(256)
CALL_304 = call_component(304)
CALL_562 = call_component(562)
CALL_772 = call_component(772)
CALL_1108 = call_component(1108)
CALL_598 = call_component(598)
CALL_976 = call_component(976)
CALL_982 = call_component(982)
CALL_988 = call_component(988)
ALLOWED_PK_CALL_RETARGETS = {
    ((1, 11), 6): (CALL_94, CALL_1247),
    ((1, 25), 4): (CALL_880, CALL_1247),
    ((2, 133), 6): (CALL_628, CALL_550),
    ((2, 248), 1): (CALL_376, CALL_178),
    ((6, 3507), 1): (CALL_1096, CALL_142),
    ((6, 3528), 3): (CALL_574, CALL_1247),
    ((6, 3541), 3): (CALL_376, CALL_520),
    ((6, 2074), 6): (CALL_700, CALL_1247),
    ((6, 2074), 7): (CALL_610, CALL_2633),
    ((6, 3763), 2): (CALL_568, CALL_520),
    ((6, 3764), 2): (CALL_568, CALL_520),
    ((6, 3764), 4): (CALL_718, CALL_550),
    ((6, 3765), 4): (CALL_34, CALL_1247),
    ((6, 3766), 2): (CALL_1096, CALL_1247),
    ((6, 3768), 7): (CALL_748, CALL_1247),
    ((6, 3769), 7): (CALL_1096, CALL_2633),
    ((6, 3532), 3): (CALL_298, CALL_748),
    ((6, 3849), 2): (CALL_34, CALL_1247),
    ((6, 3942), 4): (CALL_34, CALL_1247),
    ((6, 4179), 3): (CALL_748, CALL_142),
    ((6, 4561), 8): (CALL_1198, CALL_322),
    ((6, 4561), 9): (CALL_748, CALL_1247),
    ((6, 4564), 7): (CALL_1198, CALL_322),
    ((6, 4564), 8): (CALL_748, CALL_1247),
    ((6, 4565), 11): (CALL_1198, CALL_1247),
    ((6, 4565), 12): (CALL_748, CALL_1247),
    ((6, 4566), 11): (CALL_1198, CALL_1247),
    ((6, 4566), 12): (CALL_748, CALL_1247),
    ((6, 4577), 8): (CALL_1198, CALL_322),
    ((6, 4577), 9): (CALL_748, CALL_1247),
    ((6, 4579), 8): (CALL_1198, CALL_322),
    ((6, 4579), 9): (CALL_748, CALL_1247),
    ((6, 4580), 11): (CALL_1198, CALL_1247),
    ((6, 4580), 12): (CALL_748, CALL_1247),
    ((6, 4588), 9): (CALL_376, CALL_550),
    ((6, 4645), 2): (CALL_1096, CALL_142),
    ((6, 4645), 4): (CALL_736, CALL_1247),
    ((6, 4651), 4): (CALL_1198, CALL_1247),
    ((6, 4651), 5): (CALL_748, CALL_1247),
    ((6, 4652), 5): (CALL_1198, CALL_322),
    ((6, 4652), 6): (CALL_748, CALL_1247),
    ((6, 4690), 1): (CALL_1198, CALL_1247),
    ((6, 4690), 2): (CALL_748, CALL_1247),
    ((6, 4707), 3): (CALL_610, CALL_1247),
    ((6, 4763), 1): (CALL_1048, CALL_1247),
    ((6, 4816), 6): (CALL_1198, CALL_322),
    ((6, 4816), 7): (CALL_748, CALL_1247),
    ((6, 4917), 7): (CALL_748, CALL_1247),
    ((8, 303), 2): (CALL_376, CALL_178),
    ((8, 1239), 6): (CALL_1048, CALL_1247),
    ((8, 1239), 7): (CALL_610, CALL_2634),
    ((7, 272), 1): (CALL_748, CALL_160),
    ((7, 335), 4): (CALL_1096, CALL_142),
    ((7, 2512), 1): (CALL_376, CALL_1247),
    ((7, 2512), 3): (CALL_376, CALL_1247),
    ((7, 884), 2): (CALL_634, CALL_550),
    ((7, 884), 4): (CALL_808, CALL_466),
    ((8, 296), 6): (CALL_508, CALL_1247),
    ((8, 1237), 1): (CALL_1096, CALL_1247),
    ((9, 3953), 5): (CALL_88, CALL_70),
    ((9, 3972), 1): (CALL_376, CALL_520),
    ((9, 3973), 1): (CALL_376, CALL_520),
    ((9, 3975), 1): (CALL_376, CALL_520),
    ((9, 3976), 1): (CALL_376, CALL_520),
    ((9, 3978), 1): (CALL_376, CALL_520),
    ((9, 3979), 1): (CALL_376, CALL_520),
    ((9, 3981), 1): (CALL_376, CALL_520),
    ((9, 3982), 1): (CALL_376, CALL_520),
    ((9, 4127), 1): (CALL_376, CALL_520),
    ((9, 4138), 3): (CALL_556, CALL_610),
    ((15, 1545), 2): (CALL_376, CALL_1247),
    ((15, 364), 4): (CALL_1150, CALL_538),
    ((15, 364), 6): (CALL_394, CALL_1247),
    ((15, 379), 2): (CALL_568, CALL_178),
    ((15, 517), 5): (CALL_1096, CALL_142),
    ((15, 228), 1): (CALL_1096, CALL_550),
    ((15, 284), 1): (CALL_568, CALL_550),
    ((15, 762), 4): (CALL_748, CALL_70),
    ((15, 1383), 1): (CALL_748, CALL_1247),
    ((15, 1384), 3): (CALL_1096, CALL_550),
    ((15, 1512), 5): (CALL_610, CALL_2634),
    ((15, 1522), 3): (CALL_610, CALL_2634),
    ((15, 514), 2): (CALL_298, CALL_2633),
    ((15, 819), 6): (CALL_1048, CALL_2633),
    ((15, 1234), 3): (CALL_1048, CALL_2633),
    ((15, 1234), 4): (CALL_286, CALL_1247),
    ((15, 1537), 5): (CALL_700, CALL_1247),
    ((15, 1537), 6): (CALL_424, CALL_2634),
    ((15, 1614), 1): (CALL_310, CALL_1247),
    ((15, 1614), 3): (CALL_376, CALL_1247),
    ((15, 1614), 5): (CALL_286, CALL_1247),
    ((15, 1701), 2): (CALL_700, CALL_1247),
    ((15, 1701), 3): (CALL_616, CALL_2634),
    ((15, 1863), 3): (CALL_1096, CALL_142),
    ((15, 2211), 2): (CALL_82, CALL_142),
    ((15, 2211), 6): (CALL_700, CALL_1247),
    ((15, 2211), 7): (CALL_610, CALL_1247),
    ((15, 2406), 5): (CALL_1096, CALL_142),
    ((15, 2406), 6): (CALL_508, CALL_1247),
    ((15, 2408), 3): (CALL_1096, CALL_142),
    ((15, 2408), 4): (CALL_508, CALL_1247),
    ((15, 2579), 1): (CALL_700, CALL_1247),
    ((15, 2579), 2): (CALL_466, CALL_2633),
    ((15, 2592), 3): (CALL_574, CALL_1247),
    ((15, 2593), 1): (CALL_538, CALL_550),
    ((15, 2593), 5): (CALL_568, CALL_550),
    ((15, 2593), 7): (CALL_1096, CALL_466),
    ((15, 2449), 4): (CALL_34, CALL_1247),
    ((15, 2449), 6): (CALL_8, CALL_1247),
    ((1, 14), 1): (CALL_196, CALL_1247),
    ((1, 14), 5): (CALL_136, CALL_1247),
    ((2, 560), 3): (CALL_976, CALL_1247),
    ((6, 549), 3): (CALL_256, CALL_1247),
    ((6, 3062), 5): (CALL_628, CALL_70),
    ((6, 3110), 1): (CALL_550, CALL_1247),
    ((6, 3535), 5): (CALL_550, CALL_1247),
    ((6, 3555), 1): (CALL_598, CALL_1247),
    ((6, 3555), 5): (CALL_562, CALL_1247),
    ((6, 3625), 4): (CALL_562, CALL_1247),
    ((6, 3631), 4): (CALL_562, CALL_1247),
    ((6, 4203), 1): (CALL_628, CALL_70),
    ((6, 4210), 5): (CALL_508, CALL_1247),
    ((6, 4444), 4): (CALL_550, CALL_1247),
    ((6, 4444), 6): (CALL_550, CALL_1247),
    ((6, 4808), 6): (CALL_988, CALL_1247),
    ((7, 2436), 1): (CALL_1096, CALL_1247),
    ((7, 2436), 5): (CALL_190, CALL_1247),
    ((7, 2436), 6): (CALL_508, CALL_1247),
    ((7, 334), 3): (CALL_982, CALL_1247),
    ((9, 3990), 1): (CALL_190, CALL_1247),
    ((15, 268), 5): (CALL_304, CALL_1247),
    ((15, 269), 3): (CALL_628, CALL_70),
    ((15, 1502), 3): (CALL_376, CALL_1247),
    ((15, 1502), 5): (CALL_556, CALL_1247),
    ((15, 1541), 1): (CALL_772, CALL_1247),
    ((15, 1541), 3): (CALL_286, CALL_1247),
    ((15, 1615), 3): (CALL_286, CALL_1247),
    ((15, 1674), 1): (CALL_628, CALL_70),
}

QUESTION_SECOND_CALL_INDEXES = {
    (6, 4245): 5,
    (6, 4246): 3,
    (6, 4421): 4,
    (7, 2885): 5,
    (8, 1198): 4,
    (8, 1202): 2,
    (15, 379): 5,
    (15, 1229): 3,
    (15, 1235): 3,
    (15, 1568): 6,
    (15, 1666): 4,
    (15, 1669): 4,
    (15, 1677): 4,
    (15, 1682): 3,
    (15, 1683): 3,
    (15, 1687): 3,
    (15, 1689): 3,
    (15, 1691): 3,
    (15, 1694): 4,
    (15, 1822): 3,
    (15, 1823): 3,
    (15, 1824): 3,
    (15, 1825): 3,
    (15, 1826): 3,
    (15, 1827): 3,
    (15, 1900): 4,
    (15, 1901): 4,
    (15, 1903): 6,
    (15, 1915): 6,
    (15, 1916): 6,
    (15, 1918): 6,
    (15, 2207): 2,
    (15, 2263): 4,
    (15, 2297): 4,
    (15, 2451): 6,
    (15, 2467): 2,
    **{(15, record_id): 6 for record_id in range(2308, 2314)},
    **{(15, record_id): 2 for record_id in range(2339, 2359)},
    (15, 2442): 2,
}
ALLOWED_PK_CALL_RETARGETS.update(
    {
        (coordinate, component_index): (
            CALL_616 if coordinate in {(15, 379), (15, 1235)} else CALL_610,
            CALL_1247,
        )
        for coordinate, component_index
        in QUESTION_SECOND_CALL_INDEXES.items()
    }
)

PAST_BOUNDARY_CALL_INDEXES = {
    **{
        (6, record_id): 2
        for record_id in (
            *range(3696, 3709),
            *range(3721, 3733),
        )
    },
    (8, 1198): 1,
    (15, 1359): 7,
}
ALLOWED_PK_CALL_RETARGETS.update(
    {
        (coordinate, component_index): (CALL_628, CALL_70)
        for coordinate, component_index
        in PAST_BOUNDARY_CALL_INDEXES.items()
    }
)
ALLOWED_PK_CALL_RETARGETS.update(
    {
        ((8, 1031), 1): (CALL_568, CALL_1247),
        ((8, 1031), 3): (call_component(442), CALL_1247),
        ((8, 1031), 5): (call_component(1168), CALL_1247),
        ((6, 4468), 1): (CALL_178, CALL_1247),
        ((6, 4468), 5): (call_component(1), CALL_1247),
    }
)


def load_base_call_retargets(
) -> tuple[
    dict[
        tuple[tuple[int, int], int],
        tuple[dict[str, object], dict[str, object]],
    ],
    dict[tuple[tuple[int, int], int], str],
]:
    if not BASE_CALL_ALLOWLIST_PATH.is_file():
        raise ValueError(
            f"Base call allowlist is absent: {BASE_CALL_ALLOWLIST_PATH}"
        )
    document = json.loads(
        BASE_CALL_ALLOWLIST_PATH.read_text(encoding="utf-8")
    )
    if (
        document.get("schema")
        != "nobu16.kr.base-call-assembly-structure-allowlist.v1"
    ):
        raise ValueError("Base call allowlist schema drifted")
    entries = document.get("entries", [])
    if (
        int(document.get("allowed_mutation_count", -1))
        != EXPECTED_BASE_CALL_ALLOWLIST_COUNT
        or len(entries) != EXPECTED_BASE_CALL_ALLOWLIST_COUNT
        or document.get("allowed_mutation_sha256")
        != EXPECTED_BASE_CALL_ALLOWLIST_SHA256
    ):
        raise ValueError("Base call allowlist count/digest drifted")
    allowed = {}
    reasons = {}
    for entry in entries:
        block_id, record_id = (
            int(value) for value in str(entry["coordinate"]).split(":")
        )
        old_block, old_target = (
            int(value) for value in str(entry["old_target"]).split(":")
        )
        new_block, new_target = (
            int(value) for value in str(entry["new_target"]).split(":")
        )
        if old_block != 0 or new_block != 0:
            raise ValueError("Base allowlist contains a nonzero call block")
        key = ((block_id, record_id), int(entry["component_index"]))
        if key in allowed:
            raise ValueError(f"duplicate Base call allowlist key: {key}")
        allowed[key] = (
            call_component(old_target),
            call_component(new_target),
        )
        reasons[key] = str(entry["rule"])
    return allowed, reasons


if os.environ.get("NOBU16_PK_ONLY_STRUCTURE_AUDIT") == "1":
    # The PK builder audits only the PK pair.  This scoped mode prevents an
    # independently evolving Base allowlist from blocking PK verification;
    # standalone and Base audits still require the pinned Base allowlist.
    ALLOWED_BASE_CALL_RETARGETS = {}
    ALLOWED_BASE_CALL_RETARGET_REASONS = {}
else:
    ALLOWED_BASE_CALL_RETARGETS, ALLOWED_BASE_CALL_RETARGET_REASONS = (
        load_base_call_retargets()
    )


def register_pk_call_retargets(
    source_path: Path,
    retargets: Mapping[
        tuple[int, int],
        Sequence[tuple[int, int]],
    ],
    occurrence_counts: Mapping[
        tuple[tuple[int, int], int, int],
        int,
    ],
) -> None:
    """Bind an explicit PK old/new target list to exact component indexes."""
    source_records, source_sha256 = SURFACE.records_from_path(source_path)
    if source_sha256 != EXPECTED_PK_SOURCE_SHA256:
        raise ValueError("PK structure registration source hash drifted")
    for coordinate, operations in sorted(retargets.items()):
        components = SURFACE.tolerant_decode_record(source_records[coordinate])
        for old_target, new_target in operations:
            indexes = [
                component_index
                for component_index, component in enumerate(components)
                if component.get("kind") == "call"
                and tuple(component.get("target", ())) == (0, old_target)
            ]
            expected_count = occurrence_counts.get(
                (coordinate, old_target, new_target),
                1,
            )
            if len(indexes) != expected_count:
                raise ValueError(
                    "PK registered retarget occurrence drifted: "
                    f"{coordinate} {old_target}->{new_target}"
                )
            for component_index in indexes:
                key = (coordinate, component_index)
                expected = (
                    call_component(old_target),
                    call_component(new_target),
                )
                previous = ALLOWED_PK_CALL_RETARGETS.get(key)
                if previous is not None and previous != expected:
                    raise ValueError(
                        f"conflicting PK retarget registration: {key}"
                    )
                ALLOWED_PK_CALL_RETARGETS[key] = expected


def _component_sha256(component: Mapping[str, Any]) -> str:
    payload = json.dumps(
        dict(component),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def load_pk_reviewed_retarget_contract(
    source_path: Path = DEFAULT_PK_SOURCE,
    report_path: Path = PK_REMEDIATION_REPORT_PATH,
) -> tuple[
    dict[
        tuple[tuple[int, int], int],
        tuple[dict[str, object], dict[str, object]],
    ],
    dict[tuple[tuple[int, int], int], str],
    dict[str, Any],
]:
    """Load the final PK retarget evidence as an exact source-free contract."""

    if not report_path.is_file():
        raise ValueError(
            f"PK remediation evidence is absent: {report_path}"
        )
    document = json.loads(report_path.read_text(encoding="utf-8"))
    if (
        document.get("schema")
        != "nobu16.kr.pk-runtime-surface-remediation.v1"
        or document.get("status") != "PASS"
        or document.get("resource") != "MSG_PK/JP/msggame.bin"
        or document.get("input", {}).get("sha256")
        != EXPECTED_PK_SOURCE_SHA256
        or document.get("candidate", {}).get("sha256")
        != EXPECTED_PK_CANDIDATE_SHA256
    ):
        raise ValueError("PK remediation evidence identity drifted")

    control = document.get("control_retargets", {})
    entries = control.get("entries", [])
    if (
        int(control.get("count", -1))
        != EXPECTED_PK_REVIEWED_OPERATION_COUNT
        or len(entries) != EXPECTED_PK_REVIEWED_OPERATION_COUNT
    ):
        raise ValueError("PK reviewed retarget operation count drifted")

    source_records, source_sha256 = SURFACE.records_from_path(source_path)
    if source_sha256 != EXPECTED_PK_SOURCE_SHA256:
        raise ValueError("PK reviewed retarget source hash drifted")
    source_components = {
        coordinate: tuple(
            {
                key: component[key]
                for key in sorted(component)
            }
            for component in SURFACE.tolerant_decode_record(record)
        )
        for coordinate, record in source_records.items()
    }

    operation_rows: list[str] = []
    component_rows: list[str] = []
    allowed: dict[
        tuple[tuple[int, int], int],
        tuple[dict[str, object], dict[str, object]],
    ] = {}
    reasons: dict[tuple[tuple[int, int], int], str] = {}
    for entry in entries:
        coordinate_text = str(entry.get("coordinate", ""))
        old_target_text = str(entry.get("old_target", ""))
        new_target_text = str(entry.get("new_target", ""))
        try:
            block_id, record_id = (
                int(value) for value in coordinate_text.split(":")
            )
            old_block, old_target = (
                int(value) for value in old_target_text.split(":")
            )
            new_block, new_target = (
                int(value) for value in new_target_text.split(":")
            )
            mutation_count = int(entry["mutated_call_count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "PK reviewed retarget entry is malformed"
            ) from exc
        coordinate = (block_id, record_id)
        reason = str(entry.get("semantic_reason", ""))
        before_record_sha256 = str(
            entry.get("before_record_sha256", "")
        )
        after_record_sha256 = str(
            entry.get("after_record_sha256", "")
        )
        expected_old_hex = (
            b"\x01\x43" + struct.pack("<I", old_target)
        ).hex().upper()
        expected_new_hex = (
            b"\x01\x43" + struct.pack("<I", new_target)
        ).hex().upper()
        if (
            old_block != 0
            or new_block != 0
            or old_target == new_target
            or mutation_count < 1
            or not reason
            or len(before_record_sha256) != 64
            or len(after_record_sha256) != 64
            or entry.get("old_call_hex") != expected_old_hex
            or entry.get("new_call_hex") != expected_new_hex
            or entry.get("only_call_operand_changed") is not True
            or entry.get("record_size_preserved") is not True
        ):
            raise ValueError(
                "PK reviewed retarget invariant drifted: "
                f"{coordinate_text} {old_target_text}->{new_target_text}"
            )

        operation_rows.append(
            "|".join(
                (
                    coordinate_text,
                    old_target_text,
                    new_target_text,
                    str(mutation_count),
                    before_record_sha256,
                    after_record_sha256,
                    reason,
                )
            )
        )
        indexes = [
            component_index
            for component_index, component in enumerate(
                source_components[coordinate]
            )
            if component.get("kind") == "call"
            and tuple(component.get("target", ())) == (0, old_target)
        ]
        if len(indexes) != mutation_count:
            raise ValueError(
                "PK reviewed retarget occurrence drifted: "
                f"{coordinate_text} {old_target_text}->{new_target_text}"
            )
        before = call_component(old_target)
        after = call_component(new_target)
        before_sha256 = _component_sha256(before)
        after_sha256 = _component_sha256(after)
        for component_index in indexes:
            key = (coordinate, component_index)
            if key in allowed:
                raise ValueError(
                    f"duplicate PK reviewed component contract: {key}"
                )
            allowed[key] = (before, after)
            reasons[key] = reason
            component_rows.append(
                "|".join(
                    (
                        coordinate_text,
                        str(component_index),
                        before_sha256,
                        after_sha256,
                        reason,
                    )
                )
            )

    operation_sha256 = hashlib.sha256(
        "\n".join(operation_rows).encode("utf-8")
    ).hexdigest().upper()
    component_sha256 = hashlib.sha256(
        "\n".join(sorted(component_rows)).encode("utf-8")
    ).hexdigest().upper()
    if (
        operation_sha256 != EXPECTED_PK_REVIEWED_OPERATION_SHA256
        or len(allowed) != EXPECTED_PK_REVIEWED_MUTATION_COUNT
        or component_sha256 != EXPECTED_PK_REVIEWED_COMPONENT_SHA256
    ):
        raise ValueError("PK reviewed retarget count/digest drifted")

    return (
        allowed,
        reasons,
        {
            "report_path": str(report_path.resolve()),
            "source_sha256": source_sha256,
            "candidate_sha256": EXPECTED_PK_CANDIDATE_SHA256,
            "operation_count": len(entries),
            "operation_sha256": operation_sha256,
            "component_mutation_count": len(allowed),
            "component_contract_sha256": component_sha256,
            "exact_coordinate_component_before_after_hash_bound": True,
            "literal_bodies_omitted": True,
        },
    )


ALLOWED_PK_CALL_RETARGET_REASONS = {
    key: "legacy_exact_reviewed_pk_terminal_retarget"
    for key in ALLOWED_PK_CALL_RETARGETS
}
PK_REVIEWED_RETARGET_CONTRACT: dict[str, Any] = {
    "builder_scoped_registration": True,
    "operation_count": None,
    "component_mutation_count": None,
}
if os.environ.get("NOBU16_PK_ONLY_STRUCTURE_AUDIT") != "1":
    (
        reviewed_pk_call_retargets,
        reviewed_pk_call_retarget_reasons,
        PK_REVIEWED_RETARGET_CONTRACT,
    ) = load_pk_reviewed_retarget_contract()
    for key, expected in ALLOWED_PK_CALL_RETARGETS.items():
        if reviewed_pk_call_retargets.get(key) != expected:
            raise ValueError(
                f"legacy PK reviewed retarget contract drifted: {key}"
            )
    ALLOWED_PK_CALL_RETARGETS = reviewed_pk_call_retargets
    ALLOWED_PK_CALL_RETARGET_REASONS = (
        reviewed_pk_call_retarget_reasons
    )


SEMANTIC_BOUNDARY_PREFIXES = (
    ("\ub3c4", "additive_do"),
    ("\ubc0f", "conjunction_mit"),
)
ALLOWED_PK_SEMANTIC_BOUNDARY_MARKERS = {
    (
        6,
        1635,
        0,
        "call",
        "conjunction_mit",
    ): {
        "producer_kind": "call",
        "marker": "conjunction_mit",
        "text_sha256":
            "DFCDD6A59C71F47374099B6EAF6FA2CE0C078F09DD23717C8ACAB534DB59D8D0",
        "call_target": "0:34",
    },
    (
        6,
        1639,
        0,
        "call",
        "conjunction_mit",
    ): {
        "producer_kind": "call",
        "marker": "conjunction_mit",
        "text_sha256":
            "DFCDD6A59C71F47374099B6EAF6FA2CE0C078F09DD23717C8ACAB534DB59D8D0",
        "call_target": "0:34",
    },
}
SEMANTIC_BOUNDARY_LEXEME_PREFIXES = (
    "\ub3c4\uc6c0",
)
SEMANTIC_BOUNDARY_WRAPPERS = (
    " \t\r\n"
    "\u0029\u005d"
    "\u300d\u300f\u3011\u3009\u300b\u3015"
)


class CandidateStructureError(ValueError):
    """Raised when a structure audit input cannot be evaluated."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_component(component: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: component[key]
        for key in sorted(component)
    }


def components_for(
    records: Mapping[tuple[int, int], Any],
) -> dict[tuple[int, int], tuple[dict[str, Any], ...]]:
    return {
        coordinate: tuple(
            canonical_component(component)
            for component in SURFACE.tolerant_decode_record(record)
        )
        for coordinate, record in records.items()
    }


def semantic_boundary_marker(text: str) -> str | None:
    """Classify risky invariant particles introduced after a runtime value."""

    stripped = text.lstrip(SEMANTIC_BOUNDARY_WRAPPERS)
    if stripped.startswith(SEMANTIC_BOUNDARY_LEXEME_PREFIXES):
        return None
    for prefix, marker in SEMANTIC_BOUNDARY_PREFIXES:
        if stripped.startswith(prefix):
            return marker
    return None


def semantic_boundary_markers(
    records: Mapping[tuple[int, int], Any],
) -> dict[tuple[int, int, int, str, str], dict[str, Any]]:
    """Return dynamic-value boundaries that use ``도`` or conjunction ``및``.

    These forms are not globally forbidden: the predecessor contains reviewed
    additive constructions.  The candidate gate rejects only newly introduced
    coordinates, because the remediation translators used both strings as
    batchim-neutral substitutes for subject/comitative particles.
    """

    markers: dict[
        tuple[int, int, int, str, str],
        dict[str, Any],
    ] = {}
    for coordinate, record in records.items():
        literals = tuple(
            literal.text for literal in SURFACE.parse_record_literals(record)
        )
        producer: Mapping[str, Any] | None = None
        for component in SURFACE.tolerant_decode_record(record):
            kind = str(component["kind"])
            if kind in {"call", "selector"}:
                producer = component
                continue
            if kind == "literal_boundary":
                literal_id = int(component["slot"])
                text = literals[literal_id]
                marker = semantic_boundary_marker(text)
                if producer is not None and marker is not None:
                    producer_kind = str(producer["kind"])
                    key = (
                        coordinate[0],
                        coordinate[1],
                        literal_id,
                        producer_kind,
                        marker,
                    )
                    details: dict[str, Any] = {
                        "producer_kind": producer_kind,
                        "marker": marker,
                        "text_sha256": sha256_bytes(
                            text.encode("utf-16le")
                        ),
                    }
                    if producer_kind == "call":
                        target = tuple(producer["target"])
                        details["call_target"] = (
                            f"{int(target[0])}:{int(target[1])}"
                        )
                    else:
                        details.update(
                            {
                                "selector_group":
                                    int(producer["group"]),
                                "selector_slot":
                                    int(producer["slot"]),
                                "selector_property":
                                    producer.get("property"),
                            }
                        )
                    markers[key] = details
                producer = None
                continue
            if kind in SURFACE.IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL:
                continue
            producer = None
    return markers


def allowed_component_change(
    resource: str,
    coordinate: tuple[int, int],
    component_index: int,
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> bool:
    allowlist = (
        ALLOWED_BASE_CALL_RETARGETS
        if resource == "base_msggame"
        else ALLOWED_PK_CALL_RETARGETS
        if resource == "pk_msggame"
        else {}
    )
    expected = allowlist.get((coordinate, component_index))
    return (
        expected is not None
        and dict(before) == expected[0]
        and dict(after) == expected[1]
    )


def audit_pair(
    resource: str,
    source_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    source_records, source_sha256 = SURFACE.records_from_path(source_path)
    candidate_records, candidate_sha256 = SURFACE.records_from_path(
        candidate_path
    )
    issues: list[dict[str, Any]] = []
    source_keys = set(source_records)
    candidate_keys = set(candidate_records)
    for coordinate in sorted(source_keys - candidate_keys):
        issues.append(
            {
                "category": "record_removed",
                "block_id": coordinate[0],
                "record_id": coordinate[1],
            }
        )
    for coordinate in sorted(candidate_keys - source_keys):
        issues.append(
            {
                "category": "record_added",
                "block_id": coordinate[0],
                "record_id": coordinate[1],
            }
        )

    source_components = components_for(source_records)
    candidate_components = components_for(candidate_records)
    source_semantic_markers = semantic_boundary_markers(source_records)
    candidate_semantic_markers = semantic_boundary_markers(candidate_records)
    introduced_semantic_keys = (
        set(candidate_semantic_markers) - set(source_semantic_markers)
    )
    approved_semantic_markers = (
        ALLOWED_PK_SEMANTIC_BOUNDARY_MARKERS
        if resource == "pk_msggame"
        else {}
    )
    observed_approved_semantic_keys: set[
        tuple[int, int, int, str, str]
    ] = set()
    for key in sorted(introduced_semantic_keys):
        block_id, record_id, literal_id, _producer_kind, _marker = key
        if candidate_semantic_markers[key] == approved_semantic_markers.get(
            key
        ):
            observed_approved_semantic_keys.add(key)
            continue
        issues.append(
            {
                "category": "introduced_semantic_invariant_artifact",
                "block_id": block_id,
                "record_id": record_id,
                "literal_id": literal_id,
                **candidate_semantic_markers[key],
            }
        )
    if observed_approved_semantic_keys != set(approved_semantic_markers):
        issues.append(
            {
                "category":
                    "approved_semantic_boundary_marker_universe_mismatch",
                "expected_count": len(approved_semantic_markers),
                "actual_count": len(observed_approved_semantic_keys),
            }
        )
    literal_changed_count = 0
    allowed_mutation_count = 0
    component_changed_record_count = 0

    for coordinate in sorted(source_keys & candidate_keys):
        source_record = source_records[coordinate]
        candidate_record = candidate_records[coordinate]
        source_literals = tuple(
            literal.text
            for literal in SURFACE.parse_record_literals(source_record)
        )
        candidate_literals = tuple(
            literal.text
            for literal in SURFACE.parse_record_literals(candidate_record)
        )
        if len(source_literals) != len(candidate_literals):
            issues.append(
                {
                    "category": "literal_slot_count_changed",
                    "block_id": coordinate[0],
                    "record_id": coordinate[1],
                    "before": len(source_literals),
                    "after": len(candidate_literals),
                }
            )
        literal_changed_count += sum(
            before != after
            for before, after in zip(source_literals, candidate_literals)
        )

        before_components = source_components[coordinate]
        after_components = candidate_components[coordinate]
        if len(before_components) != len(after_components):
            issues.append(
                {
                    "category": "component_count_changed",
                    "block_id": coordinate[0],
                    "record_id": coordinate[1],
                    "before": len(before_components),
                    "after": len(after_components),
                }
            )
            continue
        record_changed = False
        for component_index, (before, after) in enumerate(
            zip(before_components, after_components)
        ):
            if before == after:
                continue
            record_changed = True
            if allowed_component_change(
                resource,
                coordinate,
                component_index,
                before,
                after,
            ):
                allowed_mutation_count += 1
                continue
            issues.append(
                {
                    "category": "unapproved_component_changed",
                    "block_id": coordinate[0],
                    "record_id": coordinate[1],
                    "component_index": component_index,
                    "before_sha256": sha256_bytes(
                        json.dumps(
                            before,
                            ensure_ascii=True,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("ascii")
                    ),
                    "after_sha256": sha256_bytes(
                        json.dumps(
                            after,
                            ensure_ascii=True,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("ascii")
                    ),
                }
            )
        if record_changed:
            component_changed_record_count += 1

    expected_allowed = (
        len(ALLOWED_BASE_CALL_RETARGETS)
        if resource == "base_msggame"
        else len(ALLOWED_PK_CALL_RETARGETS)
        if resource == "pk_msggame"
        else 0
    )
    if allowed_mutation_count != expected_allowed:
        issues.append(
            {
                "category": "allowed_mutation_count_mismatch",
                "expected": expected_allowed,
                "actual": allowed_mutation_count,
            }
        )

    category_counts = Counter(issue["category"] for issue in issues)
    return {
        "resource": resource,
        "status": "PASS" if not issues else "FAIL",
        "source": {
            "path": str(source_path.resolve()),
            "size": source_path.stat().st_size,
            "sha256": source_sha256,
            "record_count": len(source_records),
        },
        "candidate": {
            "path": str(candidate_path.resolve()),
            "size": candidate_path.stat().st_size,
            "sha256": candidate_sha256,
            "record_count": len(candidate_records),
        },
        "literal_changed_count": literal_changed_count,
        "component_changed_record_count": component_changed_record_count,
        "allowed_mutation_count": allowed_mutation_count,
        "source_semantic_marker_count": len(source_semantic_markers),
        "candidate_semantic_marker_count": len(
            candidate_semantic_markers
        ),
        "introduced_semantic_marker_count": len(introduced_semantic_keys),
        "approved_semantic_marker_count":
            len(observed_approved_semantic_keys),
        "issue_count": len(issues),
        "category_counts": dict(sorted(category_counts.items())),
        "issues": issues,
    }


def build_report(
    base_source: Path,
    base_candidate: Path,
    pk_source: Path,
    pk_candidate: Path,
) -> dict[str, Any]:
    resources = {
        "MSG/JP/msggame.bin": audit_pair(
            "base_msggame",
            base_source,
            base_candidate,
        ),
        "MSG_PK/JP/msggame.bin": audit_pair(
            "pk_msggame",
            pk_source,
            pk_candidate,
        ),
    }
    issue_count = sum(
        resource["issue_count"] for resource in resources.values()
    )
    return {
        "schema": SCHEMA,
        "status": "PASS" if issue_count == 0 else "FAIL",
        "release_target": "0.15.0",
        "issue_count": issue_count,
        "resources": resources,
        "pk_reviewed_retarget_contract": (
            PK_REVIEWED_RETARGET_CONTRACT
        ),
        "allowed_mutations": [
            {
                "resource": "base_msggame",
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "component_index": component_index,
                "before_call_target":
                    f"{before['target'][0]}:{before['target'][1]}",
                "after_call_target":
                    f"{after['target'][0]}:{after['target'][1]}",
                "before_component_sha256": _component_sha256(before),
                "after_component_sha256": _component_sha256(after),
                "reason": ALLOWED_BASE_CALL_RETARGET_REASONS[
                    (coordinate, component_index)
                ],
            }
            for (
                coordinate,
                component_index,
            ), (
                before,
                after,
            ) in sorted(ALLOWED_BASE_CALL_RETARGETS.items())
        ] + [
            {
                "resource": "pk_msggame",
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "component_index": component_index,
                "before_call_target":
                    f"{before['target'][0]}:{before['target'][1]}",
                "after_call_target":
                    f"{after['target'][0]}:{after['target'][1]}",
                "before_component_sha256": _component_sha256(before),
                "after_component_sha256": _component_sha256(after),
                "reason": ALLOWED_PK_CALL_RETARGET_REASONS[
                    (coordinate, component_index)
                ],
            }
            for (
                coordinate,
                component_index,
            ), (
                before,
                after,
            ) in sorted(ALLOWED_PK_CALL_RETARGETS.items())
        ],
        "literal_bodies_omitted": True,
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-source",
        type=Path,
        default=DEFAULT_BASE_SOURCE,
    )
    parser.add_argument(
        "--base-candidate",
        type=Path,
        default=DEFAULT_BASE_CANDIDATE,
    )
    parser.add_argument(
        "--pk-source",
        type=Path,
        default=DEFAULT_PK_SOURCE,
    )
    parser.add_argument(
        "--pk-candidate",
        type=Path,
        default=DEFAULT_PK_CANDIDATE,
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_report(
        args.base_source,
        args.base_candidate,
        args.pk_source,
        args.pk_candidate,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "status": payload["status"],
                "issue_count": payload["issue_count"],
                "resources": {
                    path: {
                        "candidate_sha256": resource["candidate"]["sha256"],
                        "literal_changed_count":
                            resource["literal_changed_count"],
                        "allowed_mutation_count":
                            resource["allowed_mutation_count"],
                        "issue_count": resource["issue_count"],
                    }
                    for path, resource in payload["resources"].items()
                },
                "output": (
                    str(args.output.resolve())
                    if args.output is not None
                    else None
                ),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 1 if args.strict and payload["issue_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        SURFACE.SurfaceAuditError,
        CandidateStructureError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
