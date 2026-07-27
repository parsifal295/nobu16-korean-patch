#!/usr/bin/env python3
"""Build the guarded PK 6:3421 standalone-localization semantic override.

The pristine JP record delegates its sentence ending to record 0:1066, while
all three official PC localizations and the current Korean record intentionally
flatten the sentence into one self-contained literal.  Restoring the JP call
would duplicate or corrupt the localized ending.  This builder therefore
keeps the localized VM shape, replaces only the incomplete Korean literal,
and emits a source-free tracked adjudication plus a private decision overlay.
It has no Steam write path.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
PK_AUDIT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_msggame_runtime_vm_audit_v1.py"
)
GHIDRA_CONTRACT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "ghidra_pk_vm_contract.v1.json"
)
SOURCE_DECISION_PATH = (
    OUTPUT_ROOT
    / "decisions"
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
CHOICE_PATH = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_msggame_3421_semantic_choice.private.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_msggame_3421_semantic_override.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "pk_semantic_flattening_3421.source_free.v1.json"
)

REPORT_SCHEMA = "nobu16.kr.pk-msggame-semantic-flattening-3421.v1"
OVERLAY_SCHEMA = (
    "nobu16.kr.pk-msggame-semantic-flattening-decision-overlay-row.v1"
)
CHOICE_SCHEMA = "nobu16.kr.pk-msggame-semantic-choice.v1.private"
COORDINATE = "6:3421:0"
RECORD = (6, 3421)
JP_TERMINAL_TARGET = (0, 1066)
EXPECTED_SOURCE_DECISION_FILE_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_SOURCE_DECISION_ROW_SHA256 = (
    "487B06C7B2F2A04594545382241D3598B3E3B667CBA3A70B97FD8AC428594DBC"
)
EXPECTED_CHOICE_FILE_SHA256 = (
    "2052679105547810645EE679270A0EAD304DF311EEA60B91A9E808F974C44829"
)
EXPECTED_TRANSLATION_SHA256 = (
    "66F99F0C1332F5EC207F9563D78B0B843FBE6827FD1352565C1B68E6194D5B36"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "063FE464ADFF1B684E6A20AC54EBAC04AF75513CF8AE92B54176ABB356F853D8"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "4EE00E2439FBCCB33C3020749AA7C4DF208C42F6688026DF7BAC4808ED8E5B2A"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "4199077CDE9E45540B0CD27408F3BCF20BFC3FCA4F2E27E69EDF195DBEDE1C62"
)


class SemanticOverrideError(ValueError):
    """Raised when the localized-flattening proof or private choice drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SemanticOverrideError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("pk_semantic_flattening_engine", ENGINE_PATH)
PK_AUDIT = load_module("pk_semantic_flattening_vm_audit", PK_AUDIT_PATH)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            row,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required private input is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} is not an object")
    return value


def source_row() -> dict[str, Any]:
    require(
        SOURCE_DECISION_PATH.is_file()
        and sha256_bytes(SOURCE_DECISION_PATH.read_bytes())
        == EXPECTED_SOURCE_DECISION_FILE_SHA256,
        "source decision segment drifted",
    )
    matches: list[dict[str, Any]] = []
    for line in SOURCE_DECISION_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("coordinate") == COORDINATE:
            matches.append(row)
    require(len(matches) == 1, "source decision row is absent or duplicated")
    require(
        canonical_sha256(matches[0]) == EXPECTED_SOURCE_DECISION_ROW_SHA256,
        "source decision row drifted",
    )
    return matches[0]


def direct_edges(record: Any) -> tuple[tuple[str, tuple[int, int]], ...]:
    return tuple(
        (str(component["kind"]), tuple(component["target"]))
        for component in PK_AUDIT.decode_record(record)
        if component["kind"] in {"call", "jump"}
    )


def gap_manifest(record: Any) -> dict[str, Any]:
    gaps = ENGINE.record_gap_bytes(record)
    return {
        "gap_count": len(gaps),
        "gap_sha256": canonical_sha256(
            [sha256_bytes(gap) for gap in gaps]
        ),
        "direct_edges": [
            {"kind": kind, "target": list(target)}
            for kind, target in direct_edges(record)
        ],
    }


def relative_line_widths(value: str) -> list[int]:
    widths: list[int] = []
    for line in value.split("\n"):
        width = 0
        for character in line:
            require(
                unicodedata.category(character) != "Cc",
                "semantic choice contains an embedded control character",
            )
            width += (
                48
                if unicodedata.east_asian_width(character) in {"W", "F", "A"}
                else 24
            )
        widths.append(width)
    return widths


def build_outputs() -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    choice_raw = CHOICE_PATH.read_bytes()
    require(
        sha256_bytes(choice_raw) == EXPECTED_CHOICE_FILE_SHA256,
        "private semantic choice drifted",
    )
    choice = load_json(CHOICE_PATH)
    require(
        choice.get("schema") == CHOICE_SCHEMA
        and choice.get("resource") == "pk_msggame"
        and choice.get("coordinate") == COORDINATE
        and choice.get("semantic_review") == "approved"
        and choice.get("manual_multilingual_context_review") is True
        and choice.get("speaker_register_review") is True
        and choice.get("historical_term_review") is True
        and choice.get("standalone_literal_flattening") is True
        and choice.get("historic_korean_used") is False
        and choice.get("switch_korean_used") is False,
        "private semantic choice metadata drifted",
    )
    translation = choice.get("translation")
    require(
        isinstance(translation, str)
        and ENGINE.sha256_text(translation) == EXPECTED_TRANSLATION_SHA256,
        "private semantic choice translation drifted",
    )
    original = source_row()
    prepared = ENGINE.prepare_artifacts(
        PK_AUDIT.SHADOW_STEAM_ROOT,
        PK_AUDIT.DEFAULT_BASE_PRISTINE,
        PK_AUDIT.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources["pk_msggame"]
    source_record = ENGINE.archive_records(resource.pristine_archive)[RECORD]
    current_record = ENGINE.archive_records(resource.current_archive)[RECORD]
    source_literals = ENGINE.parse_record_literals(source_record)
    current_literals = ENGINE.parse_record_literals(current_record)
    require(
        sha256_bytes(source_record.data) == EXPECTED_SOURCE_RECORD_SHA256
        and sha256_bytes(current_record.data) == EXPECTED_CURRENT_RECORD_SHA256
        and len(source_literals) == len(current_literals) == 1
        and ENGINE.sha256_text(current_literals[0].text)
        == EXPECTED_CURRENT_LITERAL_SHA256,
        "JP/current 6:3421 input binding drifted",
    )
    source_gap = gap_manifest(source_record)
    current_gap = gap_manifest(current_record)
    require(
        source_gap["direct_edges"] == [
            {"kind": "call", "target": list(JP_TERMINAL_TARGET)}
        ]
        and current_gap["direct_edges"] == [],
        "JP/current localization control shape drifted",
    )
    context_manifest: dict[str, Any] = {}
    for language in ("EN", "SC", "TC"):
        record = ENGINE.archive_records(
            resource.context_archives[language]
        )[RECORD]
        literals = ENGINE.parse_record_literals(record)
        manifest = gap_manifest(record)
        require(
            len(literals) == 1 and manifest["direct_edges"] == [],
            f"{language} no-call localization shape drifted",
        )
        context_manifest[language] = {
            "record_sha256": sha256_bytes(record.data),
            "literal_utf16le_sha256": ENGINE.sha256_text(literals[0].text),
            **manifest,
        }
    contract_raw = GHIDRA_CONTRACT_PATH.read_bytes()
    contract = json.loads(contract_raw)
    require(
        contract.get("opcode_contract", {}).get("02", {}).get(
            "automatic_space_inserted"
        )
        is False
        and contract.get("opcode_contract", {}).get("02", {}).get(
            "automatic_punctuation_inserted"
        )
        is False
        and contract.get("pk_message_route_proof", {}).get("conclusion"),
        "Ghidra PK msggame contract drifted",
    )
    current_widths = relative_line_widths(current_literals[0].text)
    target_widths = relative_line_widths(translation)
    require(
        len(current_widths) == len(target_widths) == 2
        and all(
            target <= current
            for current, target in zip(current_widths, target_widths)
        ),
        "standalone semantic choice expands the current line envelope",
    )
    override = copy.deepcopy(original)
    override.pop("base_exact_reuse_prefill", None)
    override["translation"] = translation
    override["basis"] = (
        "pristine PC JP meaning and official PC EN/SC/TC standalone "
        "localization structure; Ghidra-proved no-call flattening; manually "
        "reviewed Korean completion"
    )
    override["layout_review"] = "unchanged_from_current"
    override["runtime_review"] = "not_required"
    override["scope_classification"] = "retranslated"
    override["semantic_flattening_verification"] = {
        "schema": OVERLAY_SCHEMA,
        "adjudication": "repair_not_required",
        "localization_strategy": "standalone_literal_flattening",
        "translation_utf16le_sha256": EXPECTED_TRANSLATION_SHA256,
        "source_decision_row_sha256": EXPECTED_SOURCE_DECISION_ROW_SHA256,
        "choice_file_sha256": EXPECTED_CHOICE_FILE_SHA256,
        "ghidra_contract_sha256": sha256_bytes(contract_raw),
        "source_record_sha256": EXPECTED_SOURCE_RECORD_SHA256,
        "current_record_sha256": EXPECTED_CURRENT_RECORD_SHA256,
        "source_gap_manifest_sha256": canonical_sha256(source_gap),
        "current_gap_manifest_sha256": canonical_sha256(current_gap),
        "official_pc_context_manifest_sha256": canonical_sha256(
            context_manifest
        ),
        "current_line_widths_raw_g1n_px": current_widths,
        "target_line_widths_raw_g1n_px": target_widths,
        "relative_line_envelope_nonexpanding": True,
        "repair_candidate_application_forbidden": True,
    }
    private_content = canonical_jsonl([override])
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    report = {
        "schema": REPORT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "pk_msggame",
        "coordinate": COORDINATE,
        "input_binding": {
            "source_decision_file_sha256":
            EXPECTED_SOURCE_DECISION_FILE_SHA256,
            "source_decision_row_sha256":
            EXPECTED_SOURCE_DECISION_ROW_SHA256,
            "choice_file_sha256": EXPECTED_CHOICE_FILE_SHA256,
            "choice_translation_utf16le_sha256":
            EXPECTED_TRANSLATION_SHA256,
            "pk_pristine_packed_sha256": resource.file_hashes[
                "pristine_jp"
            ],
            "pk_current_packed_sha256": resource.file_hashes["current_ko"],
            "ghidra_contract_sha256": sha256_bytes(contract_raw),
        },
        "localization_evidence": {
            "jp_direct_call_target": list(JP_TERMINAL_TARGET),
            "current_direct_call_count": 0,
            "official_pc_localization_direct_call_counts": {
                language: len(value["direct_edges"])
                for language, value in context_manifest.items()
            },
            "source_gap_manifest_sha256": canonical_sha256(source_gap),
            "current_gap_manifest_sha256": canonical_sha256(current_gap),
            "official_pc_context_manifest_sha256": canonical_sha256(
                context_manifest
            ),
            "automatic_space_inserted": False,
            "automatic_punctuation_inserted": False,
        },
        "adjudication": {
            "repair_status": "repair_not_required",
            "localization_strategy": "standalone_literal_flattening",
            "repair_candidate_application_forbidden": True,
            "semantic_override_rows": 1,
            "private_override_sha256": private_sha256,
        },
        "layout_evidence": {
            "line_count_preserved": True,
            "current_line_widths_raw_g1n_px": current_widths,
            "target_line_widths_raw_g1n_px": target_widths,
            "relative_line_envelope_nonexpanding": True,
            "absolute_msggame_widget_width_assumed": False,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_override_stays_below_tmp": True,
        },
        "steam_write_performed": False,
    }
    unsealed = copy.deepcopy(report)
    report["report_payload_sha256"] = canonical_sha256(unsealed)
    public_content = canonical_json(report)
    return private_content, public_content, report, override


def validate_outputs(
    private_content: str,
    public_content: str,
    report: Mapping[str, Any],
    override: Mapping[str, Any],
) -> None:
    require(
        report.get("schema") == REPORT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False,
        "semantic override report metadata drifted",
    )
    unsealed = copy.deepcopy(dict(report))
    expected_payload = unsealed.pop("report_payload_sha256", None)
    require(
        expected_payload == canonical_sha256(unsealed),
        "semantic override report payload drifted",
    )
    require(
        private_content == canonical_jsonl([override])
        and public_content == canonical_json(report),
        "semantic override serialization drifted",
    )
    evidence = override.get("semantic_flattening_verification")
    require(
        override.get("coordinate") == COORDINATE
        and isinstance(override.get("translation"), str)
        and ENGINE.sha256_text(override["translation"])
        == EXPECTED_TRANSLATION_SHA256
        and isinstance(evidence, dict)
        and evidence.get("translation_utf16le_sha256")
        == EXPECTED_TRANSLATION_SHA256
        and evidence.get("repair_candidate_application_forbidden")
        is True
        and report.get("adjudication", {}).get(
            "private_override_sha256"
        )
        == sha256_bytes(private_content.encode("utf-8")),
        "semantic override row binding drifted",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    first = build_outputs()
    second = build_outputs()
    require(first[:3] == second[:3], "two-run semantic override drifted")
    validate_outputs(*first)
    private_content, public_content, report, _override = first
    if args.write:
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private semantic override drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "tracked semantic override report drifted",
        )
    print(
        "PASS "
        f"coordinate={COORDINATE} "
        "repair=not_required "
        "semantic_override=1 "
        f"steam_write={str(report['steam_write_performed']).lower()}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        SemanticOverrideError,
        ENGINE.RetranslationError,
        PK_AUDIT.AuditError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
