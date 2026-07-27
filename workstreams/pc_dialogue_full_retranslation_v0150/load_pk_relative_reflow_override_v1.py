#!/usr/bin/env python3
"""Load and bind the private PK relative-reflow override without dialogue leaks."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PRIVATE_PATH = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "layout_overrides"
    / "pk_msggame_residual_a_relative_reflow.private.v1.jsonl"
)
PUBLIC_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_residual_a_relative_reflow.v1.json"
)

REPORT_SCHEMA = "nobu16.kr.pk-msggame-residual-a-relative-reflow.v1"
ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-residual-a-relative-reflow-override-row.v1"
)
EXPECTED_ROWS = 26
EXPECTED_ROOT_ROWS = 39
EXPECTED_BEFORE_CANDIDATE_SHA256 = (
    "2A7A5CE6235B8D2BC1EC725F879AFB52CE264F7AB0678E9B6637AED0C98BE707"
)
EXPECTED_AFTER_CANDIDATE_SHA256 = (
    "C18AED979C9F81B99E898FD18C7CD4F2415737223F6FF7D329A69983ECF5BB1F"
)
EXPECTED_PRIVATE_SHA256 = (
    "2E195A308AC1CEE5859D28C58F1F3E3DEEA7B8A2E5F692CE2B24C2DBCDBBBE76"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "E0FC03945EA080A33BD7ACC71F8114279DB385D085F6A63A31974E77B9E0B0EE"
)
EXPECTED_OVERRIDE_MANIFEST_SHA256 = (
    "1C809ACF49B5DEF55F54FC781513C8C190BC91A766C3EBF4D86138B3C5296368"
)


class RelativeReflowContractError(ValueError):
    """Raised when the private override or its source-free binding drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RelativeReflowContractError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    require(
        len(parts) == 3 and all(part.isdigit() for part in parts),
        f"invalid reflow coordinate: {value}",
    )
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def coordinate_digest(coordinates: Sequence[str]) -> str:
    payload = "".join(
        f"{coordinate}\n"
        for coordinate in sorted(set(coordinates), key=parse_coordinate)
    )
    return sha256_bytes(payload.encode("ascii"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"private reflow override is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
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


def load_report() -> tuple[dict[str, Any], str]:
    require(PUBLIC_PATH.is_file(), f"reflow report is absent: {PUBLIC_PATH}")
    raw = PUBLIC_PATH.read_bytes()
    report = json.loads(raw.decode("utf-8"))
    require(
        isinstance(report, dict)
        and report.get("schema") == REPORT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False,
        "reflow report schema/status drifted",
    )
    unsealed = copy.deepcopy(report)
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "reflow report guards are absent")
    payload_sha256 = guards.pop("report_payload_sha256", None)
    require(
        payload_sha256 == canonical_sha256(unsealed),
        "reflow report payload hash drifted",
    )
    require(
        report.get("scope", {}).get("private_override_rows")
        == EXPECTED_ROWS
        and report.get("scope", {}).get("exact_nonnewline_safe_root_rows")
        == EXPECTED_ROOT_ROWS
        and report.get("candidate_binding", {}).get(
            "before_full_candidate_packed_sha256"
        )
        == EXPECTED_BEFORE_CANDIDATE_SHA256
        and report.get("candidate_binding", {}).get(
            "after_reflow_candidate_packed_sha256"
        )
        == EXPECTED_AFTER_CANDIDATE_SHA256
        and report.get("candidate_binding", {}).get(
            "reflow_override_manifest_sha256"
        )
        == EXPECTED_OVERRIDE_MANIFEST_SHA256
        and report.get("result", {}).get("private_override_file_sha256")
        == EXPECTED_PRIVATE_SHA256
        and report.get("result", {}).get(
            "runtime_review_transition_performed"
        )
        is False
        and report.get("result", {}).get(
            "layout_review_transition_performed"
        )
        is False
        and report.get("layout_contract", {}).get(
            "absolute_msggame_widget_width_assumed"
        )
        is False
        and report.get("layout_contract", {}).get(
            "pk_msgev_912px_rule_applied"
        )
        is False,
        "reflow report contract drifted",
    )
    return report, sha256_bytes(raw)


def load_overrides(
    source_rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    report, report_file_sha256 = load_report()
    private_raw = PRIVATE_PATH.read_bytes()
    require(
        sha256_bytes(private_raw) == EXPECTED_PRIVATE_SHA256,
        "private reflow override file hash drifted",
    )
    rows = read_jsonl(PRIVATE_PATH)
    require(len(rows) == EXPECTED_ROWS, "private reflow row count drifted")
    source_by_coordinate = {
        str(row["coordinate"]): dict(row)
        for row in source_rows
        if row.get("resource") == "pk_msggame"
    }
    require(
        len(source_by_coordinate) == len(source_rows),
        "reflow source universe contains duplicates or non-PK rows",
    )

    overrides: dict[str, dict[str, Any]] = {}
    manifest: list[dict[str, Any]] = []
    adjudications = report.get("row_adjudications")
    require(isinstance(adjudications, dict), "reflow adjudications are absent")
    for row in rows:
        coordinate = str(row.get("coordinate"))
        parse_coordinate(coordinate)
        require(
            coordinate not in overrides
            and row.get("schema") == ROW_SCHEMA
            and row.get("resource") == "pk_msggame"
            and row.get("runtime_review_transition_performed") is False
            and row.get("layout_review_transition_performed") is False
            and row.get("steam_write_performed") is False,
            f"invalid private reflow row: {coordinate}",
        )
        source = source_by_coordinate.get(coordinate)
        require(source is not None, f"reflow source row is absent: {coordinate}")
        translation = row.get("translation")
        source_translation = source.get("translation")
        source_binding = row.get("source_decision_binding")
        contract = row.get("exact_nonnewline_contract")
        candidate_binding = row.get("candidate_binding")
        adjudication = adjudications.get(coordinate)
        require(
            isinstance(translation, str)
            and isinstance(source_translation, str)
            and isinstance(source_binding, dict)
            and isinstance(contract, dict)
            and isinstance(candidate_binding, dict)
            and isinstance(adjudication, dict),
            f"incomplete private reflow row: {coordinate}",
        )
        before_hash = sha256_text(source_translation)
        after_hash = sha256_text(translation)
        nonnewline_hash = sha256_text(translation.replace("\n", ""))
        require(
            source_binding.get("decision_canonical_sha256")
            == canonical_sha256(source)
            and source_binding.get("before_translation_utf16le_sha256")
            == before_hash
            and adjudication.get("before_translation_utf16le_sha256")
            == before_hash
            and adjudication.get("after_translation_utf16le_sha256")
            == after_hash
            and adjudication.get("nonnewline_utf16le_sha256")
            == nonnewline_hash
            and contract.get("nonnewline_utf16le_sha256")
            == nonnewline_hash
            and source_translation.replace("\n", "")
            == translation.replace("\n", "")
            and source_translation.count("\n") == translation.count("\n")
            and contract.get("all_after_lines_nonexpanding") is True
            and contract.get("absolute_msggame_widget_width_assumed")
            is False
            and contract.get("pk_msgev_912px_rule_applied") is False
            and candidate_binding.get(
                "before_full_candidate_packed_sha256"
            )
            == EXPECTED_BEFORE_CANDIDATE_SHA256
            and candidate_binding.get(
                "after_reflow_candidate_packed_sha256"
            )
            == EXPECTED_AFTER_CANDIDATE_SHA256,
            f"private reflow binding drifted: {coordinate}",
        )
        effective = dict(source)
        effective["translation"] = translation
        overrides[coordinate] = effective
        manifest.append(
            {
                "coordinate": coordinate,
                "before_translation_utf16le_sha256": before_hash,
                "after_translation_utf16le_sha256": after_hash,
                "nonnewline_utf16le_sha256": nonnewline_hash,
            }
        )

    ordered_coordinates = sorted(overrides, key=parse_coordinate)
    require(
        coordinate_digest(ordered_coordinates)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and canonical_sha256(
            sorted(manifest, key=lambda item: parse_coordinate(item["coordinate"]))
        )
        == EXPECTED_OVERRIDE_MANIFEST_SHA256,
        "private reflow override universe drifted",
    )
    return overrides, {
        "override_count": len(overrides),
        "private_file_sha256": EXPECTED_PRIVATE_SHA256,
        "public_file_sha256": report_file_sha256,
        "report_payload_sha256": report["guards"]["report_payload_sha256"],
        "before_candidate_packed_sha256": EXPECTED_BEFORE_CANDIDATE_SHA256,
        "after_candidate_packed_sha256": EXPECTED_AFTER_CANDIDATE_SHA256,
        "override_manifest_sha256": EXPECTED_OVERRIDE_MANIFEST_SHA256,
        "override_coordinate_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "runtime_review_transition_performed": False,
        "layout_review_transition_performed": False,
        "steam_write_performed": False,
    }
