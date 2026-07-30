#!/usr/bin/env python3
"""Build the source-free PK 2546 category-B reflow proposal.

The exact Korean reflow map and semantic review stay in one hash-bound private
handoff below ``tmp``.  This builder independently reconstructs the BF7B
checkpoint candidate, the immediate-only proposal, the unsafe pending-only
deferred probe, and the dependency-inclusive proposal.  It writes only a
source-free tracked report and has no shared-integration or Steam write path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
FAMILY_BUILDER_PATH = (
    WORKSTREAM / "build_pk_bound_terminal_2546_full_caller_closure_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
CHECKPOINT_SOURCE_FREE_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
LEDGER_PATH = DIALOGUE_TMP / "family2546_full_ledger.private.v1.json"
HANDOFF_000_151_PATH = (
    DIALOGUE_TMP / "family2546_ord000_151_analysis.private.v1.json"
)
HANDOFF_152_303_PATH = (
    DIALOGUE_TMP / "family2546_ord152_303_analysis.private.v1.json"
)
REVIEW_QUEUE_PATH = DIALOGUE_TMP / "review_queue.private.v1.jsonl"
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP
    / "family2546_category_b_relative_width_reflow.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_relative_width_reflow_proposal.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "relative-width-reflow-private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "relative-width-reflow-proposal.v1"
)
RELEASE_TARGET = "0.15.0"
RESOURCE = "pk_msggame"
SELECTOR = 1066
TERMINAL_RECORD_IDS = tuple(range(2546, 2553))
B_REASONS = frozenset(
    {
        "relative_line_topology_not_comparable",
        "noncaller_right_line_width_expansion",
    }
)

EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHECKPOINT_SOURCE_FREE_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_CHECKPOINT_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "90987EC88A5AA06DA1BAB681E84D59ECD1E8090EE1AFCD472A0A5D646C3399EE"
)
EXPECTED_HANDOFF_000_151_SHA256 = (
    "CD6A535AFA08678924EA6296FAFAFE192BF70D78F96F616BAC09B741A7CCBEA9"
)
EXPECTED_HANDOFF_152_303_SHA256 = (
    "0E83FCEC00A894B444899B251CABE8F6E0506FE987C29025DB26EEA804A9350B"
)
EXPECTED_REVIEW_QUEUE_SHA256 = (
    "B3F393B578EB46B50C1714A4007AEAA87F8BEF74704E84F7837F3FC482E1D1CC"
)
EXPECTED_PRIVATE_HANDOFF_SHA256 = (
    "686E1D80457C3CF62AEAEDA7BAD619A998B66982980DBAE29AC88C94C0CB3102"
)
EXPECTED_CHECKPOINT_ROWS = 52_803
EXPECTED_CHECKPOINT_PENDING = 8_213

EXPECTED_ROOTS = 6
EXPECTED_ROOT_SHA256 = (
    "830C0834E258B750AC8F15458A55E1DDE432CB948A692F08BEF53F54A4CEF0AB"
)
EXPECTED_PENDING_ROWS = 17
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "0CA9C630F0CAAC5658BA7F6C812B2F64EECA77134415C146D503EC731797E0F5"
)
EXPECTED_PREVERIFIED_ROWS = 3
EXPECTED_PREVERIFIED_COORDINATE_SHA256 = (
    "502E62578238308669A8BA0A873DED20487DB59B54C6EF1B6214EE212773B878"
)

EXPECTED_IMMEDIATE_ROOTS = 4
EXPECTED_IMMEDIATE_ROOT_SHA256 = (
    "4B31FB1F28AD390A8C953EC762B51FEF6FFAF2F914DD0AE40EF9264B727041CC"
)
EXPECTED_IMMEDIATE_PENDING_ROWS = 12
EXPECTED_IMMEDIATE_PENDING_COORDINATE_SHA256 = (
    "D3AF7F5D0111F7FD630BD4DD3782828F6B7140C5B036567BDD3E542605CCB00F"
)
EXPECTED_IMMEDIATE_OVERRIDE_ROWS = 7
EXPECTED_IMMEDIATE_OVERRIDE_COORDINATE_SHA256 = (
    "F88B5E9A65BAF53723BB7CD4CEFF830D6E47F33D8DCED4324F568FB869BBF271"
)
EXPECTED_IMMEDIATE_OVERRIDE_MAP_SHA256 = (
    "8B709CE05A5A0EA674990F54BE4F095DF9BE8D7BE8F8426500808D06F285E883"
)
EXPECTED_IMMEDIATE_KEEP_ROWS = 5
EXPECTED_IMMEDIATE_CANDIDATE_SHA256 = (
    "2AE326439AC0A503104A245774FA4D2CA3B833E05AAE7E8E40F5CFCF7F5B31E2"
)
EXPECTED_IMMEDIATE_ASSEMBLY_SHA256 = (
    "C4AFCB6065A5057AF7DBCE649C28BA14ADFC167FAC23CEAB3137DD6D9A757214"
)

EXPECTED_DEFERRED_ROOTS = 2
EXPECTED_DEFERRED_ROOT_SHA256 = (
    "0C6D9BC26056B32ED99DBADEA8CB5637FE67C8BD3C0A94C2B90846F1F744D5C4"
)
EXPECTED_DEFERRED_PENDING_ROWS = 5
EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256 = (
    "A17010484F8BEFD7CD337CC678E585B43BC0305766C566D1544197B503CB5A28"
)
EXPECTED_DEFERRED_PENDING_OVERRIDE_ROWS = 4
EXPECTED_DEFERRED_PENDING_OVERRIDE_COORDINATE_SHA256 = (
    "237B9D051F481F3EF909BE2C5FABEC565304837E26B382E6B1E8454F02F567B8"
)
EXPECTED_DEFERRED_PENDING_OVERRIDE_MAP_SHA256 = (
    "89FA920C1AD71F747748D71C29AE972FB517C7070F378BB1A8B4757209EB0D16"
)
EXPECTED_DEFERRED_PENDING_KEEP_ROWS = 1
EXPECTED_DEPENDENCY_ROWS = 2
EXPECTED_DEPENDENCY_COORDINATE_SHA256 = (
    "A7E739AEF436B94F5DE6A2BE2FE2BC2C434B9DEB7EA807B33C4D9D3D69A8A15B"
)
EXPECTED_PENDING_ONLY_CANDIDATE_SHA256 = (
    "2B57DECFB4E5D23200E8FCE4FC43BADD74B48B67107D60A49975FB0D3EB24DB3"
)
EXPECTED_PENDING_ONLY_ASSEMBLY_SHA256 = (
    "E64E863D3F6600A70075475EAC18120EA1523A8D2DAEF4AA28D1083767A08B38"
)
EXPECTED_PENDING_ONLY_FAILURE_SHA256 = (
    "6FADD0E16CA0B41F6845C2F26631D7799CBA3C7FAB4805A7AE0577986B128818"
)
EXPECTED_DEFERRED_FULL_ASSEMBLY_SHA256 = (
    "CE69192BC0E9B6CDA44DCC2EB7C3359AB87F4630563723A1CFD62E54D90C5A48"
)

EXPECTED_FULL_OVERRIDE_ROWS = 13
EXPECTED_FULL_OVERRIDE_COORDINATE_SHA256 = (
    "5B20F2EF21BB90064182771EB9092F6C93BAB26173895A6565AC9684E671ECBE"
)
EXPECTED_FULL_OVERRIDE_MAP_SHA256 = (
    "ADCB9D7035C41A520171E8D5E4001054B5DF99A0C2248C99B3770CB220C98FB6"
)
EXPECTED_FULL_CANDIDATE_SHA256 = (
    "1E57A600BE7EC64F2D923816121D16E2444B460527291347322ADCEE48110053"
)
EXPECTED_FULL_ASSEMBLY_SHA256 = (
    "9AB6833E02EDE9572EB4EEF21D8A8D2FF6EB3F241A9DE225E780EA28260BE795"
)
EXPECTED_COMPONENT_MANIFEST_SHA256 = (
    "8458AA4811137FCE3CAFB79731BB36D3F474BD2A6BA1CE64CE5F3494E71A6302"
)

# Frozen after the first independent --write reproduction.
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "9D39B97FDC11037A1B46EFD5F1F743939CAF4F5AD176B0F5299F89DDBEEC1E9A"
)


class ProposalError(ValueError):
    """Raised when the category-B proposal contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProposalError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FAMILY = load_module(
    FAMILY_BUILDER_PATH,
    "pk_bound_terminal_2546_category_b_family_helpers_v1",
)
BASE_AUDIT = FAMILY.BASE_AUDIT
CALLER = FAMILY.CALLER
CROSS = FAMILY.CROSS
ENGINE = FAMILY.ENGINE
HONORIFIC = FAMILY.HONORIFIC
LIVE_STEAM_BASE = FAMILY.LIVE_STEAM_BASE
LIVE_STEAM_PK = FAMILY.LIVE_STEAM_PK


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def exact_map_sha256(value: Mapping[str, str]) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return FAMILY.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return FAMILY.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return FAMILY.record_digest(values)


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 2, f"invalid root coordinate: {value}")
    return parts


def load_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    raw = path.read_bytes()
    require(
        sha256_bytes(raw) == expected_sha256,
        f"JSON digest drifted: {path}",
    )
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    value = json.loads(raw.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_jsonl(path: Path, expected_sha256: str) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    raw = path.read_bytes()
    require(
        sha256_bytes(raw) == expected_sha256,
        f"JSONL digest drifted: {path}",
    )
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        raw.decode("utf-8", errors="strict").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(
            isinstance(value, dict),
            f"{path}:{line_number} is not an object",
        )
        rows.append(value)
    return rows


def load_checkpoint() -> dict[tuple[str, str], dict[str, Any]]:
    rows = load_jsonl(
        CHECKPOINT_PRIVATE_PATH,
        EXPECTED_CHECKPOINT_PRIVATE_SHA256,
    )
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key not in result, f"duplicate checkpoint row: {key}")
        result[key] = row
    require(
        len(result) == EXPECTED_CHECKPOINT_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in result.values()
        )
        == EXPECTED_CHECKPOINT_PENDING,
        "BF7B checkpoint universe drifted",
    )
    return result


def validate_checkpoint_source_free() -> dict[str, Any]:
    report = load_json(
        CHECKPOINT_SOURCE_FREE_PATH,
        EXPECTED_CHECKPOINT_SOURCE_FREE_SHA256,
    )
    layer = (
        report.get("promotions", {})
        .get("pk_msggame", {})
        .get("bound_terminal_2546_full_caller", {})
    )
    require(
        report.get("status") == "PASS"
        and report.get("result", {}).get("private_integrated_decision_sha256")
        == EXPECTED_CHECKPOINT_PRIVATE_SHA256
        and report.get("result", {}).get("runtime_review_pending")
        == EXPECTED_CHECKPOINT_PENDING
        and layer.get("pk_candidate_packed_sha256")
        == EXPECTED_CHECKPOINT_CANDIDATE_SHA256
        and report.get("steam_write_performed") is False,
        "838D checkpoint binding drifted",
    )
    return report


def build_category_sets(
    ledger: Mapping[str, Any],
) -> tuple[
    set[tuple[int, int]],
    set[str],
    set[str],
    dict[tuple[int, int], str],
]:
    reason_by_root = {
        parse_root(str(key)): str(reason)
        for key, reason in ledger.get("bindings", {})
        .get("blocker_reason_by_root", {})
        .items()
    }
    rejected_roots = {
        parse_root(str(value))
        for value in ledger.get("sets", {})
        .get("rejected_pending", {})
        .get("roots", ())
    }
    roots = {
        root
        for root in rejected_roots
        if reason_by_root.get(root) in B_REASONS
    }
    members = ledger.get("bindings", {}).get("root_members", {})
    pending = {
        str(coordinate)
        for root in roots
        for coordinate in members[root_string(root)][
            "rejected_pending_coordinates"
        ]
    }
    preverified = {
        str(coordinate)
        for root in roots
        for coordinate in members[root_string(root)][
            "verified_renewal_coordinates"
        ]
    }
    require(
        len(roots) == EXPECTED_ROOTS
        and record_digest(roots) == EXPECTED_ROOT_SHA256
        and len(pending) == EXPECTED_PENDING_ROWS
        and coordinate_digest(pending)
        == EXPECTED_PENDING_COORDINATE_SHA256
        and len(preverified) == EXPECTED_PREVERIFIED_ROWS
        and coordinate_digest(preverified)
        == EXPECTED_PREVERIFIED_COORDINATE_SHA256,
        "category-B ledger universe drifted",
    )
    return roots, pending, preverified, reason_by_root


def validate_category_handoff(
    *,
    handoff: Mapping[str, Any],
    roots: set[tuple[int, int]],
    pending: set[str],
    preverified: set[str],
    reason_by_root: Mapping[tuple[int, int], str],
) -> dict[str, Any]:
    expected_bindings = {
        "checkpoint_private_sha256": EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        "checkpoint_source_free_sha256":
        EXPECTED_CHECKPOINT_SOURCE_FREE_SHA256,
        "checkpoint_candidate_sha256":
        EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
        "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "handoff_ord000_151_sha256": EXPECTED_HANDOFF_000_151_SHA256,
        "handoff_ord152_303_sha256": EXPECTED_HANDOFF_152_303_SHA256,
        "review_queue_sha256": EXPECTED_REVIEW_QUEUE_SHA256,
    }
    require(
        handoff.get("schema") == PRIVATE_SCHEMA
        and handoff.get("status") == "PASS"
        and handoff.get("release_target") == RELEASE_TARGET
        and handoff.get("resource") == RESOURCE
        and handoff.get("bindings") == expected_bindings
        and handoff.get("shared_integration_modified") is False
        and handoff.get("steam_write_performed") is False
        and handoff.get("privacy", {}).get("public") is False
        and handoff.get("privacy", {}).get("tracked") is False
        and handoff.get("privacy", {}).get("contains_translation_bodies")
        is True
        and all(handoff.get("assertions", {}).values()),
        "private category-B handoff metadata drifted",
    )

    scope = handoff.get("scope", {})
    handoff_roots = {parse_root(str(value)) for value in scope.get("roots", ())}
    handoff_pending = {str(value) for value in scope.get(
        "pending_coordinates",
        (),
    )}
    handoff_preverified = {str(value) for value in scope.get(
        "preexisting_verified_coordinates",
        (),
    )}
    require(
        handoff_roots == roots
        and handoff_pending == pending
        and handoff_preverified == preverified
        and scope.get("root_count") == EXPECTED_ROOTS
        and scope.get("pending_coordinate_count") == EXPECTED_PENDING_ROWS
        and scope.get("selector_coordinate") == "0:1066:0"
        and tuple(scope.get("terminal_coordinates", ()))
        == tuple(
            f"0:{record_id}:0" for record_id in TERMINAL_RECORD_IDS
        ),
        "private handoff scope drifted",
    )

    immediate = handoff.get("immediate_promotion", {})
    deferred = handoff.get("deferred_vm_proof", {})
    immediate_roots = {
        parse_root(str(value)) for value in immediate.get("roots", ())
    }
    deferred_roots = {
        parse_root(str(value)) for value in deferred.get("roots", ())
    }
    immediate_pending = {
        str(value) for value in immediate.get("pending_coordinates", ())
    }
    deferred_pending = {
        str(value) for value in deferred.get("pending_coordinates", ())
    }
    immediate_override = {
        str(value) for value in immediate.get("override_coordinates", ())
    }
    immediate_keep = {
        str(value) for value in immediate.get("keep_coordinates", ())
    }
    deferred_override = {
        str(value)
        for value in deferred.get("pending_override_coordinates", ())
    }
    deferred_keep = {
        str(value)
        for value in deferred.get("pending_keep_coordinates", ())
    }
    dependencies = {
        str(value)
        for value in deferred.get(
            "required_preexisting_verified_dependency_coordinates",
            (),
        )
    }
    require(
        immediate_roots | deferred_roots == roots
        and not (immediate_roots & deferred_roots)
        and immediate_pending | deferred_pending == pending
        and not (immediate_pending & deferred_pending)
        and immediate_override | immediate_keep == immediate_pending
        and not (immediate_override & immediate_keep)
        and deferred_override | deferred_keep == deferred_pending
        and not (deferred_override & deferred_keep)
        and dependencies <= preverified
        and len(immediate_roots) == EXPECTED_IMMEDIATE_ROOTS
        and record_digest(immediate_roots)
        == EXPECTED_IMMEDIATE_ROOT_SHA256
        and len(immediate_pending) == EXPECTED_IMMEDIATE_PENDING_ROWS
        and coordinate_digest(immediate_pending)
        == EXPECTED_IMMEDIATE_PENDING_COORDINATE_SHA256
        and len(immediate_override) == EXPECTED_IMMEDIATE_OVERRIDE_ROWS
        and coordinate_digest(immediate_override)
        == EXPECTED_IMMEDIATE_OVERRIDE_COORDINATE_SHA256
        and len(immediate_keep) == EXPECTED_IMMEDIATE_KEEP_ROWS
        and len(deferred_roots) == EXPECTED_DEFERRED_ROOTS
        and record_digest(deferred_roots)
        == EXPECTED_DEFERRED_ROOT_SHA256
        and len(deferred_pending) == EXPECTED_DEFERRED_PENDING_ROWS
        and coordinate_digest(deferred_pending)
        == EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256
        and len(deferred_override)
        == EXPECTED_DEFERRED_PENDING_OVERRIDE_ROWS
        and coordinate_digest(deferred_override)
        == EXPECTED_DEFERRED_PENDING_OVERRIDE_COORDINATE_SHA256
        and len(deferred_keep) == EXPECTED_DEFERRED_PENDING_KEEP_ROWS
        and len(dependencies) == EXPECTED_DEPENDENCY_ROWS
        and coordinate_digest(dependencies)
        == EXPECTED_DEPENDENCY_COORDINATE_SHA256,
        "private handoff immediate/deferred partition drifted",
    )

    exact = handoff.get("exact_reflow_map")
    require(isinstance(exact, dict), "private exact reflow map is absent")
    exact_map = {str(key): str(value) for key, value in exact.items()}
    immediate_map = {
        coordinate: exact_map[coordinate] for coordinate in immediate_override
    }
    deferred_pending_map = {
        coordinate: exact_map[coordinate] for coordinate in deferred_override
    }
    require(
        set(exact_map) == immediate_override | deferred_override | dependencies
        and len(exact_map) == EXPECTED_FULL_OVERRIDE_ROWS
        and coordinate_digest(exact_map)
        == EXPECTED_FULL_OVERRIDE_COORDINATE_SHA256
        and exact_map_sha256(exact_map) == EXPECTED_FULL_OVERRIDE_MAP_SHA256
        and exact_map_sha256(immediate_map)
        == EXPECTED_IMMEDIATE_OVERRIDE_MAP_SHA256
        and exact_map_sha256(deferred_pending_map)
        == EXPECTED_DEFERRED_PENDING_OVERRIDE_MAP_SHA256
        and all(
            text and not ENGINE.KANA_OR_HAN_RE.search(text)
            for text in exact_map.values()
        ),
        "private exact reflow map drifted",
    )
    expected_handoff_digests = {
        "root_sha256": EXPECTED_ROOT_SHA256,
        "pending_coordinate_sha256":
        EXPECTED_PENDING_COORDINATE_SHA256,
        "preexisting_verified_coordinate_sha256":
        EXPECTED_PREVERIFIED_COORDINATE_SHA256,
        "immediate_root_sha256": EXPECTED_IMMEDIATE_ROOT_SHA256,
        "immediate_pending_coordinate_sha256":
        EXPECTED_IMMEDIATE_PENDING_COORDINATE_SHA256,
        "immediate_override_coordinate_sha256":
        EXPECTED_IMMEDIATE_OVERRIDE_COORDINATE_SHA256,
        "immediate_override_map_sha256":
        EXPECTED_IMMEDIATE_OVERRIDE_MAP_SHA256,
        "deferred_root_sha256": EXPECTED_DEFERRED_ROOT_SHA256,
        "deferred_pending_coordinate_sha256":
        EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256,
        "deferred_pending_override_coordinate_sha256":
        EXPECTED_DEFERRED_PENDING_OVERRIDE_COORDINATE_SHA256,
        "deferred_pending_override_map_sha256":
        EXPECTED_DEFERRED_PENDING_OVERRIDE_MAP_SHA256,
        "dependency_coordinate_sha256":
        EXPECTED_DEPENDENCY_COORDINATE_SHA256,
        "full_override_coordinate_sha256":
        EXPECTED_FULL_OVERRIDE_COORDINATE_SHA256,
        "full_override_map_sha256": EXPECTED_FULL_OVERRIDE_MAP_SHA256,
        "component_manifest_sha256":
        EXPECTED_COMPONENT_MANIFEST_SHA256,
        "immediate_candidate_sha256":
        EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
        "deferred_pending_only_candidate_sha256":
        EXPECTED_PENDING_ONLY_CANDIDATE_SHA256,
        "full_dependency_inclusive_candidate_sha256":
        EXPECTED_FULL_CANDIDATE_SHA256,
        "all_dependency_inclusive_assembly_manifest_sha256":
        EXPECTED_FULL_ASSEMBLY_SHA256,
    }
    precise_reason = deferred.get("precise_reason", {})
    require(
        handoff.get("digests") == expected_handoff_digests
        and immediate.get("proof", {}).get("assembly_manifest_sha256")
        == EXPECTED_IMMEDIATE_ASSEMBLY_SHA256
        and precise_reason.get(
            "pending_only_assembly_manifest_sha256"
        )
        == EXPECTED_PENDING_ONLY_ASSEMBLY_SHA256
        and precise_reason.get(
            "pending_only_failure_manifest_sha256"
        )
        == EXPECTED_PENDING_ONLY_FAILURE_SHA256
        and precise_reason.get(
            "dependency_inclusive_assembly_manifest_sha256"
        )
        == EXPECTED_DEFERRED_FULL_ASSEMBLY_SHA256
        and precise_reason.get("pending_only_register_assembly_fail_count")
        == 13
        and precise_reason.get(
            "additional_vm_closure_and_verified_evidence_renewal_required"
        )
        is True,
        "private handoff digest/rejection proof drifted",
    )

    root_reviews = handoff.get("root_reviews")
    require(
        isinstance(root_reviews, list)
        and len(root_reviews) == EXPECTED_ROOTS,
        "private root review universe drifted",
    )
    reviews_by_root: dict[tuple[int, int], dict[str, Any]] = {}
    for review in root_reviews:
        require(isinstance(review, dict), "root review is not an object")
        root = parse_root(str(review.get("root")))
        require(root not in reviews_by_root, f"duplicate root review: {root}")
        presence = review.get("multilingual_context_present", {})
        require(
            root in roots
            and review.get("blocker_reason") == reason_by_root[root]
            and review.get("jp_semantic_authority") is True
            and review.get("en_sc_tc_context_only") is True
            and all(presence.get(language) is True for language in (
                "jp",
                "en",
                "sc",
                "tc",
            ))
            and all(
                isinstance(review.get(field), str) and review.get(field)
                for field in (
                    "semantic_review",
                    "historical_term_review",
                    "voice_review",
                    "source_record_raw_sha256",
                )
            ),
            f"private multilingual/semantic review drifted: {root}",
        )
        reviews_by_root[root] = dict(review)
    require(
        set(reviews_by_root) == roots,
        "private root review coverage is incomplete",
    )
    return {
        "exact_map": exact_map,
        "immediate_map": immediate_map,
        "deferred_pending_map": deferred_pending_map,
        "immediate_roots": immediate_roots,
        "deferred_roots": deferred_roots,
        "immediate_pending": immediate_pending,
        "deferred_pending": deferred_pending,
        "immediate_override": immediate_override,
        "immediate_keep": immediate_keep,
        "deferred_override": deferred_override,
        "deferred_keep": deferred_keep,
        "dependencies": dependencies,
        "reviews_by_root": reviews_by_root,
    }


def rebuild_candidates(
    *,
    checkpoint: Mapping[tuple[str, str], Mapping[str, Any]],
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    current_blob = BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    checkpoint_replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in checkpoint.items()
        if resource == RESOURCE and isinstance(row.get("translation"), str)
    }

    def rebuild(extra: Mapping[str, str]) -> tuple[bytes, dict[Any, Any]]:
        replacements = dict(checkpoint_replacements)
        replacements.update(
            {
                parse_coordinate(coordinate): text
                for coordinate, text in extra.items()
            }
        )
        blob = BASE_AUDIT.rebuild_packed_with_literals(
            current_blob,
            replacements,
        )
        return blob, BASE_AUDIT.records_from_blob(blob)

    checkpoint_blob, checkpoint_records = rebuild({})
    immediate_blob, immediate_records = rebuild(handoff["immediate_map"])
    pending_only_blob, pending_only_records = rebuild(
        handoff["deferred_pending_map"]
    )
    full_blob, full_records = rebuild(handoff["exact_map"])
    require(
        sha256_bytes(checkpoint_blob)
        == EXPECTED_CHECKPOINT_CANDIDATE_SHA256
        and sha256_bytes(immediate_blob)
        == EXPECTED_IMMEDIATE_CANDIDATE_SHA256
        and sha256_bytes(pending_only_blob)
        == EXPECTED_PENDING_ONLY_CANDIDATE_SHA256
        and sha256_bytes(full_blob) == EXPECTED_FULL_CANDIDATE_SHA256,
        "reconstructed proposal candidate digest drifted",
    )
    HONORIFIC.changed_record_guard(
        predecessor_records=checkpoint_records,
        candidate_records=immediate_records,
        expected_changed=handoff["immediate_roots"],
    )
    HONORIFIC.changed_record_guard(
        predecessor_records=checkpoint_records,
        candidate_records=pending_only_records,
        expected_changed=handoff["deferred_roots"],
    )
    HONORIFIC.changed_record_guard(
        predecessor_records=checkpoint_records,
        candidate_records=full_records,
        expected_changed=(
            handoff["immediate_roots"] | handoff["deferred_roots"]
        ),
    )
    return {
        "current_blob": current_blob,
        "current_records": BASE_AUDIT.records_from_blob(current_blob),
        "checkpoint_blob": checkpoint_blob,
        "checkpoint_records": checkpoint_records,
        "immediate_blob": immediate_blob,
        "immediate_records": immediate_records,
        "pending_only_blob": pending_only_blob,
        "pending_only_records": pending_only_records,
        "full_blob": full_blob,
        "full_records": full_records,
    }


def language_presence(context: Mapping[str, Any]) -> dict[str, bool]:
    result = {"jp": True}
    for language in ("en", "sc", "tc"):
        values = context.get(language.upper(), ())
        result[language] = bool(
            isinstance(values, list)
            and any(isinstance(value, str) and value for value in values)
        )
    return result


def protected_token_signature(value: str) -> dict[str, Any]:
    signature = ENGINE.protected_signature(value)
    return {
        key: signature[key]
        for key in (
            "escape_tags",
            "printf_tokens",
            "bracket_tokens",
            "non_layout_controls",
        )
    }


def load_queue_by_root(
    roots: set[tuple[int, int]],
) -> dict[tuple[int, int], dict[str, Any]]:
    rows = load_jsonl(REVIEW_QUEUE_PATH, EXPECTED_REVIEW_QUEUE_SHA256)
    selected: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        if row.get("resource") != RESOURCE:
            continue
        root = parse_root(str(row["record_coordinate"]))
        if root in roots:
            require(root not in selected, f"duplicate queue root: {root}")
            selected[root] = row
    require(set(selected) == roots, "private review queue coverage drifted")
    return selected


def verify_record_invariants(
    *,
    roots: set[tuple[int, int]],
    records: Mapping[str, Any],
    queue_by_root: Mapping[tuple[int, int], Mapping[str, Any]],
    reviews_by_root: Mapping[tuple[int, int], Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = records["current_records"]
    checkpoint_records = records["checkpoint_records"]
    full_records = records["full_records"]
    component_manifest: list[dict[str, Any]] = []
    review_manifest: list[dict[str, Any]] = []

    for root in sorted(roots):
        versions = (
            source_records[root],
            current_records[root],
            checkpoint_records[root],
            full_records[root],
        )
        components = [
            HONORIFIC.component_signatures(record) for record in versions
        ]
        gaps = [ENGINE.record_gap_bytes(record) for record in versions]
        require(
            components.count(components[0]) == len(components)
            and gaps.count(gaps[0]) == len(gaps),
            f"record control/gap topology drifted: {root}",
        )
        literal_versions = [
            BASE_AUDIT.parse_record_literals(record) for record in versions
        ]
        require(
            len({len(literals) for literals in literal_versions}) == 1,
            f"literal count drifted: {root}",
        )
        for literal_index in range(len(literal_versions[0])):
            current_text = literal_versions[1][literal_index].text
            checkpoint_text = literal_versions[2][literal_index].text
            proposal_text = literal_versions[3][literal_index].text
            require(
                protected_token_signature(current_text)
                == protected_token_signature(checkpoint_text)
                == protected_token_signature(proposal_text)
                and current_text.count("\n")
                == checkpoint_text.count("\n")
                == proposal_text.count("\n"),
                f"protected/newline topology drifted: {root}:{literal_index}",
            )
        component_manifest.append(
            {
                "root": root_string(root),
                "component_sha256": canonical_sha256(components[0]),
                "record_gap_sha256": canonical_sha256(
                    [gap.hex() for gap in gaps[0]]
                ),
            }
        )

        queue = queue_by_root[root]
        review = reviews_by_root[root]
        presence = language_presence(queue["pc_context_literals"])
        require(
            queue.get("source_record_raw_sha256")
            == sha256_bytes(source_records[root].data)
            == review.get("source_record_raw_sha256")
            and all(presence.values()),
            f"multilingual source binding drifted: {root}",
        )
        review_manifest.append(
            {
                "root_sha256": sha256_bytes(
                    (root_string(root) + "\n").encode("ascii")
                ),
                "source_record_raw_sha256":
                queue["source_record_raw_sha256"],
                "blocker_reason": review["blocker_reason"],
                "language_presence": presence,
                "semantic_review_sha256": ENGINE.sha256_text(
                    str(review["semantic_review"])
                ),
                "historical_review_sha256": ENGINE.sha256_text(
                    str(review["historical_term_review"])
                ),
                "voice_review_sha256": ENGINE.sha256_text(
                    str(review["voice_review"])
                ),
            }
        )

    require(
        canonical_sha256(component_manifest)
        == EXPECTED_COMPONENT_MANIFEST_SHA256,
        "component manifest drifted",
    )
    return component_manifest, review_manifest


def linewise_nonexpanding(
    current_widths: Sequence[int],
    proposal_widths: Sequence[int],
) -> bool:
    return (
        len(current_widths) == len(proposal_widths)
        and all(
            proposal <= current
            for current, proposal in zip(current_widths, proposal_widths)
        )
    )


def build_assembly_manifest(
    *,
    proposal_records: Mapping[tuple[int, int], Any],
    current_records: Mapping[tuple[int, int], Any],
    sites_by_root: Mapping[tuple[int, int], str],
    roots: set[tuple[int, int]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    manifest: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    all_deltas: list[int] = []
    for root in sorted(roots):
        site = sites_by_root[root]
        current_left, current_right = CALLER.adjacent_literals(
            current_records,
            site,
        )
        proposal_left, proposal_right = CALLER.adjacent_literals(
            proposal_records,
            site,
        )
        for terminal_record_id in TERMINAL_RECORD_IDS:
            current_ending = BASE_AUDIT.parse_record_literals(
                current_records[(0, terminal_record_id)]
            )[0].text
            proposal_ending = BASE_AUDIT.parse_record_literals(
                proposal_records[(0, terminal_record_id)]
            )[0].text
            current_assembly = (
                current_left + current_ending + current_right
            )
            proposal_assembly = (
                proposal_left + proposal_ending + proposal_right
            )
            current_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(
                current_assembly
            )
            proposal_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(
                proposal_assembly
            )
            nonexpanding = linewise_nonexpanding(
                current_widths,
                proposal_widths,
            )
            deltas = (
                [
                    proposal - current
                    for current, proposal in zip(
                        current_widths,
                        proposal_widths,
                    )
                ]
                if len(current_widths) == len(proposal_widths)
                else []
            )
            all_deltas.extend(deltas)
            require(
                protected_token_signature(current_assembly)
                == protected_token_signature(proposal_assembly),
                f"assembly protected signature drifted: {root}",
            )
            row = {
                "root": root_string(root),
                "terminal_record_id": terminal_record_id,
                "current_assembly_utf16le_sha256":
                ENGINE.sha256_text(current_assembly),
                "proposal_assembly_utf16le_sha256":
                ENGINE.sha256_text(proposal_assembly),
                "current_raw_g1n_widths": list(current_widths),
                "proposal_raw_g1n_widths": list(proposal_widths),
                "width_delta_px": deltas,
                "line_topology_equal":
                len(current_widths) == len(proposal_widths),
                "nonexpanding": nonexpanding,
            }
            manifest.append(row)
            if not nonexpanding:
                failures.append(row)
    return manifest, failures, all_deltas


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
SENSITIVE_KEYS = {
    "translation",
    "translations",
    "exact_reflow_map",
    "exact_map",
    "source_text",
    "current_text",
    "proposal_text",
    "assembly",
    "assemblies",
    "coordinates",
    "roots",
    "site",
    "sites",
}


def assert_source_free_report(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(
                key not in SENSITIVE_KEYS,
                f"tracked report contains a sensitive key: {key}",
            )
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains source or translated text",
        )


def build_outputs() -> tuple[str, dict[str, Any], dict[str, Any]]:
    steam_before = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    checkpoint_source_free = validate_checkpoint_source_free()
    ledger = load_json(LEDGER_PATH, EXPECTED_LEDGER_SHA256)
    load_json(HANDOFF_000_151_PATH, EXPECTED_HANDOFF_000_151_SHA256)
    load_json(HANDOFF_152_303_PATH, EXPECTED_HANDOFF_152_303_SHA256)
    handoff_raw = load_json(
        PRIVATE_HANDOFF_PATH,
        EXPECTED_PRIVATE_HANDOFF_SHA256,
    )
    roots, pending, preverified, reason_by_root = build_category_sets(ledger)
    handoff = validate_category_handoff(
        handoff=handoff_raw,
        roots=roots,
        pending=pending,
        preverified=preverified,
        reason_by_root=reason_by_root,
    )
    checkpoint = load_checkpoint()
    for coordinate in pending:
        require(
            checkpoint[(RESOURCE, coordinate)].get("runtime_review")
            == "pending",
            f"pending checkpoint status drifted: {coordinate}",
        )
    for coordinate in preverified:
        require(
            checkpoint[(RESOURCE, coordinate)].get("runtime_review")
            == "verified",
            f"verified checkpoint status drifted: {coordinate}",
        )
    candidates = rebuild_candidates(
        checkpoint=checkpoint,
        handoff=handoff,
    )
    queue_by_root = load_queue_by_root(roots)
    component_manifest, review_manifest = verify_record_invariants(
        roots=roots,
        records=candidates,
        queue_by_root=queue_by_root,
        reviews_by_root=handoff["reviews_by_root"],
    )

    full_sites = CALLER.call_sites(
        candidates["checkpoint_records"],
        SELECTOR,
    )
    sites_by_root: dict[tuple[int, int], str] = {}
    for root in roots:
        sites = [
            site for site in full_sites if FAMILY.site_root(site) == root
        ]
        require(
            len(sites) == 1,
            f"category-B root must have exactly one selector site: {root}",
        )
        sites_by_root[root] = sites[0]

    immediate_manifest, immediate_failures, immediate_deltas = (
        build_assembly_manifest(
            proposal_records=candidates["immediate_records"],
            current_records=candidates["current_records"],
            sites_by_root=sites_by_root,
            roots=handoff["immediate_roots"],
        )
    )
    pending_manifest, pending_failures, pending_deltas = (
        build_assembly_manifest(
            proposal_records=candidates["pending_only_records"],
            current_records=candidates["current_records"],
            sites_by_root=sites_by_root,
            roots=handoff["deferred_roots"],
        )
    )
    deferred_full_manifest, deferred_full_failures, deferred_full_deltas = (
        build_assembly_manifest(
            proposal_records=candidates["full_records"],
            current_records=candidates["current_records"],
            sites_by_root=sites_by_root,
            roots=handoff["deferred_roots"],
        )
    )
    full_manifest, full_failures, full_deltas = build_assembly_manifest(
        proposal_records=candidates["full_records"],
        current_records=candidates["current_records"],
        sites_by_root=sites_by_root,
        roots=roots,
    )

    failure_counts = Counter(
        parse_root(str(row["root"])) for row in pending_failures
    )
    passing_pending_only = [
        row for row in pending_manifest if row["nonexpanding"]
    ]
    require(
        len(immediate_manifest) == 28
        and not immediate_failures
        and canonical_sha256(immediate_manifest)
        == EXPECTED_IMMEDIATE_ASSEMBLY_SHA256
        and len(pending_manifest) == 14
        and len(pending_failures) == 13
        and canonical_sha256(pending_manifest)
        == EXPECTED_PENDING_ONLY_ASSEMBLY_SHA256
        and canonical_sha256(pending_failures)
        == EXPECTED_PENDING_ONLY_FAILURE_SHA256
        and sorted(failure_counts.values()) == [6, 7]
        and len(passing_pending_only) == 1
        and passing_pending_only[0]["terminal_record_id"] == 2551
        and len(deferred_full_manifest) == 14
        and not deferred_full_failures
        and canonical_sha256(deferred_full_manifest)
        == EXPECTED_DEFERRED_FULL_ASSEMBLY_SHA256
        and len(full_manifest) == 42
        and not full_failures
        and canonical_sha256(full_manifest)
        == EXPECTED_FULL_ASSEMBLY_SHA256
        and immediate_deltas
        and pending_deltas
        and deferred_full_deltas
        and full_deltas,
        "7-register current-relative assembly proof drifted",
    )

    decision_manifest = [
        {
            "coordinate": coordinate,
            "checkpoint_status": str(
                checkpoint[(RESOURCE, coordinate)]["runtime_review"]
            ),
            "decision": (
                "rewrite"
                if coordinate in handoff["exact_map"]
                else "keep"
            ),
            "proposal_translation_utf16le_sha256": ENGINE.sha256_text(
                handoff["exact_map"].get(
                    coordinate,
                    str(checkpoint[(RESOURCE, coordinate)]["translation"]),
                )
            ),
        }
        for coordinate in sorted(
            pending | preverified,
            key=parse_coordinate,
        )
    ]
    reason_counts = Counter(reason_by_root[root] for root in roots)
    report = {
        "schema": PUBLIC_SCHEMA,
        "status": "PASS",
        "release_target": RELEASE_TARGET,
        "resource": "MSG_PK/JP/msggame.bin",
        "method": (
            "private_multilingual_category_b_current_relative_"
            "raw_g1n_reflow_review"
        ),
        "bindings": {
            "checkpoint_private_sha256":
            EXPECTED_CHECKPOINT_PRIVATE_SHA256,
            "checkpoint_source_free_sha256":
            EXPECTED_CHECKPOINT_SOURCE_FREE_SHA256,
            "checkpoint_source_free_payload_reference_sha256":
            checkpoint_source_free.get("result", {}).get(
                "coordinate_universe_sha256"
            ),
            "checkpoint_candidate_sha256":
            EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
            "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
            "handoff_ord000_151_sha256":
            EXPECTED_HANDOFF_000_151_SHA256,
            "handoff_ord152_303_sha256":
            EXPECTED_HANDOFF_152_303_SHA256,
            "review_queue_sha256": EXPECTED_REVIEW_QUEUE_SHA256,
            "category_b_private_handoff_sha256":
            EXPECTED_PRIVATE_HANDOFF_SHA256,
            "immediate_candidate_sha256":
            EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
            "deferred_pending_only_candidate_sha256":
            EXPECTED_PENDING_ONLY_CANDIDATE_SHA256,
            "dependency_inclusive_candidate_sha256":
            EXPECTED_FULL_CANDIDATE_SHA256,
        },
        "scope": {
            "selector": SELECTOR,
            "terminal_registers": len(TERMINAL_RECORD_IDS),
            "category_b_root_count": len(roots),
            "category_b_pending_rows": len(pending),
            "category_b_preexisting_verified_rows": len(preverified),
            "root_sha256": EXPECTED_ROOT_SHA256,
            "pending_coordinate_sha256":
            EXPECTED_PENDING_COORDINATE_SHA256,
            "preexisting_verified_coordinate_sha256":
            EXPECTED_PREVERIFIED_COORDINATE_SHA256,
            "blocker_reason_root_counts": dict(sorted(reason_counts.items())),
        },
        "proposal": {
            "immediate": {
                "root_count": len(handoff["immediate_roots"]),
                "pending_promotion_rows": len(
                    handoff["immediate_pending"]
                ),
                "translation_override_rows": len(
                    handoff["immediate_override"]
                ),
                "translation_keep_rows": len(handoff["immediate_keep"]),
                "preexisting_verified_dependency_rewrite_rows": 0,
                "root_sha256": EXPECTED_IMMEDIATE_ROOT_SHA256,
                "pending_coordinate_sha256":
                EXPECTED_IMMEDIATE_PENDING_COORDINATE_SHA256,
                "override_coordinate_sha256":
                EXPECTED_IMMEDIATE_OVERRIDE_COORDINATE_SHA256,
                "override_map_sha256":
                EXPECTED_IMMEDIATE_OVERRIDE_MAP_SHA256,
                "candidate_sha256": EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
                "potential_pending_after_integration":
                EXPECTED_CHECKPOINT_PENDING
                - EXPECTED_IMMEDIATE_PENDING_ROWS,
                "runtime_promotion_authorized_by_this_proposal": True,
            },
            "deferred": {
                "root_count": len(handoff["deferred_roots"]),
                "pending_rows": len(handoff["deferred_pending"]),
                "pending_translation_override_rows": len(
                    handoff["deferred_override"]
                ),
                "pending_translation_keep_rows": len(
                    handoff["deferred_keep"]
                ),
                "required_preexisting_verified_dependency_rewrite_rows":
                len(handoff["dependencies"]),
                "root_sha256": EXPECTED_DEFERRED_ROOT_SHA256,
                "pending_coordinate_sha256":
                EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256,
                "pending_override_coordinate_sha256":
                EXPECTED_DEFERRED_PENDING_OVERRIDE_COORDINATE_SHA256,
                "dependency_coordinate_sha256":
                EXPECTED_DEPENDENCY_COORDINATE_SHA256,
                "precise_reason_code": (
                    "pending_only_first_line_width_expansion_requires_"
                    "verified_left_dependency_rewrite_and_full_vm_renewal"
                ),
                "pending_only_register_assemblies": len(pending_manifest),
                "pending_only_pass": (
                    len(pending_manifest) - len(pending_failures)
                ),
                "pending_only_fail": len(pending_failures),
                "pending_only_failure_root_count": len(failure_counts),
                "pending_only_assembly_manifest_sha256":
                EXPECTED_PENDING_ONLY_ASSEMBLY_SHA256,
                "pending_only_failure_manifest_sha256":
                EXPECTED_PENDING_ONLY_FAILURE_SHA256,
                "dependency_inclusive_register_assemblies":
                len(deferred_full_manifest),
                "dependency_inclusive_pass": len(
                    deferred_full_manifest
                ),
                "dependency_inclusive_fail": 0,
                "dependency_inclusive_assembly_manifest_sha256":
                EXPECTED_DEFERRED_FULL_ASSEMBLY_SHA256,
                "additional_vm_closure_required": True,
                "verified_evidence_renewal_required": True,
                "runtime_promotion_authorized_by_this_proposal": False,
            },
            "full_private_reflow": {
                "translation_override_rows": len(handoff["exact_map"]),
                "override_coordinate_sha256":
                EXPECTED_FULL_OVERRIDE_COORDINATE_SHA256,
                "override_map_sha256": EXPECTED_FULL_OVERRIDE_MAP_SHA256,
                "candidate_sha256": EXPECTED_FULL_CANDIDATE_SHA256,
            },
        },
        "proof": {
            "immediate_register_assemblies": len(immediate_manifest),
            "immediate_register_assembly_pass": len(immediate_manifest),
            "immediate_register_assembly_fail": 0,
            "immediate_assembly_manifest_sha256":
            EXPECTED_IMMEDIATE_ASSEMBLY_SHA256,
            "all_dependency_inclusive_register_assemblies":
            len(full_manifest),
            "all_dependency_inclusive_register_assembly_pass":
            len(full_manifest),
            "all_dependency_inclusive_register_assembly_fail": 0,
            "all_dependency_inclusive_assembly_manifest_sha256":
            EXPECTED_FULL_ASSEMBLY_SHA256,
            "component_manifest_sha256":
            EXPECTED_COMPONENT_MANIFEST_SHA256,
            "decision_manifest_sha256":
            canonical_sha256(decision_manifest),
            "review_manifest_sha256": canonical_sha256(review_manifest),
            "minimum_immediate_width_delta_px": min(immediate_deltas),
            "maximum_immediate_width_delta_px": max(immediate_deltas),
            "minimum_dependency_inclusive_width_delta_px":
            min(full_deltas),
            "maximum_dependency_inclusive_width_delta_px":
            max(full_deltas),
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_dependency_inclusive_direct_assemblies_nonexpanding":
            True,
            "control_components_preserved": True,
            "record_gap_bytes_preserved": True,
            "protected_token_signatures_preserved": True,
            "newline_topology_preserved": True,
            "absolute_msggame_widget_width_assumed": False,
            "pk_msgev_912px_rule_applied": False,
        },
        "review": {
            "jp_semantic_authority_root_count": len(roots),
            "en_sc_tc_auxiliary_context_root_count": len(roots),
            "all_four_language_context_root_count": len(roots),
            "historical_term_review_root_count": len(roots),
            "character_voice_seven_register_review_root_count":
            len(roots),
            "jp_is_authority": True,
            "en_sc_tc_are_auxiliary_only": True,
        },
        "integration": {
            "proposal_only": True,
            "shared_runtime_vm_integration_modified": False,
            "private_checkpoint_modified": False,
            "immediate_rows_require_separate_checkpoint_integration": True,
            "deferred_rows_require_additional_vm_proof": True,
        },
        "distribution_policy": {
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "steam_write_performed": False,
    }
    report = HONORIFIC.seal_report(report)
    HONORIFIC.validate_seal(report)
    assert_source_free_report(report)
    content = canonical_json(report)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during proposal build",
    )
    return (
        content,
        report,
        {
            "roots": roots,
            "pending": pending,
            "preverified": preverified,
            "reason_by_root": reason_by_root,
            "handoff": handoff,
            "checkpoint": checkpoint,
            "candidates": candidates,
            "component_manifest": component_manifest,
            "review_manifest": review_manifest,
            "decision_manifest": decision_manifest,
            "immediate_manifest": immediate_manifest,
            "pending_manifest": pending_manifest,
            "pending_failures": pending_failures,
            "deferred_full_manifest": deferred_full_manifest,
            "full_manifest": full_manifest,
            "steam_before": steam_before,
            "steam_after": steam_after,
        },
    )


def validate_outputs(
    *,
    content: str,
    report: Mapping[str, Any],
    bundle: Mapping[str, Any],
    require_frozen_hash: bool = True,
) -> None:
    require(
        content == canonical_json(report),
        "public report serialization drifted",
    )
    HONORIFIC.validate_seal(report)
    assert_source_free_report(report)
    if require_frozen_hash:
        require(
            EXPECTED_PUBLIC_OUTPUT_SHA256 is not None
            and sha256_bytes(content.encode("utf-8"))
            == EXPECTED_PUBLIC_OUTPUT_SHA256,
            "frozen public report digest drifted",
        )
    immediate = report["proposal"]["immediate"]
    deferred = report["proposal"]["deferred"]
    require(
        immediate["pending_promotion_rows"]
        == EXPECTED_IMMEDIATE_PENDING_ROWS
        and immediate["runtime_promotion_authorized_by_this_proposal"]
        is True
        and deferred["pending_rows"] == EXPECTED_DEFERRED_PENDING_ROWS
        and deferred["pending_only_fail"] == 13
        and deferred["dependency_inclusive_pass"] == 14
        and deferred["runtime_promotion_authorized_by_this_proposal"]
        is False
        and report["integration"][
            "shared_runtime_vm_integration_modified"
        ]
        is False
        and report.get("steam_write_performed") is False
        and bundle["steam_before"] == bundle["steam_after"],
        "proposal verdict contract drifted",
    )


def validate_output_path(path: Path) -> None:
    require(
        path.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public report must use its fixed tracked source-free path",
    )
    require(
        path.resolve(strict=False)
        not in {
            LIVE_STEAM_BASE.resolve(strict=False),
            LIVE_STEAM_PK.resolve(strict=False),
        },
        "public report may not target live Steam",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_path(args.public_output)
    content, report, bundle = build_outputs()
    validate_outputs(
        content=content,
        report=report,
        bundle=bundle,
        require_frozen_hash=EXPECTED_PUBLIC_OUTPUT_SHA256 is not None,
    )
    if args.write:
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )
    if args.check:
        require(
            args.public_output.is_file(),
            f"public output is absent: {args.public_output}",
        )
        require(
            args.public_output.read_text(encoding="utf-8") == content,
            "public output content drifted",
        )
        require(
            EXPECTED_PUBLIC_OUTPUT_SHA256 is not None,
            "public output digest has not been frozen",
        )
    print(
        "PASS "
        f"immediate_roots={EXPECTED_IMMEDIATE_ROOTS} "
        f"immediate_rows={EXPECTED_IMMEDIATE_PENDING_ROWS} "
        f"deferred_roots={EXPECTED_DEFERRED_ROOTS} "
        f"deferred_rows={EXPECTED_DEFERRED_PENDING_ROWS} "
        "pending_only_failures=13 "
        "shared_integration_write=false "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
