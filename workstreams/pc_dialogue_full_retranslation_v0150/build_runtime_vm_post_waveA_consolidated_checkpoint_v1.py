#!/usr/bin/env python3
"""Apply the frozen WaveA closure as a targeted runtime-ledger checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pc_dialogue_full_retranslation_v0150").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
PREDECESSOR = (
    TMP / "runtime_vm_integrated.post_wave7_local_static_checkpoint.private.v1.jsonl"
)
UNION_BUILDER = (
    AUDIT / "build_pk_msggame_waveA_consolidated_closure_v1.py"
)
UNION_DECISIONS = TMP / "pk_msggame_waveA_union_decisions.private.v1.jsonl"
UNION_EVIDENCE = TMP / "pk_msggame_waveA_union_evidence.private.v1.json"
UNION_CANDIDATE = TMP / "pk_msggame_waveA_union_candidate.private.v1.bin"
UNION_PUBLIC = (
    AUDIT
    / "public"
    / "pk_msggame_waveA_consolidated_closure.source_free.v1.json"
)
ENGINE_BUILDER = DIALOGUE / "build_pc_dialogue_full_retranslation_v0150.py"
SHADOW_CURRENT = (
    TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
DEFAULT_PRIVATE = (
    TMP / "runtime_vm_integrated.post_waveA_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC = (
    DIALOGUE
    / "runtime_vm_integration.post_waveA_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_SHA256 = (
    "502C274DB571359D6C028381F1E77CE70A0AA191CAEC39FD41499044537964ED"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_INPUT_SHA256 = {
    "predecessor": "502C274DB571359D6C028381F1E77CE70A0AA191CAEC39FD41499044537964ED",
    "union_builder": "FD0E8C2C1EC51448219704F94565688D23DF7D3492BCD4914CB9F74554FF7458",
    "union_decisions": "C11954FF36D41141915749A90A8B2DE43A2D0A4ACB747298167114BBF40D3647",
    "union_evidence": "588F618722F4B19E8AB0D6DB833CB15EE1BC0430D0102E55ECFD569E25292C95",
    "union_candidate": "A2811CA8B9A53C84678727737FDA1729520FB4AB16F19AAB537C51292D1EEE78",
    "union_public": "F1FFA1FA8F0764D1ACE1BC0D71BE3676B36C0A36AECE76B4A01CF14B3F5B31C2",
    "engine_builder": "CF32112EB7B0BA578DF9EF2E9D2A5C92818E25AC2217FE867BE7968F92D8372E",
    "shadow_current": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private": "F7B2AA9642E6FDC80920B091991C41F7EC08590E5DE778326EB72E3C8BA67E1A",
    "public": "B8465232576E13BC9D0397775190ED035DFEA203632E4A282DC203A6455939FB",
}


class CheckpointError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


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


def load_decisions() -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with UNION_DECISIONS.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = (str(row["resource"]), str(row["coordinate"]))
            require(key not in rows, f"duplicate union decision: {key}")
            require(
                key[0] == "pk_msggame"
                and (
                    str(row["action"]).endswith("runtime_promotion")
                    or str(row["action"]).endswith("verification_renewal")
                )
                and row.get("runtime_review") == "verified"
                and row.get("semantic_review") == "approved"
                and row.get("layout_review")
                == "current_relative_raw_g1n_nonexpanding"
                and row.get("steam_write_performed") is False,
                f"invalid union decision: {key}",
            )
            rows[key] = row
    require(rows, "empty WaveA union")
    return rows


def patch_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
    union_evidence_sha256: str,
) -> dict[str, Any]:
    coordinate = str(predecessor["coordinate"])
    action = str(decision["action"])
    is_promotion = action.endswith("runtime_promotion")
    is_renewal = action.endswith("verification_renewal")
    require(is_promotion != is_renewal, f"ambiguous action: {coordinate}")
    if is_promotion:
        require(
            predecessor.get("runtime_review") == "pending"
            and predecessor.get("scope_classification")
            == "runtime_fragment_pending",
            f"invalid promotion predecessor: {coordinate}",
        )
    else:
        require(
            predecessor.get("runtime_review") == "verified"
            and predecessor.get("scope_classification") == "retranslated",
            f"invalid renewal predecessor: {coordinate}",
        )
    translation = str(decision["translation"])
    require(
        utf16le_sha256(translation) == decision["translation_utf16le_sha256"],
        f"translation digest drift: {coordinate}",
    )
    changed = dict(predecessor)
    changed["translation"] = translation
    changed["runtime_review"] = "verified"
    changed["scope_classification"] = "retranslated"
    changed["layout_review"] = "current_relative_raw_g1n_nonexpanding"
    changed["post_waveA_update_action"] = action
    changed["post_waveA_exact_review"] = {
        "schema": "nobu16.kr.pk-msggame-waveA-row-verification.v1",
        "method": decision["method"],
        "result": "verified",
        "root": decision["root"],
        "translation_changed": bool(decision["translation_changed"]),
        "per_row_game_playback_required": False,
        "union_evidence_sha256": union_evidence_sha256,
    }
    runtime = dict(decision.get("runtime_vm_verification", {}))
    runtime.update(
        {
            "schema": "nobu16.kr.pk-msggame-waveA-runtime-vm-verification.v1",
            "method": decision["method"],
            "result": "verified",
            "per_row_game_playback_required": False,
            "union_evidence_sha256": union_evidence_sha256,
        }
    )
    changed["runtime_vm_verification"] = runtime
    return changed


def build_outputs() -> tuple[bytes, bytes, dict[str, Any]]:
    inputs = {
        "predecessor": sha256_file(PREDECESSOR),
        "union_builder": sha256_file(UNION_BUILDER),
        "union_decisions": sha256_file(UNION_DECISIONS),
        "union_evidence": sha256_file(UNION_EVIDENCE),
        "union_candidate": sha256_file(UNION_CANDIDATE),
        "union_public": sha256_file(UNION_PUBLIC),
        "engine_builder": sha256_file(ENGINE_BUILDER),
        "shadow_current": sha256_file(SHADOW_CURRENT),
    }
    require(
        inputs == EXPECTED_INPUT_SHA256,
        f"frozen checkpoint input drift: {inputs}",
    )
    evidence = json.loads(UNION_EVIDENCE.read_text(encoding="utf-8"))
    require(evidence.get("status") == "PASS", "union evidence failed")
    decisions = load_decisions()
    evidence_sha256 = inputs["union_evidence"]
    union_candidate_sha256 = inputs["union_candidate"]
    require(
        union_candidate_sha256
        == evidence["digests"]["candidate_after_sha256"],
        "union candidate/evidence drift",
    )

    output_lines: list[bytes] = []
    replacements: dict[tuple[int, int, int], str] = {}
    seen: set[tuple[str, str]] = set()
    before_counts: dict[str, int] = {}
    after_counts: dict[str, int] = {}
    promotion_count = 0
    renewal_count = 0
    affected_roots: set[str] = set()
    row_count = 0
    with PREDECESSOR.open("rb") as handle:
        for raw_line in handle:
            require(raw_line.endswith(b"\n"), "unterminated predecessor line")
            predecessor = json.loads(raw_line)
            row_count += 1
            key = (
                str(predecessor["resource"]),
                str(predecessor["coordinate"]),
            )
            before_key = (
                f"{predecessor.get('runtime_review')}/"
                f"{predecessor.get('scope_classification')}"
            )
            before_counts[before_key] = before_counts.get(before_key, 0) + 1
            decision = decisions.get(key)
            if decision is None:
                row = predecessor
                output_lines.append(raw_line)
            else:
                require(key not in seen, f"duplicate predecessor key: {key}")
                seen.add(key)
                row = patch_row(predecessor, decision, evidence_sha256)
                output_lines.append(canonical_bytes(row) + b"\n")
                promotion_count += str(decision["action"]).endswith(
                    "runtime_promotion"
                )
                renewal_count += str(decision["action"]).endswith(
                    "verification_renewal"
                )
                affected_roots.add(str(decision["root"]))
            if row.get("resource") == "pk_msggame" and "translation" in row:
                replacements[parse_coordinate(str(row["coordinate"]))] = str(
                    row["translation"]
                )
            after_key = (
                f"{row.get('runtime_review')}/"
                f"{row.get('scope_classification')}"
            )
            after_counts[after_key] = after_counts.get(after_key, 0) + 1
    require(row_count == 52_803, "checkpoint row count drift")
    require(seen == set(decisions), "not all union decisions were applied")
    require(
        promotion_count == evidence["counts"]["promoted_coordinates"]
        and renewal_count == evidence["counts"]["renewal_coordinates"],
        "union action count drift",
    )

    ENGINE = load_module(ENGINE_BUILDER, "pk_post_waveA_checkpoint_engine")
    rebuilt_candidate = ENGINE.rebuild_packed_with_literals(
        SHADOW_CURRENT.read_bytes(), replacements
    )
    require(
        rebuilt_candidate == UNION_CANDIDATE.read_bytes(),
        "checkpoint translation map does not rebuild union candidate",
    )
    private = b"".join(output_lines)
    public: dict[str, Any] = {
        "schema": "nobu16.kr.pc-dialogue-runtime-vm-post-waveA-checkpoint.source-free.v1",
        "method": "post_waveA_targeted_promotion_and_verified_dependency_renewal",
        "release_target": "0.15.0",
        "inputs": {
            "predecessor_sha256": inputs["predecessor"],
            "union_builder_sha256": inputs["union_builder"],
            "union_decisions_sha256": inputs["union_decisions"],
            "union_evidence_sha256": evidence_sha256,
            "union_candidate_sha256": union_candidate_sha256,
            "union_public_sha256": inputs["union_public"],
            "engine_builder_sha256": inputs["engine_builder"],
        },
        "result": {
            "row_count": row_count,
            "affected_row_count": len(decisions),
            "promotion_count": promotion_count,
            "verification_renewal_count": renewal_count,
            "affected_root_count": len(affected_roots),
            "pending_before": evidence["counts"]["pending_before"],
            "pending_after": evidence["counts"]["pending_after"],
            "fully_candidate_eligible": row_count
            - evidence["counts"]["pending_after"],
            "private_checkpoint_sha256": sha256_bytes(private),
        },
        "candidate": {
            "before_sha256": EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "after_sha256": union_candidate_sha256,
        },
        "guards": {
            "before_state_counts": dict(sorted(before_counts.items())),
            "after_state_counts": dict(sorted(after_counts.items())),
            "all_decisions_applied_once": True,
            "candidate_rebuilt_from_checkpoint_translation_map": True,
            "unaffected_rows_byte_copied": row_count - len(decisions),
            "full_dialogue_rebuild_performed": False,
            "steam_archives_read_only": True,
        },
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "private_checkpoint_stays_below_tmp": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    return private, (
        json.dumps(public, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii"), public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pins", action="store_true")
    parser.add_argument("--private", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    private, public, report = build_outputs()
    observed = {
        "private": sha256_bytes(private),
        "public": sha256_bytes(public),
    }
    if not args.bootstrap_output_pins:
        require(
            all(EXPECTED_OUTPUT_SHA256.values()),
            "unfrozen checkpoint output pins",
        )
        require(
            observed == EXPECTED_OUTPUT_SHA256,
            f"checkpoint output drift: {observed}",
        )
    if args.write:
        atomic_write(args.private, private)
        atomic_write(args.public, public)
    else:
        require(args.private.read_bytes() == private, "private output drift")
        require(args.public.read_bytes() == public, "public output drift")
    print(
        json.dumps(
            {
                "status": report["status"],
                **report["result"],
                "candidate_sha256": report["candidate"]["after_sha256"],
                "output_sha256": observed,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
