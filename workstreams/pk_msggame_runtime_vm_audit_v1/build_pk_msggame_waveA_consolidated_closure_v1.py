#!/usr/bin/env python3
"""Union independently reviewed WaveA decisions and rebuild the PK candidate.

The dialogue-bearing reviewer artifacts and candidate stay below ``tmp/``.
This tracked verifier rejects overlapping or partial-unit promotions,
verifies every predecessor and translation hash, rebuilds the packed
candidate, and emits a source-free public closure without writing Steam.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pk_msggame_runtime_vm_audit_v1").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
CHECKPOINT = (
    TMP / "runtime_vm_integrated.post_wave7_local_static_checkpoint.private.v1.jsonl"
)
ASSIGNMENT = TMP / "pk_msggame_waveA_exact_assignment.private.v1.json"
PACKETS = tuple(
    TMP / "pk_msggame_waveA_exact_packets" / f"A{index}.private.v1.json"
    for index in range(3)
)
ENGINE_BUILDER = DIALOGUE / "build_pc_dialogue_full_retranslation_v0150.py"
SHADOW_CURRENT = (
    TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
GHIDRA_RECHECK = (
    AUDIT
    / "public"
    / "pk_msggame_ghidra_live_recheck_20260729.source_free.v1.json"
)
DEFAULT_DECISIONS = (
    TMP / "pk_msggame_waveA_union_decisions.private.v1.jsonl"
)
DEFAULT_REPORT = TMP / "pk_msggame_waveA_union_evidence.private.v1.json"
DEFAULT_CANDIDATE = TMP / "pk_msggame_waveA_union_candidate.private.v1.bin"
DEFAULT_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_waveA_consolidated_closure.source_free.v1.json"
)
REVIEW_OVERLAY = TMP / "decisions" / "runtime_verification_overlays"
REVIEW_INPUTS = {
    "a0_builder":
        TMP / "build_pk_msggame_waveA_A0_remediated_review.private.v1.py",
    "a0_decisions":
        REVIEW_OVERLAY
        / "pk_msggame_waveA_A0_remediated_runtime_verified_decisions.private.v1.jsonl",
    "a0_evidence":
        TMP / "pk_msggame_waveA_A0_remediated_review_evidence.private.v1.json",
    "a0_public":
        TMP / "pk_msggame_waveA_A0_remediated_review.source_free.v1.json",
    "a1_initial_builder":
        TMP / "build_pk_msggame_waveA_A1_review.private.v1.py",
    "a1_initial_decisions":
        REVIEW_OVERLAY
        / "pk_msggame_waveA_A1_runtime_verified_decisions.private.v1.jsonl",
    "a1_initial_evidence":
        TMP / "pk_msggame_waveA_A1_review_evidence.private.v1.json",
    "a1_initial_public":
        TMP / "pk_msggame_waveA_A1_review.source_free.v1.json",
    "a1_remediation_builder":
        TMP / "build_pk_msggame_waveA_A1_width_remediation.private.v1.py",
    "a1_remediation_proposals":
        TMP / "pk_msggame_waveA_A1_width_remediation_proposals.private.v1.json",
    "a1_remediation_decisions":
        REVIEW_OVERLAY
        / "pk_msggame_waveA_A1_width_remediation_runtime_verified_decisions.private.v1.jsonl",
    "a1_remediation_evidence":
        TMP / "pk_msggame_waveA_A1_width_remediation_evidence.private.v1.json",
    "a1_remediation_public":
        TMP / "pk_msggame_waveA_A1_width_remediation.source_free.v1.json",
    "a2_initial_builder":
        TMP / "build_pk_msggame_waveA_A2_review.private.v1.py",
    "a2_initial_decisions":
        REVIEW_OVERLAY / "pk_msggame_waveA_A2_decisions.private.v1.jsonl",
    "a2_initial_evidence":
        TMP / "pk_msggame_waveA_A2_evidence.private.v1.json",
    "a2_remediation_builder":
        TMP / "build_pk_msggame_waveA_A2_width_remediation.private.v1.py",
    "a2_remediation_proposals":
        TMP / "pk_msggame_waveA_A2_width_remediation_proposals.private.v1.jsonl",
    "a2_remediation_decisions":
        REVIEW_OVERLAY
        / "pk_msggame_waveA_A2_width_remediation_decisions.private.v1.jsonl",
    "a2_remediation_evidence":
        TMP / "pk_msggame_waveA_A2_width_remediation_evidence.private.v1.json",
    "a2_remediation_public":
        TMP / "pk_msggame_waveA_A2_width_remediation.source_free.v1.json",
}
DEFAULT_DECISION_PATHS = (
    REVIEW_INPUTS["a0_decisions"],
    REVIEW_INPUTS["a1_initial_decisions"],
    REVIEW_INPUTS["a1_remediation_decisions"],
    REVIEW_INPUTS["a2_initial_decisions"],
    REVIEW_INPUTS["a2_remediation_decisions"],
)
EXPECTED_REVIEW_INPUT_SHA256 = {
    "a0_builder": "6B322FECD3F77177B560C43398421BA14F1AAA27A55FF858AAF31B28BF58B041",
    "a0_decisions": "A8F28D61C219902B5307FCD61EC75A9B77B2C164B99ED3DC151446BCD9DB65FE",
    "a0_evidence": "4A15C85C3881EC50DCF48EE2E154EE15D9A373FB1C901AC9CD691E6624D1EDC0",
    "a0_public": "DA63ECB2B2620BCC855033FB2E0B0D23306195A1757D049D80AE64CE5D8EA214",
    "a1_initial_builder": "04D2C7E887A1B0775D8484D0B2250ADAB07F62EB6F09B7EAE34DFEF0A55E92F0",
    "a1_initial_decisions": "4386DB744DA9F0F4E71B641CB1AF9E09A9E58FA32DAF9565E42A9B9B85FB4440",
    "a1_initial_evidence": "91A423A5C882565D19B62B7F9027D71312E48BE190520CA88C05D9D6A8FCCE11",
    "a1_initial_public": "C7BC6D53E0673FF5CE06E795BEA2A4F264738405F35D4005DFF6CE885D9708C1",
    "a1_remediation_builder": "E30681AEB01011C61CE05F19581E30634F700A93DFB9368C64E85163058A1C1E",
    "a1_remediation_proposals": "9A22A4ECC328D32F68F322497EA02060BF862C1000265A1000BA19D7FC0857EA",
    "a1_remediation_decisions": "4F00ACFBB33EFDE226FB078032B13E92ADF9BBC9C59A523C5E6587750DF015F7",
    "a1_remediation_evidence": "14A90B49D6427C04FB0B755C00E43A4EB9421A3665AEBC193DEA2813F18760C7",
    "a1_remediation_public": "1AE6593D532C2F7AE22A65B1A7C3AAAE3A3E0D746F49740AF1C062257FBDAD08",
    "a2_initial_builder": "E8A2E642633174EBD2C6BBDA14F020F82C8CA5FA523989D464C9F1578DC564BB",
    "a2_initial_decisions": "735E8D05DA8A8455CF7EDA09F2B2F672FFA9B6D5E18E504C83C89EADE00344CB",
    "a2_initial_evidence": "6B1293C673E025CC0F1F634131AC16615BE69939D1F6B572FC205157CB460FA6",
    "a2_remediation_builder": "68B50A66B8512E88441E73D2EAB24623B92EB03AA63620F6654FE26FBCEE8115",
    "a2_remediation_proposals": "FBFC49B7E8AEACE64514B9A98DCC04DA985AB3989977BBD0C139F919C2655B4C",
    "a2_remediation_decisions": "A29D47D38B4033D087E70F1CEE700A8DC16D38DAF2EB924918583F7C57E4BC4B",
    "a2_remediation_evidence": "292C7FD5436CDA9935423F1CFD0956D56573FDB7FA4D0367C9DDECC069D419F4",
    "a2_remediation_public": "65EE6E4DAC13CAF748CE953562CCDC1B1ECFFCD391C1D4C3F01424D0E503B2D8",
}
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "decisions": "C11954FF36D41141915749A90A8B2DE43A2D0A4ACB747298167114BBF40D3647",
    "evidence": "588F618722F4B19E8AB0D6DB833CB15EE1BC0430D0102E55ECFD569E25292C95",
    "candidate": "A2811CA8B9A53C84678727737FDA1729520FB4AB16F19AAB537C51292D1EEE78",
    "public": "F1FFA1FA8F0764D1ACE1BC0D71BE3676B36C0A36AECE76B4A01CF14B3F5B31C2",
}

EXPECTED_INPUT_SHA256 = {
    "checkpoint": "502C274DB571359D6C028381F1E77CE70A0AA191CAEC39FD41499044537964ED",
    "assignment": "352BA44152920A269D092237DA70F5278FADB295D3AEB4B8F52BD8B7DA78448F",
    "packet0": "E45B355C4606E8BA56E34CFD89D48668E5ACF25889C4562B44388F7FA69AB4A2",
    "packet1": "EE59AF760C9940C259A27B0813A7777B2B63A7E9DDE3C18F2DDF53EA6DAB41B7",
    "packet2": "EB87B46196D03354E7E6B22658F929D9CF7CD961FDC5A76ACAD29A1C09924823",
    "engine_builder": "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "shadow_current": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "ghidra_recheck": "938CEF5DFA0DADD21B48650C2CFFCCA09300A735706AA3131498D531B2EAC386",
}
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_WAVEA_COORDINATES = 3_433
EXPECTED_WAVEA_ROOTS = 2_542


class UnionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


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


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    result = tuple(map(int, value.split(":")))
    require(len(result) == 3, f"invalid coordinate: {value}")
    return result


def parse_root(value: str) -> tuple[int, int]:
    result = tuple(map(int, value.split(":")))
    require(len(result) == 2, f"invalid root: {value}")
    return result


def digest_lines(values: Iterable[str], parser: Any) -> str:
    return sha256_bytes(
        "".join(f"{value}\n" for value in sorted(set(values), key=parser)).encode(
            "ascii"
        )
    )


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            require(
                isinstance(value, dict),
                f"non-object JSONL row: {path}:{line_number}",
            )
            rows.append(value)
    return rows


def build_outputs(
    decision_paths: Sequence[Path],
    *,
    require_complete_packets: bool,
) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    inputs = {
        "checkpoint": sha256_file(CHECKPOINT),
        "assignment": sha256_file(ASSIGNMENT),
        "packet0": sha256_file(PACKETS[0]),
        "packet1": sha256_file(PACKETS[1]),
        "packet2": sha256_file(PACKETS[2]),
        "engine_builder": sha256_file(ENGINE_BUILDER),
        "shadow_current": sha256_file(SHADOW_CURRENT),
        "ghidra_recheck": sha256_file(GHIDRA_RECHECK),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"frozen input drift: {inputs}")
    review_inputs = {
        name: sha256_file(path) for name, path in REVIEW_INPUTS.items()
    }
    require(
        review_inputs == EXPECTED_REVIEW_INPUT_SHA256,
        f"review input drift: {review_inputs}",
    )
    require(decision_paths, "at least one decision file is required")
    require(
        len(set(map(Path.resolve, decision_paths))) == len(decision_paths),
        "duplicate decision path",
    )

    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    require(
        assignment["result"]["waveA_coordinate_count"]
        == EXPECTED_WAVEA_COORDINATES
        and assignment["result"]["waveA_root_count"] == EXPECTED_WAVEA_ROOTS,
        "assignment scope drift",
    )
    packets = [
        json.loads(path.read_text(encoding="utf-8")) for path in PACKETS
    ]
    coordinate_to_packet: dict[str, int] = {}
    root_to_packet: dict[str, int] = {}
    units: list[tuple[int, int, frozenset[str], frozenset[str]]] = []
    owned_roots: set[str] = set()
    for packet_id, packet in enumerate(packets):
        require(packet["packet_id"] == packet_id, "packet id drift")
        for unit in packet["units"]:
            coordinates = frozenset(map(str, unit["coordinates"]))
            roots = frozenset(map(str, unit["roots"]))
            require(coordinates and roots, "empty WaveA unit")
            units.append(
                (packet_id, int(unit["unit_id"]), coordinates, roots)
            )
            for coordinate in coordinates:
                require(
                    coordinate not in coordinate_to_packet,
                    f"assignment coordinate overlap: {coordinate}",
                )
                coordinate_to_packet[coordinate] = packet_id
            require(not owned_roots & roots, "assignment root overlap")
            owned_roots.update(roots)
            for root in roots:
                root_to_packet[root] = packet_id
    require(
        len(coordinate_to_packet) == EXPECTED_WAVEA_COORDINATES
        and len(owned_roots) == EXPECTED_WAVEA_ROOTS,
        "packet union drift",
    )

    checkpoint_rows: dict[str, dict[str, Any]] = {}
    checkpoint_raw_line_sha256: dict[str, str] = {}
    replacements: dict[tuple[int, int, int], str] = {}
    checkpoint_row_count = 0
    pending_count = 0
    with CHECKPOINT.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            checkpoint_row_count += 1
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            coordinate = str(row["coordinate"])
            checkpoint_rows[coordinate] = row
            checkpoint_raw_line_sha256[coordinate] = sha256_bytes(
                line.encode("utf-8")
            )
            if "translation" in row:
                replacements[parse_coordinate(coordinate)] = str(
                    row["translation"]
                )
            pending_count += row.get("runtime_review") == "pending"
    require(checkpoint_row_count == 52_803, "checkpoint row count drift")
    require(pending_count == 4_647, "checkpoint pending count drift")

    ENGINE = load_module(ENGINE_BUILDER, "pk_waveA_union_dialogue_engine")
    current_blob = SHADOW_CURRENT.read_bytes()
    predecessor_candidate = ENGINE.rebuild_packed_with_literals(
        current_blob, replacements
    )
    require(
        sha256_bytes(predecessor_candidate)
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
        "predecessor candidate drift",
    )

    accepted: dict[str, dict[str, Any]] = {}
    promotions: dict[str, dict[str, Any]] = {}
    renewals: dict[str, dict[str, Any]] = {}
    accepted_source: dict[str, str] = {}
    file_rows: list[dict[str, Any]] = []
    blocked_rows = 0
    for path in decision_paths:
        require(path.is_file(), f"missing decision file: {path}")
        for row in load_jsonl(path):
            coordinate = str(row.get("coordinate", ""))
            action = str(row.get("action", ""))
            require(
                row.get("resource") == "pk_msggame",
                f"non-PK decision: {path}:{coordinate}",
            )
            coordinate_root = ":".join(coordinate.split(":")[:2])
            is_owned_pending = coordinate in coordinate_to_packet
            is_owned_renewal = (
                not is_owned_pending and coordinate_root in root_to_packet
            )
            require(
                is_owned_pending or is_owned_renewal,
                f"non-WaveA root coordinate: {path}:{coordinate}",
            )
            if action == "blocked":
                require(
                    is_owned_pending,
                    f"blocked nonpending coordinate: {coordinate}",
                )
                blocked_rows += 1
                continue
            if is_owned_pending:
                require(
                    action.endswith("runtime_promotion"),
                    f"unauthorized promotion action: {path}:{coordinate}:{action}",
                )
            else:
                require(
                    action.endswith("verification_renewal"),
                    f"unauthorized renewal action: {path}:{coordinate}:{action}",
                )
            require(
                coordinate not in accepted,
                f"accepted coordinate overlap: {coordinate}",
            )
            predecessor = checkpoint_rows[coordinate]
            if is_owned_pending:
                require(
                    predecessor.get("runtime_review") == "pending"
                    and predecessor.get("scope_classification")
                    == "runtime_fragment_pending"
                    and predecessor.get("semantic_review") == "approved",
                    f"invalid pending predecessor state: {coordinate}",
                )
            else:
                require(
                    predecessor.get("runtime_review") == "verified"
                    and predecessor.get("scope_classification") == "retranslated"
                    and predecessor.get("semantic_review") == "approved",
                    f"invalid renewal predecessor state: {coordinate}",
                )
            require(
                row.get("predecessor_row_sha256")
                in {
                    canonical_sha256(predecessor),
                    checkpoint_raw_line_sha256[coordinate],
                },
                f"predecessor digest drift: {coordinate}",
            )
            translation_value = row.get("translation")
            if translation_value is None:
                require(
                    row.get("translation_changed") is False,
                    f"missing override translation: {coordinate}",
                )
                translation = str(predecessor["translation"])
                row = dict(row)
                row["translation"] = translation
            else:
                translation = str(translation_value)
            require(
                (
                    row.get("translation_utf16le_sha256")
                    or row.get("after_translation_utf16le_sha256")
                )
                == utf16le_sha256(translation),
                f"translation digest drift: {coordinate}",
            )
            row = dict(row)
            row["translation_utf16le_sha256"] = utf16le_sha256(translation)
            require(
                row.get("runtime_review") == "verified"
                and row.get("semantic_review") == "approved"
                and row.get("layout_review")
                == "current_relative_raw_g1n_nonexpanding"
                and row.get("steam_write_performed") is False,
                f"review contract failed: {coordinate}",
            )
            accepted[coordinate] = row
            if is_owned_pending:
                promotions[coordinate] = row
            else:
                renewals[coordinate] = row
            accepted_source[coordinate] = str(path)
            file_rows.append(
                {
                    "path": str(path.resolve().relative_to(REPO)).replace("\\", "/"),
                    "sha256": sha256_file(path),
                }
            )

    accepted_coordinates = set(promotions)
    partial_units: list[str] = []
    promoted_units = 0
    for packet_id, unit_id, coordinates, _roots in units:
        overlap = accepted_coordinates & coordinates
        if overlap:
            if overlap != coordinates:
                partial_units.append(f"A{packet_id}:{unit_id}")
            else:
                promoted_units += 1
    require(not partial_units, f"partial-unit promotions: {partial_units[:20]}")
    if require_complete_packets:
        covered_packets = {
            coordinate_to_packet[coordinate]
            for coordinate in accepted_coordinates
        }
        require(
            covered_packets == {0, 1, 2},
            f"not all packets have accepted output: {covered_packets}",
        )

    override_coordinates: set[str] = set()
    for coordinate, row in accepted.items():
        translation = str(row["translation"])
        predecessor_translation = str(checkpoint_rows[coordinate]["translation"])
        translation_changed = translation != predecessor_translation
        require(
            bool(row.get("translation_changed")) == translation_changed,
            f"translation_changed flag drift: {coordinate}",
        )
        if translation_changed:
            expected_action = (
                "translation_override_and_runtime_promotion"
                if coordinate in promotions
                else "translation_override_and_verification_renewal"
            )
            require(
                row["action"] == expected_action,
                f"override action drift: {coordinate}",
            )
            replacements[parse_coordinate(coordinate)] = translation
            override_coordinates.add(coordinate)
        else:
            expected_action = (
                "runtime_promotion"
                if coordinate in promotions
                else "verification_renewal"
            )
            require(
                row["action"] == expected_action,
                f"keep action drift: {coordinate}",
            )

    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    candidate_sha256 = sha256_bytes(candidate)
    decisions = b"".join(
        canonical_bytes(accepted[coordinate]) + b"\n"
        for coordinate in sorted(accepted, key=parse_coordinate)
    )
    promotion_root_strings = {
        ":".join(coordinate.split(":")[:2]) for coordinate in promotions
    }
    renewal_root_strings = {
        ":".join(coordinate.split(":")[:2]) for coordinate in renewals
    }
    report: dict[str, Any] = {
        "schema": "nobu16.kr.pk-msggame-waveA-union-evidence.private.v1",
        "method": "three_packet_root_atomic_review_union_and_candidate_rebuild",
        "inputs": {
            **inputs,
            "review_artifact_sha256": review_inputs,
            "decision_files": sorted(
                {
                    (
                        str(path.resolve().relative_to(REPO)).replace("\\", "/"),
                        sha256_file(path),
                    )
                    for path in decision_paths
                }
            ),
        },
        "counts": {
            "accepted_coordinates": len(accepted),
            "accepted_roots": len(
                promotion_root_strings | renewal_root_strings
            ),
            "promoted_coordinates": len(promotions),
            "promoted_roots": len(promotion_root_strings),
            "renewal_coordinates": len(renewals),
            "renewal_roots": len(renewal_root_strings),
            "promoted_units": promoted_units,
            "translation_overrides": len(override_coordinates),
            "classification_only_promotions":
                len(accepted) - len(override_coordinates),
            "observed_block_rows": blocked_rows,
            "pending_before": pending_count,
            "pending_after": pending_count - len(promotions),
        },
        "digests": {
            "accepted_coordinate_sha256":
                digest_lines(accepted, parse_coordinate),
            "accepted_root_sha256": digest_lines(
                promotion_root_strings | renewal_root_strings, parse_root
            ),
            "promotion_coordinate_sha256":
                digest_lines(promotions, parse_coordinate),
            "promotion_root_sha256":
                digest_lines(promotion_root_strings, parse_root),
            "renewal_coordinate_sha256":
                digest_lines(renewals, parse_coordinate),
            "renewal_root_sha256":
                digest_lines(renewal_root_strings, parse_root),
            "override_coordinate_sha256":
                digest_lines(override_coordinates, parse_coordinate),
            "decision_payload_sha256": sha256_bytes(decisions),
            "candidate_before_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "candidate_after_sha256": candidate_sha256,
        },
        "proof": {
            "all_predecessor_rows_bound": True,
            "all_translation_hashes_bound": True,
            "accepted_coordinate_overlap_count": 0,
            "partial_unit_promotion_count": 0,
            "root_atomic": True,
            "source_only_action_count": 0,
            "full_integration_rebuild_performed": False,
            "steam_write_performed": False,
        },
        "status": "PASS",
    }
    return decisions, json.dumps(
        report, ensure_ascii=True, indent=2, sort_keys=True
    ).encode("ascii") + b"\n", candidate, report


def assert_source_free(value: Any, path: str = "$") -> None:
    forbidden_keys = {
        "translation",
        "translations",
        "source_text",
        "current_text",
        "candidate_text",
        "dialogue",
        "japanese",
        "korean",
    }
    cjk = re.compile(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
    )
    if isinstance(value, dict):
        for key, child in value.items():
            require(
                str(key) not in forbidden_keys,
                f"source-bearing public key: {path}.{key}",
            )
            assert_source_free(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_source_free(child, f"{path}[{index}]")
    elif isinstance(value, str):
        require(cjk.search(value) is None, f"CJK leaked into public output: {path}")


def build_public(report: Mapping[str, Any]) -> dict[str, Any]:
    public: dict[str, Any] = {
        "schema": "nobu16.kr.pk-msggame-waveA-consolidated-closure.source-free.v1",
        "method": report["method"],
        "release_target": "0.15.0",
        "inputs": {
            "checkpoint_sha256": report["inputs"]["checkpoint"],
            "assignment_sha256": report["inputs"]["assignment"],
            "packet_sha256": [
                report["inputs"]["packet0"],
                report["inputs"]["packet1"],
                report["inputs"]["packet2"],
            ],
            "engine_builder_sha256": report["inputs"]["engine_builder"],
            "ghidra_recheck_sha256": report["inputs"]["ghidra_recheck"],
            "review_artifact_sha256":
                report["inputs"]["review_artifact_sha256"],
        },
        "result": report["counts"],
        "digests": report["digests"],
        "proof": {
            **report["proof"],
            "all_actual_selector_and_terminal_branches_rechecked": True,
            "current_relative_raw_g1n_nonexpansion_required": True,
            "en_sc_tc_used_as_auxiliary_context_only": True,
            "jp_used_as_semantic_authority": True,
            "historical_factuality_and_speaker_register_reviewed": True,
            "pk_msgev_912px_rule_applied": False,
        },
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "private_review_artifacts_stay_below_tmp": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(public)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pins", action="store_true")
    parser.add_argument(
        "--decision",
        action="append",
        type=Path,
        dest="decisions",
    )
    parser.add_argument("--decisions-output", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    decision_paths = tuple(args.decisions or DEFAULT_DECISION_PATHS)
    require(
        tuple(path.resolve() for path in decision_paths)
        == tuple(path.resolve() for path in DEFAULT_DECISION_PATHS),
        "official WaveA decision path/order drift",
    )
    decisions, report, candidate, value = build_outputs(
        decision_paths,
        require_complete_packets=True,
    )
    public = (
        json.dumps(
            build_public(value),
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")
    outputs = {
        "decisions": (args.decisions_output, decisions),
        "evidence": (args.report_output, report),
        "candidate": (args.candidate_output, candidate),
        "public": (args.public_output, public),
    }
    observed = {
        name: sha256_bytes(payload)
        for name, (_path, payload) in outputs.items()
    }
    if not args.bootstrap_output_pins:
        require(
            all(EXPECTED_OUTPUT_SHA256.values()),
            "unfrozen WaveA output pins",
        )
        require(
            observed == EXPECTED_OUTPUT_SHA256,
            f"WaveA output drift: {observed}",
        )
    if args.write:
        for path, payload in outputs.values():
            atomic_write(path, payload)
    else:
        for path, payload in outputs.values():
            require(path.is_file(), f"missing output: {path}")
            require(path.read_bytes() == payload, f"output drift: {path}")
    print(
        json.dumps(
            {
                "status": value["status"],
                **value["counts"],
                "candidate_sha256": value["digests"]["candidate_after_sha256"],
                "decisions_sha256": value["digests"]["decision_payload_sha256"],
                "output_sha256": observed,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
